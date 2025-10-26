# Frontend Integration Plan

## Overview

This document outlines how to integrate the scraped data with the existing 3D globe visualization frontend in [earth-3d](../earth-3d).

## Current Frontend Structure

The frontend currently uses:
- **Component**: [CountryInfoPanel](../earth-3d/components/country-info-panel.tsx)
- **Categories**: Memes, Economics, Politics, Sports, Entertainment, Technology
- **Mock Data**: Currently using placeholder/mock data

## Integration Steps

### 1. Update TypeScript Interfaces

Update the `CountryData` interface in [country-info-panel.tsx](../earth-3d/components/country-info-panel.tsx:11-59) to match our new data schema:

```typescript
// New type definitions to add
type Category = "Memes" | "Economics" | "Politics" | "Sports" | "News" | "YouTube" | "Google Trends"

interface CountryData {
  name: string
  flag: string
  lastUpdated: string
  moodSummary: string
  moodMeter: {
    joy: number
    curiosity: number
    anger: number
    confusion: number
    sadness: number
  }
  sentimentTrend: number[]
  topTopics: Array<{
    keyword: string
    sentiment: "positive" | "negative" | "neutral"
    volume: number
  }>
  representativeContent: Array<{
    id: string
    title: string
    excerpt: string
    engagement: number
    platform: string
    sentiment: "positive" | "negative" | "neutral"
    type: "video" | "reddit" | "news" | "twitter" | "article" | "meme" | "short"
    url?: string
    timestamp?: string
    thumbnail?: string
    author?: string
    upvotes?: number
    comments?: number
    views?: number
    source?: string
  }>
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
}
```

### 2. Create Supabase Client

Create a new file: `earth-3d/lib/supabase.ts`

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseKey)

// Type definitions for database tables
export type CategoryDataRow = {
  id: string
  country_id: string
  category: string
  data: any // JSONB field
  timestamp: string
  last_updated: string
}

export type CountryRow = {
  id: string
  name: string
  code: string
  flag_emoji: string
  latitude: number
  longitude: number
}
```

### 3. Create API Functions

Create: `earth-3d/lib/api/country-data.ts`

```typescript
import { supabase } from '../supabase'
import type { CountryData } from '@/components/country-info-panel'

export async function getCountryData(
  countryName: string,
  category: string
): Promise<CountryData | null> {
  try {
    // Fetch country
    const { data: country, error: countryError } = await supabase
      .from('countries')
      .select('*')
      .eq('name', countryName)
      .single()

    if (countryError) throw countryError

    // Fetch latest category data
    const { data: categoryData, error: categoryError } = await supabase
      .from('category_data')
      .select('*')
      .eq('country_id', country.id)
      .eq('category', category.toLowerCase())
      .order('timestamp', { ascending: false })
      .limit(1)
      .single()

    if (categoryError) throw categoryError

    // Transform database data to CountryData format
    return transformToCountryData(country, categoryData)
  } catch (error) {
    console.error('Error fetching country data:', error)
    return null
  }
}

export async function getAllCountries() {
  const { data, error } = await supabase
    .from('countries')
    .select('*')
    .order('name')

  if (error) throw error
  return data
}

export async function getMoodMetrics(countryId: string, category: string) {
  const { data, error } = await supabase
    .from('mood_metrics')
    .select('*')
    .eq('country_id', countryId)
    .eq('category', category)
    .order('timestamp', { ascending: false })
    .limit(1)
    .single()

  if (error) throw error
  return data
}

export async function getTrendingTopics(countryId: string, category: string) {
  const { data, error } = await supabase
    .from('trending_topics')
    .select('*')
    .eq('country_id', countryId)
    .eq('category', category)
    .order('volume', { ascending: false })
    .limit(10)

  if (error) throw error
  return data
}

function transformToCountryData(country: any, categoryData: any): CountryData {
  const data = categoryData.data // JSONB field

  return {
    name: country.name,
    flag: country.flag_emoji,
    lastUpdated: new Date(categoryData.last_updated).toLocaleString(),
    moodSummary: data.summary?.mood_summary || "No data available",
    moodMeter: data.mood_metrics || {
      joy: 0,
      curiosity: 0,
      anger: 0,
      confusion: 0,
      sadness: 0,
    },
    sentimentTrend: data.sentiment_trend || Array(12).fill(50),
    topTopics: data.trending_topics?.slice(0, 10) || [],
    representativeContent: data.items?.slice(0, 10) || [],
    categoryMetrics: {
      totalPosts: data.summary?.total_items || 0,
      avgEngagement: data.summary?.avg_engagement || 0,
      viralityScore: data.summary?.virality_score || 0,
    },
    platformBreakdown: data.platform_breakdown || [],
    engagementStats: data.summary?.engagement_stats || {
      likes: 0,
      shares: 0,
      comments: 0,
    },
  }
}
```

### 4. Update Main Globe Component

Modify the main globe component to fetch real data:

```typescript
// In your globe component or page
import { getCountryData } from '@/lib/api/country-data'

const [countryData, setCountryData] = useState<CountryData | null>(null)
const [selectedCountry, setSelectedCountry] = useState<string | null>(null)
const [selectedCategory, setSelectedCategory] = useState<Category>("Memes")

// Fetch data when country or category changes
useEffect(() => {
  if (!selectedCountry) return

  async function fetchData() {
    const data = await getCountryData(selectedCountry, selectedCategory)
    setCountryData(data)
  }

  fetchData()
}, [selectedCountry, selectedCategory])
```

### 5. Update Category Mapping

The current frontend categories need to map to our data categories:

```typescript
const categoryMapping = {
  "Memes": "memes",
  "Economics": "economics",
  "Politics": "politics",
  "Sports": "sports",
  "Entertainment": "youtube", // Map to YouTube category
  "Technology": "news", // Could be a subset of news
  "News": "news",
  "Google Trends": "google_trends",
  "YouTube": "youtube"
}
```

### 6. Add Real-time Updates (Optional)

For live data updates using Supabase Realtime:

```typescript
import { supabase } from '@/lib/supabase'

useEffect(() => {
  if (!selectedCountry) return

  // Subscribe to changes
  const channel = supabase
    .channel('country-data-changes')
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'category_data',
        filter: `country_id=eq.${countryId}`,
      },
      (payload) => {
        // Update state with new data
        setCountryData(transformToCountryData(country, payload.new))
      }
    )
    .subscribe()

  return () => {
    supabase.removeChannel(channel)
  }
}, [selectedCountry, countryId])
```

### 7. Environment Variables

Add to `earth-3d/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 8. Update Package Dependencies

Add to `earth-3d/package.json`:

```bash
npm install @supabase/supabase-js
```

## Data Flow

```
┌─────────────────┐
│   Data Scrapers │
│  (Python/Node)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Process & ETL  │
│   (Transform)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Supabase     │
│   (PostgreSQL)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Next.js API    │
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3D Globe UI    │
│ CountryInfoPanel│
└─────────────────┘
```

## Testing Strategy

1. **Mock Data First**: Continue using mock data while building scrapers
2. **Hybrid Approach**: Mix mock + real data during development
3. **Full Integration**: Switch to 100% real data once scrapers are complete

## Content Type Rendering

The `renderContentCard` function in CountryInfoPanel already supports:
- ✅ video (YouTube videos)
- ✅ reddit (Reddit posts)
- ✅ news (News articles)
- ✅ twitter (Tweets)
- ✅ article (Generic articles)

We may need to add:
- 🆕 meme (Meme images/videos)
- 🆕 short (YouTube Shorts)
- 🆕 trend (Google Trends)

## Performance Considerations

1. **Caching**: Cache country data on the frontend for 5-10 minutes
2. **Loading States**: Show skeleton loaders while fetching
3. **Error Handling**: Graceful fallbacks if data unavailable
4. **Pagination**: Load content items in batches
5. **CDN**: Serve media (images/videos) through CDN

## Next Steps

1. Set up Supabase project
2. Create database schema
3. Build data upload pipeline
4. Update frontend components
5. Test with real data
6. Deploy!
