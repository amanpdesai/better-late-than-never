"""
SUPABASE DATA UPLOADER
======================

This script uploads scraped data to Supabase database.

Usage:
    python upload_to_supabase.py --input output/USA/2025-10-25.json
    python upload_to_supabase.py --category memes --country USA
    python upload_to_supabase.py --all  # Upload all pending data
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials not found in environment variables")
    logger.warning("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file")


class SupabaseUploader:
    """Handles uploading data to Supabase."""

    def __init__(self):
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self.supabase = None

    def get_or_create_country(self, country_name: str) -> str:
        """Get country ID or create if doesn't exist."""
        if not self.supabase:
            return None

        try:
            # Try to get existing country
            result = self.supabase.table('countries').select('id').eq('name', country_name).execute()

            if result.data:
                return result.data[0]['id']

            # Create new country
            # TODO: Add proper flag emoji, lat/lon, country code
            country_data = {
                'name': country_name,
                'code': country_name[:2].upper(),  # Placeholder
                'flag_emoji': '🌍',  # Placeholder
                'latitude': 0.0,
                'longitude': 0.0
            }

            result = self.supabase.table('countries').insert(country_data).execute()
            logger.info(f"Created new country: {country_name}")
            return result.data[0]['id']

        except Exception as e:
            logger.error(f"Error getting/creating country {country_name}: {e}")
            return None

    def upload_category_data(self, country_name: str, category: str, data: Dict[str, Any]) -> bool:
        """Upload category data to Supabase."""
        if not self.supabase:
            logger.warning("Supabase not connected. Skipping upload.")
            return False

        try:
            # Get or create country
            country_id = self.get_or_create_country(country_name)
            if not country_id:
                return False

            # Prepare data
            category_data = {
                'country_id': country_id,
                'category': category.lower(),
                'data': data,  # JSONB field
                'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
                'last_updated': datetime.utcnow().isoformat()
            }

            # Upload to category_data table
            result = self.supabase.table('category_data').insert(category_data).execute()
            logger.info(f"Uploaded {category} data for {country_name}")

            # Upload mood metrics if available
            if 'mood_metrics' in data:
                self.upload_mood_metrics(country_id, category, data['mood_metrics'])

            # Upload trending topics if available
            if 'trending_topics' in data:
                self.upload_trending_topics(country_id, category, data['trending_topics'])

            # Upload individual items if available
            if 'items' in data:
                self.upload_content_items(result.data[0]['id'], data['items'])

            return True

        except Exception as e:
            logger.error(f"Error uploading data for {country_name}/{category}: {e}")
            return False

    def upload_mood_metrics(self, country_id: str, category: str, mood_data: Dict[str, float]):
        """Upload mood metrics."""
        try:
            mood_record = {
                'country_id': country_id,
                'category': category,
                'timestamp': datetime.utcnow().isoformat(),
                **mood_data
            }
            self.supabase.table('mood_metrics').insert(mood_record).execute()
            logger.info(f"Uploaded mood metrics for {category}")
        except Exception as e:
            logger.error(f"Error uploading mood metrics: {e}")

    def upload_trending_topics(self, country_id: str, category: str, topics: List[Dict[str, Any]]):
        """Upload trending topics."""
        try:
            for topic in topics:
                topic_record = {
                    'country_id': country_id,
                    'category': category,
                    'topic': topic.get('keyword') or topic.get('topic'),
                    'volume': topic.get('volume', 0),
                    'sentiment': topic.get('sentiment', 'neutral'),
                    'trend': topic.get('trend', 'stable'),
                    'timestamp': datetime.utcnow().isoformat()
                }
                self.supabase.table('trending_topics').insert(topic_record).execute()
            logger.info(f"Uploaded {len(topics)} trending topics")
        except Exception as e:
            logger.error(f"Error uploading trending topics: {e}")

    def upload_content_items(self, category_data_id: str, items: List[Dict[str, Any]]):
        """Upload individual content items."""
        try:
            for item in items[:50]:  # Limit to top 50 items
                content_record = {
                    'category_data_id': category_data_id,
                    'item_id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'content': item.get('content') or item.get('excerpt', ''),
                    'source_platform': item.get('source_platform') or item.get('platform', ''),
                    'source_url': item.get('source_url') or item.get('url', ''),
                    'engagement_data': {
                        'likes': item.get('engagement', {}).get('likes', 0),
                        'comments': item.get('engagement', {}).get('comments', 0),
                        'shares': item.get('engagement', {}).get('shares', 0),
                        'views': item.get('engagement', {}).get('views', 0)
                    },
                    'sentiment': item.get('sentiment', 'neutral'),
                    'virality_score': item.get('virality_score', 0)
                }
                self.supabase.table('content_items').insert(content_record).execute()
            logger.info(f"Uploaded {len(items[:50])} content items")
        except Exception as e:
            logger.error(f"Error uploading content items: {e}")

    def upload_from_file(self, file_path: Path) -> bool:
        """Upload data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            country = data.get('country')
            category = data.get('category')

            if not country or not category:
                logger.error(f"Missing country or category in {file_path}")
                return False

            return self.upload_category_data(country, category, data)

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Upload scraped data to Supabase')
    parser.add_argument('--input', type=str, help='Input JSON file path')
    parser.add_argument('--category', type=str, help='Category to upload')
    parser.add_argument('--country', type=str, help='Country to upload')
    parser.add_argument('--all', action='store_true', help='Upload all pending data')

    args = parser.parse_args()

    uploader = SupabaseUploader()

    if args.input:
        # Upload specific file
        file_path = Path(args.input)
        if file_path.exists():
            uploader.upload_from_file(file_path)
        else:
            logger.error(f"File not found: {file_path}")

    elif args.category and args.country:
        # Upload latest data for category/country
        output_dir = Path(f"{args.category}/output/{args.country}")
        if output_dir.exists():
            # Find latest file
            files = sorted(output_dir.glob("*.json"), reverse=True)
            if files:
                uploader.upload_from_file(files[0])
            else:
                logger.warning(f"No files found in {output_dir}")
        else:
            logger.error(f"Directory not found: {output_dir}")

    elif args.all:
        # Upload all pending data
        logger.info("Uploading all pending data...")
        for category_dir in Path('.').glob('*/output'):
            category = category_dir.parent.name
            for country_dir in category_dir.glob('*'):
                if country_dir.is_dir():
                    country = country_dir.name
                    files = sorted(country_dir.glob("*.json"), reverse=True)
                    if files:
                        logger.info(f"Uploading {category}/{country}")
                        uploader.upload_from_file(files[0])
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
