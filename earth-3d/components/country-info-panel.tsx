"use client"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { X, ExternalLink, ArrowRight, Play, MessageCircle, ArrowUp, Eye } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

type Category = "Memes" | "Economics" | "Politics" | "Sports" | "Entertainment" | "Technology"

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
    title: string
    excerpt: string
    engagement: number
    platform: string
    sentiment: "positive" | "negative" | "neutral"
    type: "video" | "reddit" | "news" | "twitter" | "article"
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

interface CountryInfoPanelProps {
  countryData: CountryData | null
  onClose: () => void
  category: Category
  onCategoryChange: (category: Category) => void
  showFullPageLink?: boolean
  isOpen?: boolean
}

export function CountryInfoPanel({
  countryData,
  onClose,
  category,
  onCategoryChange,
  showFullPageLink = true,
  isOpen = true,
}: CountryInfoPanelProps) {
  if (!countryData) return null

  const categories: Category[] = ["Memes", "Economics", "Politics", "Sports", "Entertainment", "Technology"]

  const moodColors = {
    joy: "bg-yellow-500",
    curiosity: "bg-blue-500",
    anger: "bg-red-500",
    confusion: "bg-purple-500",
    sadness: "bg-gray-500",
  }

  const sentimentColors = {
    positive: "text-green-500 bg-green-500/10 border-green-500/20",
    negative: "text-red-500 bg-red-500/10 border-red-500/20",
    neutral: "text-gray-500 bg-gray-500/10 border-gray-500/20",
  }

  const countrySlug = countryData.name.toLowerCase().replace(/\s+/g, "-")

  const renderContentCard = (content: CountryData["representativeContent"][0], index: number) => {
    const baseCardClasses = "bg-white/5 border-white/10 hover:bg-white/10 transition-colors cursor-pointer group"

    switch (content.type) {
      case "video":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="relative">
              {content.thumbnail && (
                <div className="relative h-40 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-t-lg overflow-hidden">
                  <img
                    src={content.thumbnail || "/placeholder.svg"}
                    alt={content.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center group-hover:bg-black/30 transition-colors">
                    <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center">
                      <Play className="w-6 h-6 text-white ml-1" fill="white" />
                    </div>
                  </div>
                  {content.views && (
                    <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs text-white flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      {(content.views / 1000).toFixed(1)}k views
                    </div>
                  )}
                </div>
              )}
              <div className="p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-red-500/10 border-red-500/30 text-red-400">
                    {content.platform}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                </div>
                <h4 className="text-white font-medium text-sm leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                  {content.title}
                </h4>
                {content.author && <p className="text-xs text-gray-500">by {content.author}</p>}
              </div>
            </div>
          </Card>
        )

      case "reddit":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="p-4 space-y-3">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs bg-orange-500/10 border-orange-500/30 text-orange-400">
                  {content.platform}
                </Badge>
                <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                  {content.sentiment}
                </Badge>
              </div>
              <h4 className="text-white font-medium text-sm leading-snug group-hover:text-blue-400 transition-colors">
                {content.title}
              </h4>
              <p className="text-gray-400 text-xs line-clamp-2">{content.excerpt}</p>
              <div className="flex items-center gap-4 text-xs pt-2 border-t border-white/5">
                <div className="flex items-center gap-1 text-orange-400">
                  <ArrowUp className="w-3 h-3" />
                  <span className="font-medium">{content.upvotes?.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1 text-gray-400">
                  <MessageCircle className="w-3 h-3" />
                  <span>{content.comments?.toLocaleString()}</span>
                </div>
                {content.source && <span className="text-gray-500">r/{content.source}</span>}
              </div>
            </div>
          </Card>
        )

      case "news":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="relative">
              {content.thumbnail && (
                <div className="relative h-32 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-t-lg overflow-hidden">
                  <img
                    src={content.thumbnail || "/placeholder.svg"}
                    alt={content.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-blue-500/10 border-blue-500/30 text-blue-400">
                    News
                  </Badge>
                  {content.source && <span className="text-xs text-gray-500 font-medium">{content.source}</span>}
                </div>
                <h4 className="text-white font-medium text-sm leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                  {content.title}
                </h4>
                <p className="text-gray-400 text-xs line-clamp-2">{content.excerpt}</p>
                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <span className="text-xs text-gray-500">{content.engagement.toLocaleString()} reads</span>
                  <ExternalLink className="w-3 h-3 text-gray-500 group-hover:text-blue-400 transition-colors" />
                </div>
              </div>
            </div>
          </Card>
        )

      case "twitter":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="p-4 space-y-3">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs bg-sky-500/10 border-sky-500/30 text-sky-400">
                  {content.platform}
                </Badge>
                <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                  {content.sentiment}
                </Badge>
              </div>
              {content.author && (
                <p className="text-sm text-gray-400">
                  <span className="text-white font-medium">{content.author}</span>
                </p>
              )}
              <p className="text-white text-sm leading-relaxed">{content.excerpt}</p>
              <div className="flex items-center gap-4 text-xs text-gray-500 pt-2 border-t border-white/5">
                <span>{(content.engagement * 0.5).toFixed(0)} likes</span>
                <span>{(content.engagement * 0.3).toFixed(0)} retweets</span>
                <span>{(content.engagement * 0.2).toFixed(0)} replies</span>
              </div>
            </div>
          </Card>
        )

      default:
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="p-4 space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {content.platform}
                    </Badge>
                    <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                      {content.sentiment}
                    </Badge>
                  </div>
                  <h4 className="text-white font-medium text-sm leading-snug group-hover:text-blue-400 transition-colors">
                    {content.title}
                  </h4>
                  <p className="text-gray-400 text-xs line-clamp-2">{content.excerpt}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>{content.engagement.toLocaleString()} engagements</span>
                  </div>
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </div>
          </Card>
        )
    }
  }

  return (
    <div
      data-state={isOpen ? "open" : "closed"}
      className={cn(
        "fixed top-0 right-0 h-screen w-full md:w-[480px] bg-black/95 backdrop-blur-xl border-l border-white/10 z-50 overflow-y-auto transition-all duration-300 ease-out",
        isOpen ? "translate-x-0 opacity-100" : "translate-x-full opacity-0 pointer-events-none",
      )}
    >
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-5xl">{countryData.flag}</span>
            <div>
              <h2 className="text-2xl font-bold text-white">{countryData.name}</h2>
              <p className="text-sm text-gray-400">Last Updated: {countryData.lastUpdated}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              className="font-bold text-blue-600 bg-blue-300 border-white/20 hover:bg-gray-500/40 hover:text-blue-300"
              asChild
            >
              <Link href={`/country/${countrySlug}?category=${category}`}>
                <Eye className="w-4 h-4" aria-hidden />
                <span className="sr-only">View full page</span>
              </Link>
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose} className="text-white hover:bg-white/10">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {showFullPageLink && (
          <div className="space-y-4 pt-4 mt-4 border-t border-white/10">
            <Link href={`/country/${countrySlug}?category=${category}`}>
              <Button className="w-full bg-blue-100 text-blue-700 hover:bg-gray-200 hover:text-white group">
                View Full Page
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </div>
        )}

        {/* Mood Summary */}
        <Card className="bg-white/5 border-white/10 p-4">
          <p className="text-gray-300 text-sm leading-relaxed">{countryData.moodSummary}</p>
        </Card>

        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-400">Select Category</h3>
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <Button
                key={cat}
                variant="outline"
                size="sm"
                onClick={() => onCategoryChange(cat)}
                className={`transition-all duration-200 ${
                  category === cat
                    ? "bg-blue-600 border-blue-600 text-white hover:bg-blue-700 hover:border-blue-700"
                    : "bg-white/5 border-white/20 text-gray-300 hover:bg-blue-300 hover:text-blue-900"
                }`}
              >
                {cat}
              </Button>
            ))}
          </div>
        </div>

        {/* Mood Meter */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Mood Meter</h3>
          <div className="space-y-2">
            {Object.entries(countryData.moodMeter).map(([mood, value]) => (
              <div key={mood} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400 capitalize">{mood}</span>
                  <span className="text-white font-medium">{value}%</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${moodColors[mood as keyof typeof moodColors]} transition-all duration-500`}
                    style={{ width: `${value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sentiment Trend */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Sentiment Trend</h3>
          <div className="h-16 flex items-end gap-1">
            {countryData.sentimentTrend.map((value, index) => (
              <div
                key={index}
                className="flex-1 bg-blue-500/30 rounded-t transition-all duration-300 hover:bg-blue-500/50"
                style={{ height: `${value}%` }}
              />
            ))}
          </div>
          <p className="text-xs text-gray-500">Past 12 hours</p>
        </div>

        {/* Top Topics */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Top Topics</h3>
          <div className="flex flex-wrap gap-2">
            {countryData.topTopics.map((topic, index) => (
              <Badge
                key={index}
                variant="outline"
                className={`${sentimentColors[topic.sentiment]} cursor-pointer hover:scale-105 transition-transform`}
              >
                #{topic.keyword}
                <span className="ml-1 text-xs opacity-70">({topic.volume}k)</span>
              </Badge>
            ))}
          </div>
        </div>

        {/* Representative Content */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Representative Content</h3>
          <div className="space-y-3">
            {countryData.representativeContent.slice(0, 4).map((content, index) => renderContentCard(content, index))}
          </div>
        </div>

        {/* Category Metrics */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Category Metrics - {category}</h3>
          <div className="grid grid-cols-3 gap-3">
            <Card className="bg-white/5 border-white/10 p-4 text-center">
              <p className="text-2xl font-bold text-white">{countryData.categoryMetrics.totalPosts.toLocaleString()}</p>
              <p className="text-xs text-gray-400 mt-1">Total Posts</p>
            </Card>
            <Card className="bg-white/5 border-white/10 p-4 text-center">
              <p className="text-2xl font-bold text-white">{countryData.categoryMetrics.avgEngagement.toFixed(1)}k</p>
              <p className="text-xs text-gray-400 mt-1">Avg Engagement</p>
            </Card>
            <Card className="bg-white/5 border-white/10 p-4 text-center">
              <p className="text-2xl font-bold text-white">{countryData.categoryMetrics.viralityScore}</p>
              <p className="text-xs text-gray-400 mt-1">Virality Score</p>
            </Card>
          </div>
        </div>

        {/* Platform Breakdown */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Platform Breakdown</h3>
          <div className="space-y-2">
            {countryData.platformBreakdown.map((platform, index) => (
              <div key={index} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">{platform.platform}</span>
                  <span className="text-white font-medium">{platform.percentage}%</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                    style={{ width: `${platform.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Engagement Stats */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Engagement Stats</h3>
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{(countryData.engagementStats.likes / 1000).toFixed(1)}k</p>
              <p className="text-xs text-gray-400 mt-1">Likes</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{(countryData.engagementStats.shares / 1000).toFixed(1)}k</p>
              <p className="text-xs text-gray-400 mt-1">Shares</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">
                {(countryData.engagementStats.comments / 1000).toFixed(1)}k
              </p>
              <p className="text-xs text-gray-400 mt-1">Comments</p>
            </div>
          </div>
        </div>

        <Link href={`/country/${countrySlug}?category=${category}`}>
          <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white group">
            View Full Page
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </Button>
        </Link>
      </div>
    </div>
  )
}
