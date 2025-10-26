// Type definitions based on the actual scraped data structure

export type Sentiment = "positive" | "negative" | "neutral"
export type MoodKey = "joy" | "curiosity" | "anger" | "confusion" | "sadness"
export type ContentType = "video" | "reddit" | "news" | "twitter" | "article"
export type Category = "All" | "Memes" | "News" | "Politics" | "Economics" | "Sports"

// Base engagement metrics
export interface EngagementMetrics {
  likes?: number
  comments?: number
  shares?: number
  views?: number
  upvotes?: number
}

// Common content item structure
export interface ContentItem {
  id: string
  title: string
  excerpt?: string
  content?: string
  source_platform: string
  source_name?: string
  source_url?: string
  created_at?: string
  timestamp?: string
  engagement: EngagementMetrics
  sentiment: Sentiment
  virality_score: number
  type?: ContentType
  thumbnail?: string
  author?: string
  upvotes?: number
  comments?: number
  views?: number
  source?: string
  tags?: string[]
  is_video?: boolean
  sport?: string // For sports content: NFL, NBA, MLB, etc.
  media?: {
    thumbnail?: string
    images?: string[]
    videos?: string[]
  }
}

// Memes data structure
export interface MemesData {
  country: string
  category: "memes"
  timestamp: string
  items: ContentItem[]
  summary: {
    total_memes: number
    platform_breakdown: Record<string, number>
    sentiment_breakdown: Record<Sentiment, number>
    top_subreddits?: Array<{ name: string; count: number }>
    top_channels?: Array<{ name: string; count: number }>
    video_count?: number
    image_count?: number
  }
}

// Google Trends data structure
export interface GoogleTrendsData {
  country: string
  timestamp: string
  trending_searches: Array<{
    query: string
    traffic_label: string
    category: string
    related_queries: string[]
    share_url: string
  }>
  breakout_searches?: Array<{
    query: string
    growth?: string
  }>
  summary?: {
    total_trending_searches: number
    total_breakout_searches: number
    top_category: string
    notable_topics: string[]
  }
}

// News data structure
export interface NewsData {
  country: string
  category: "news"
  timestamp: string
  items: ContentItem[]
  summary: {
    total_stories: number
    overall_sentiment: string
    news_by_source: Record<string, number>
    top_topics?: string[]
    avg_virality_score?: number
  }
}

// Politics data structure
export interface PoliticsData {
  country: string
  category: "politics"
  timestamp: string
  leadership_and_government: {
    legislature?: string
    president?: string
    prime_minister?: string
    head_of_state?: string
  }
  recent_and_upcoming: {
    recent_policies: Array<{
      title: string
      source: string
      published_at: string
      url?: string
    }>
  }
  political_climate: {
    key_issues: string[]
    controversies: string[]
    recent_headlines: Array<{
      headline: string
      source: string
      published: string
      url?: string
      sentiment?: string
    }>
  }
}

// Economics data structure
export interface EconomicsData {
  country: string
  category: "economics"
  timestamp: string
  economic_indicators: {
    gdp_growth?: {
      value: number
      year: string
      trend: string
    }
    inflation_rate?: {
      value: number
      trend: string
    }
    unemployment_rate?: {
      value: number
      trend: string
    }
    stock_index?: {
      name: string
      value: number
      trend: string
    }
  }
  market_data: {
    top_gainers: Array<{
      symbol: string
      name: string
      price: number
      change_pct: number
    }>
    top_losers?: Array<{
      symbol: string
      name: string
      price: number
      change_pct: number
    }>
  }
  news_headlines?: Array<{
    title: string
    source: string
    published_at: string
    url?: string
  }>
}

// Sports data structure
export interface SportsData {
  country: string
  category: "sports"
  timestamp: string
  items: ContentItem[]
  summary?: {
    total_stories: number
    sports_breakdown?: Record<string, number>
    sentiment_breakdown?: Record<Sentiment, number>
  }
}

// Entertainment data structure (similar to memes/news)
export interface EntertainmentData {
  country: string
  category: "entertainment"
  timestamp: string
  items: ContentItem[]
  summary?: {
    total_items: number
    platform_breakdown?: Record<string, number>
    sentiment_breakdown?: Record<Sentiment, number>
  }
}

// Technology data structure (similar to news)
export interface TechnologyData {
  country: string
  category: "technology"
  timestamp: string
  items: ContentItem[]
  summary?: {
    total_items: number
    platform_breakdown?: Record<string, number>
    sentiment_breakdown?: Record<Sentiment, number>
  }
}

// Aggregated country data for display
export interface CountryData {
  name: string
  flag: string
  lastUpdated: string
  moodSummary: string
  moodMeter: Record<MoodKey, number>
  sentimentTrend: number[]
  topTopics: Array<{
    keyword: string
    sentiment: Sentiment
    volume: number
  }>
  representativeContent: ContentItem[]
  categoryMetrics: {
    totalPosts: number
    avgEngagement: number
    viralityScore: number
  }
  platformBreakdown: Array<{
    platform: string
    percentage: number
  }>
  engagementStats: {
    likes: number
    shares: number
    comments: number
  }
  categoryBreakdown?: Array<{
    category: Category
    count: number
    sentiment: string
  }>
  categoryData?: PoliticsData | EconomicsData | MemesData | NewsData | SportsData
}

// Country metadata
export interface CountryMetadata {
  name: string
  code: string // USA, UK, Canada, India, Australia
  flag: string
  availableCategories: Category[]
  lastUpdated: string
}
