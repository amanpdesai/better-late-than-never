import fs from "fs"
import path from "path"
import type {
  MemesData,
  GoogleTrendsData,
  NewsData,
  PoliticsData,
  EconomicsData,
  SportsData,
  EntertainmentData,
  TechnologyData,
  CountryData,
  CountryMetadata,
  Category,
  MoodKey,
  Sentiment,
  ContentItem,
} from "./types"

// Path to the data directory
const DATA_DIR = path.join(process.cwd(), "..", "data")

// Country code mapping
const COUNTRY_CODES: Record<string, { name: string; flag: string }> = {
  USA: { name: "United States", flag: "🇺🇸" },
  UK: { name: "United Kingdom", flag: "🇬🇧" },
  Canada: { name: "Canada", flag: "🇨🇦" },
  India: { name: "India", flag: "🇮🇳" },
  Australia: { name: "Australia", flag: "🇦🇺" },
  United_States: { name: "United States", flag: "🇺🇸" },
  United_Kingdom: { name: "United Kingdom", flag: "🇬🇧" },
}

// Category mapping - matches actual data directories
const CATEGORY_DIRS: Record<string, string> = {
  All: "", // Special case - will load all categories
  Memes: "memes",
  News: "news",
  Politics: "politics",
  Economics: "economics",
  Sports: "sports",
}

/**
 * Get the latest JSON file for a country and category
 */
function getLatestFile(categoryPath: string, countryCode: string): string | null {
  try {
    const countryPath = path.join(categoryPath, countryCode)
    if (!fs.existsSync(countryPath)) {
      return null
    }

    const files = fs.readdirSync(countryPath).filter((f) => f.endsWith(".json"))
    if (files.length === 0) {
      return null
    }

    // Sort by date (filename format: YYYY-MM-DD.json)
    files.sort().reverse()
    return path.join(countryPath, files[0])
  } catch (error) {
    console.error(`Error getting latest file for ${countryCode}:`, error)
    return null
  }
}

/**
 * Load data for a specific category and country
 */
function loadCategoryData<T>(category: Category, countryCode: string): T | null {
  try {
    const categoryDir = CATEGORY_DIRS[category]

    // If category not in our mapping, return null
    if (!categoryDir && category !== "All") {
      return null
    }

    const categoryPath = path.join(DATA_DIR, categoryDir)
    const filePath = getLatestFile(categoryPath, countryCode)

    if (!filePath || !fs.existsSync(filePath)) {
      return null
    }

    const rawData = fs.readFileSync(filePath, "utf-8")
    return JSON.parse(rawData) as T
  } catch (error) {
    console.error(`Error loading ${category} data for ${countryCode}:`, error)
    return null
  }
}

/**
 * Calculate mood meter from content items
 */
function calculateMoodMeter(items: ContentItem[]): Record<MoodKey, number> {
  const sentimentCounts: Record<Sentiment, number> = {
    positive: 0,
    negative: 0,
    neutral: 0,
  }

  items.forEach((item) => {
    sentimentCounts[item.sentiment] = (sentimentCounts[item.sentiment] || 0) + 1
  })

  const total = items.length || 1

  // Map sentiment to mood
  const positivePercent = (sentimentCounts.positive / total) * 100
  const negativePercent = (sentimentCounts.negative / total) * 100
  const neutralPercent = (sentimentCounts.neutral / total) * 100

  return {
    joy: Math.round(positivePercent * 0.7), // Joy correlates with positive
    curiosity: Math.round(neutralPercent * 0.5 + positivePercent * 0.3), // Curiosity from neutral and some positive
    anger: Math.round(negativePercent * 0.6), // Anger from negative
    confusion: Math.round(neutralPercent * 0.3 + negativePercent * 0.2), // Confusion from neutral and some negative
    sadness: Math.round(negativePercent * 0.4), // Sadness from negative
  }
}

/**
 * Calculate sentiment trend (mock data for now - would need historical data)
 */
function calculateSentimentTrend(items: ContentItem[]): number[] {
  // For now, generate based on current sentiment
  const avgSentiment =
    items.reduce((acc, item) => {
      if (item.sentiment === "positive") return acc + 75
      if (item.sentiment === "negative") return acc + 25
      return acc + 50
    }, 0) / (items.length || 1)

  // Generate 12 data points with some variance
  return Array.from({ length: 12 }, (_, i) => {
    const variance = Math.random() * 20 - 10
    return Math.max(0, Math.min(100, avgSentiment + variance))
  })
}

/**
 * Extract top topics from content items and trends
 */
function extractTopTopics(
  items: ContentItem[],
  trendsData: GoogleTrendsData | null,
): Array<{ keyword: string; sentiment: Sentiment; volume: number }> {
  const topics: Array<{ keyword: string; sentiment: Sentiment; volume: number }> = []

  // Add trending searches from Google Trends
  if (trendsData?.trending_searches) {
    trendsData.trending_searches.slice(0, 5).forEach((search) => {
      topics.push({
        keyword: search.query,
        sentiment: "neutral",
        volume: parseInt(search.traffic_label.replace(/[^0-9]/g, "")) || 100,
      })
    })
  }

  // Add topics from content tags and sport field
  const tagCounts: Record<string, { count: number; sentiment: Sentiment }> = {}
  items.forEach((item) => {
    // Add tags if they exist
    item.tags?.forEach((tag) => {
      if (!tagCounts[tag]) {
        tagCounts[tag] = { count: 0, sentiment: item.sentiment }
      }
      tagCounts[tag].count++
    })

    // Add sport as a topic for sports content
    if (item.sport) {
      if (!tagCounts[item.sport]) {
        tagCounts[item.sport] = { count: 0, sentiment: item.sentiment }
      }
      tagCounts[item.sport].count++
    }
  })

  // Sort by count and add top tags/sports
  const topTags = Object.entries(tagCounts)
    .sort(([, a], [, b]) => b.count - a.count)
    .slice(0, 5)
    .map(([tag, data]) => ({
      keyword: tag,
      sentiment: data.sentiment,
      volume: data.count,
    }))

  topics.push(...topTags)

  return topics.slice(0, 8)
}

/**
 * Calculate platform breakdown
 */
function calculatePlatformBreakdown(
  items: ContentItem[],
): Array<{ platform: string; percentage: number }> {
  const platformCounts: Record<string, number> = {}
  items.forEach((item) => {
    const platform = item.source_platform || "Other"
    platformCounts[platform] = (platformCounts[platform] || 0) + 1
  })

  const total = items.length || 1
  return Object.entries(platformCounts)
    .map(([platform, count]) => ({
      platform: platform.charAt(0).toUpperCase() + platform.slice(1),
      percentage: Math.round((count / total) * 100),
    }))
    .sort((a, b) => b.percentage - a.percentage)
    .slice(0, 4)
}

/**
 * Generate mood summary text
 */
function generateMoodSummary(
  countryName: string,
  category: Category,
  sentiment: Record<MoodKey, number>,
): string {
  const dominant = Object.entries(sentiment).sort(([, a], [, b]) => b - a)[0][0]

  const summaries: Record<string, string[]> = {
    joy: [
      `${countryName}'s ${category.toLowerCase()} scene is vibrant and optimistic.`,
      `High spirits dominate ${countryName}'s ${category.toLowerCase()} conversations.`,
      `${countryName} is experiencing positive vibes in ${category.toLowerCase()}.`,
    ],
    curiosity: [
      `${countryName} shows strong interest and engagement in ${category.toLowerCase()}.`,
      `Exploration and discovery drive ${countryName}'s ${category.toLowerCase()} discussions.`,
      `${countryName}'s ${category.toLowerCase()} space is filled with questions and learning.`,
    ],
    anger: [
      `Frustration and strong opinions mark ${countryName}'s ${category.toLowerCase()} dialogue.`,
      `${countryName} is experiencing heated debates in ${category.toLowerCase()}.`,
      `Tension and criticism dominate ${countryName}'s ${category.toLowerCase()} landscape.`,
    ],
    confusion: [
      `${countryName}'s ${category.toLowerCase()} discussions show uncertainty and mixed signals.`,
      `Ambiguity characterizes ${countryName}'s ${category.toLowerCase()} conversations.`,
      `${countryName} is navigating complex ${category.toLowerCase()} narratives.`,
    ],
    sadness: [
      `${countryName}'s ${category.toLowerCase()} mood leans toward concern and reflection.`,
      `Somber tones color ${countryName}'s ${category.toLowerCase()} discussions.`,
      `${countryName} shows empathy and seriousness in ${category.toLowerCase()}.`,
    ],
  }

  const options = summaries[dominant] || [
    `${countryName}'s ${category.toLowerCase()} landscape shows diverse perspectives.`,
  ]
  return options[Math.floor(Math.random() * options.length)]
}

/**
 * Load aggregated country data for a specific category
 */
export async function loadCountryData(countryCode: string, category: Category): Promise<CountryData | null> {
  try {
    const countryInfo = COUNTRY_CODES[countryCode]
    if (!countryInfo) {
      console.error(`Unknown country code: ${countryCode}`)
      return null
    }

    // Load data for the category
    let items: ContentItem[] = []
    let lastUpdated = new Date().toISOString()
    const categoryBreakdown: Array<{ category: Category; count: number; sentiment: string }> = []
    let rawCategoryData: PoliticsData | EconomicsData | MemesData | NewsData | SportsData | undefined

    // Special case: Load ALL categories
    if (category === "All") {
      const categories: Category[] = ["Memes", "News", "Politics", "Economics", "Sports"]

      for (const cat of categories) {
        const catData = await loadCountryData(countryCode, cat)
        if (catData) {
          items.push(...catData.representativeContent)

          // Track category breakdown
          const sentimentCounts = { positive: 0, negative: 0, neutral: 0 }
          catData.representativeContent.forEach(item => {
            sentimentCounts[item.sentiment]++
          })
          const dominantSentiment = Object.entries(sentimentCounts)
            .sort(([, a], [, b]) => b - a)[0][0]

          categoryBreakdown.push({
            category: cat,
            count: catData.representativeContent.length,
            sentiment: dominantSentiment,
          })
        }
      }

      lastUpdated = new Date().toISOString()
    } else {
      // Load single category
      switch (category) {
      case "Memes": {
        const data = loadCategoryData<MemesData>(category, countryCode)
        if (data) {
          items = data.items
          lastUpdated = data.timestamp
          rawCategoryData = data
        }
        break
      }
      case "Politics": {
        const data = loadCategoryData<PoliticsData>(category, countryCode)
        if (data) {
          // Convert politics data to content items
          items = data.political_climate?.recent_headlines?.map((headline, idx) => ({
            id: `politics_${idx}`,
            title: headline.title,
            excerpt: "",
            source_platform: "news",
            source_name: headline.source,
            source_url: headline.url,
            created_at: headline.published_at,
            engagement: {},
            sentiment: "neutral" as Sentiment,
            virality_score: 50,
          })) || []
          lastUpdated = data.timestamp
          rawCategoryData = data
        }
        break
      }
      case "Economics": {
        const data = loadCategoryData<EconomicsData>(category, countryCode)
        if (data) {
          // Convert economics data to content items
          items = data.news_headlines?.map((headline, idx) => ({
            id: `economics_${idx}`,
            title: headline.title,
            excerpt: "",
            source_platform: "news",
            source_name: headline.source,
            source_url: headline.url,
            created_at: headline.published_at,
            engagement: {},
            sentiment: "neutral" as Sentiment,
            virality_score: 50,
          })) || []
          lastUpdated = data.timestamp
          rawCategoryData = data
        }
        break
      }
      case "Sports": {
        const data = loadCategoryData<SportsData>(category, countryCode)
        if (data) {
          items = data.items
          lastUpdated = data.timestamp
          rawCategoryData = data
        }
        break
      }
      case "Entertainment":
      case "Technology": {
        const data = loadCategoryData<EntertainmentData | TechnologyData>(category, countryCode)
        if (data) {
          items = data.items || []
          lastUpdated = data.timestamp
        }
        break
      }
      default: {
        const data = loadCategoryData<NewsData>(category, countryCode)
        if (data) {
          items = data.items
          lastUpdated = data.timestamp
          rawCategoryData = data
        }
      }
      }
    }

    if (items.length === 0) {
      return null
    }

    // Load Google Trends data for topics
    const trendsData = loadCategoryData<GoogleTrendsData>("Technology", countryCode) // Using Technology as fallback

    // Calculate metrics
    const moodMeter = calculateMoodMeter(items)
    const sentimentTrend = calculateSentimentTrend(items)
    const topTopics = extractTopTopics(items, trendsData)
    const platformBreakdown = calculatePlatformBreakdown(items)

    // Sort by virality and take top items
    const representativeContent = items
      .sort((a, b) => b.virality_score - a.virality_score)
      .slice(0, 8)
      .map((item) => ({
        ...item,
        type: item.type || (item.source_platform === "reddit" ? "reddit" : "article"),
      }))

    // Calculate engagement stats
    const engagementStats = items.reduce(
      (acc, item) => ({
        likes: acc.likes + (item.engagement.likes || 0),
        shares: acc.shares + (item.engagement.shares || 0),
        comments: acc.comments + (item.engagement.comments || 0),
      }),
      { likes: 0, shares: 0, comments: 0 },
    )

    // Calculate category metrics
    const avgEngagement =
      items.reduce((acc, item) => {
        const total =
          (item.engagement.likes || 0) +
          (item.engagement.comments || 0) +
          (item.engagement.shares || 0) +
          (item.engagement.views || 0) / 100 // Scale down views
        return acc + total
      }, 0) / items.length

    const avgViralityScore = items.reduce((acc, item) => acc + item.virality_score, 0) / items.length

    return {
      name: countryInfo.name,
      flag: countryInfo.flag,
      lastUpdated: new Date(lastUpdated).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
      }),
      moodSummary: generateMoodSummary(countryInfo.name, category, moodMeter),
      moodMeter,
      sentimentTrend,
      topTopics,
      representativeContent,
      categoryMetrics: {
        totalPosts: items.length,
        avgEngagement: avgEngagement / 1000, // Convert to k
        viralityScore: Math.round(avgViralityScore),
      },
      platformBreakdown,
      engagementStats,
      categoryBreakdown: categoryBreakdown.length > 0 ? categoryBreakdown : undefined,
      categoryData: rawCategoryData,
    }
  } catch (error) {
    console.error(`Error loading country data for ${countryCode}:`, error)
    return null
  }
}

/**
 * Get list of all available countries
 */
export async function getAvailableCountries(): Promise<CountryMetadata[]> {
  const countries: CountryMetadata[] = []

  try {
    // Check memes directory for available countries
    const memesDir = path.join(DATA_DIR, "memes")
    if (fs.existsSync(memesDir)) {
      const countryCodes = fs.readdirSync(memesDir).filter((f) => {
        const stat = fs.statSync(path.join(memesDir, f))
        return stat.isDirectory()
      })

      for (const code of countryCodes) {
        const countryInfo = COUNTRY_CODES[code]
        if (countryInfo) {
          // Check which categories have data
          const availableCategories: Category[] = []
          for (const [category, dir] of Object.entries(CATEGORY_DIRS)) {
            const categoryPath = path.join(DATA_DIR, dir, code)
            if (fs.existsSync(categoryPath)) {
              const files = fs.readdirSync(categoryPath).filter((f) => f.endsWith(".json"))
              if (files.length > 0) {
                availableCategories.push(category as Category)
              }
            }
          }

          if (availableCategories.length > 0) {
            // Get latest update time
            const latestFile = getLatestFile(memesDir, code)
            let lastUpdated = new Date().toISOString()
            if (latestFile) {
              const data = JSON.parse(fs.readFileSync(latestFile, "utf-8"))
              lastUpdated = data.timestamp || lastUpdated
            }

            countries.push({
              name: countryInfo.name,
              code,
              flag: countryInfo.flag,
              availableCategories,
              lastUpdated,
            })
          }
        }
      }
    }
  } catch (error) {
    console.error("Error getting available countries:", error)
  }

  return countries
}

/**
 * Get country slug from country code
 */
export function getCountrySlug(countryCode: string): string {
  const countryInfo = COUNTRY_CODES[countryCode]
  return countryInfo ? countryInfo.name.toLowerCase().replace(/\s+/g, "-") : countryCode.toLowerCase()
}

/**
 * Get country code from slug
 */
export function getCountryCodeFromSlug(slug: string): string | null {
  const name = slug.replace(/-/g, " ")
  for (const [code, info] of Object.entries(COUNTRY_CODES)) {
    if (info.name.toLowerCase() === name) {
      return code
    }
  }
  return null
}
