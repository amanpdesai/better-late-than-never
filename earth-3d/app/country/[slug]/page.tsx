"use client"

import { Navbar } from "@/components/navbar"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  ArrowLeft,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  MessageSquare,
  Heart,
  Share2,
  Play,
  ArrowUp,
  Eye,
  MessageCircle,
} from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts"
import { useEffect, useState } from "react"
import type { CountryData, Category, ContentItem, Sentiment, MoodKey } from "@/lib/types"
import { PoliticsView } from "@/components/category-views/PoliticsView"
import { EconomicsView } from "@/components/category-views/EconomicsView"
import { MemesView } from "@/components/category-views/MemesView"
import { NewsView } from "@/components/category-views/NewsView"
import { SportsView } from "@/components/category-views/SportsView"
import { GoogleTrendsView } from "@/components/category-views/GoogleTrendsView"
import { ComprehensiveDataView } from "@/components/comprehensive-data-view"
import { cn } from "@/lib/utils"

const CATEGORIES: Category[] = ["All", "Memes", "News", "Politics", "Economics", "Sports", "Google Trends"]

export default function CountryDetailPage({ params }: { params: { slug: string } }) {
  const searchParams = useSearchParams()
  const [category, setCategory] = useState<Category>((searchParams.get("category") as Category) || "All")
  const [countryData, setCountryData] = useState<CountryData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const response = await fetch(`/api/country/${params.slug}?category=${category}`)
        if (response.ok) {
          const data = await response.json()
          setCountryData(data)
        }
      } catch (error) {
        console.error("Error loading country data:", error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [params.slug, category])

  const moodColors: Record<MoodKey, string> = {
    joy: "bg-yellow-500",
    curiosity: "bg-blue-500",
    anger: "bg-red-500",
    confusion: "bg-purple-500",
    sadness: "bg-gray-500",
  }

  const sentimentColors: Record<Sentiment, string> = {
    positive: "text-green-500 bg-green-500/10 border-green-500/20",
    negative: "text-red-500 bg-red-500/10 border-red-500/20",
    neutral: "text-gray-500 bg-gray-500/10 border-gray-500/20",
  }

  const renderContentCard = (content: ContentItem, index: number) => {
    const baseCardClasses = "bg-white/5 border-white/10 p-5 hover:bg-white/10 transition-all cursor-pointer group"
    const contentType =
      content.type || (content.source_platform === "reddit" ? "reddit" : content.source_platform === "youtube" ? "video" : "article")

    switch (contentType) {
      case "video":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              {(content.thumbnail || content.media?.thumbnail) && (
                <div className="relative h-48 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-lg overflow-hidden">
                  <img
                    src={content.thumbnail || content.media?.thumbnail || "/placeholder.svg"}
                    alt={content.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center group-hover:bg-black/30 transition-colors">
                    <div className="w-16 h-16 rounded-full bg-red-600 flex items-center justify-center">
                      <Play className="w-8 h-8 text-white ml-1" fill="white" />
                    </div>
                  </div>
                  {content.views && (
                    <div className="absolute bottom-3 right-3 bg-black/80 px-3 py-1 rounded text-sm text-white flex items-center gap-2">
                      <Eye className="w-4 h-4" />
                      {(content.views / 1000).toFixed(0)}k views
                    </div>
                  )}
                </div>
              )}
              <div className="space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-red-500/10 border-red-500/30 text-red-400">
                    {content.source_platform || content.source_name || "Video"}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  {content.timestamp && <span className="text-xs text-gray-500">{content.timestamp}</span>}
                </div>
                <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                  {content.title}
                </h4>
                {content.author && <p className="text-sm text-gray-400">by {content.author}</p>}
                <div className="flex items-center justify-between pt-3 border-t border-white/5">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Heart className="w-4 h-4" />
                      <span>{(content.engagement?.likes || content.virality_score * 100 || 0).toFixed(0)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageSquare className="w-4 h-4" />
                      <span>{(content.engagement?.comments || content.virality_score * 20 || 0).toFixed(0)}</span>
                    </div>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" />
                </div>
              </div>
            </div>
          </Card>
        )

      case "reddit":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-orange-500/10 border-orange-500/30 text-orange-400">
                    {content.source_platform || "Reddit"}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  {content.timestamp && <span className="text-xs text-gray-500">{content.timestamp}</span>}
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </div>
              <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                {content.title}
              </h4>
              <p className="text-gray-400 text-sm line-clamp-2">{content.excerpt || content.content || ""}</p>
              <div className="flex items-center gap-4 text-sm pt-2 border-t border-white/5">
                <div className="flex items-center gap-1 text-orange-400">
                  <ArrowUp className="w-4 h-4" />
                  <span className="font-medium">
                    {(content.upvotes || content.engagement?.upvotes || content.virality_score * 10 || 0).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-gray-400">
                  <MessageCircle className="w-4 h-4" />
                  <span>
                    {(content.comments || content.engagement?.comments || content.virality_score * 2 || 0).toLocaleString()}
                  </span>
                </div>
                {(content.source || content.source_name) && (
                  <span className="text-gray-500">r/{content.source || content.source_name}</span>
                )}
              </div>
            </div>
          </Card>
        )

      case "news":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              {(content.thumbnail || content.media?.thumbnail) && (
                <div className="relative h-48 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-lg overflow-hidden">
                  <img
                    src={content.thumbnail || content.media?.thumbnail || "/placeholder.svg"}
                    alt={content.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-blue-500/10 border-blue-500/30 text-blue-400">
                    News
                  </Badge>
                  {(content.source || content.source_name) && (
                    <span className="text-xs text-gray-400 font-medium">{content.source || content.source_name}</span>
                  )}
                  {content.timestamp && <span className="text-xs text-gray-500">{content.timestamp}</span>}
                </div>
                <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                  {content.title}
                </h4>
                <p className="text-gray-400 text-sm line-clamp-2">{content.excerpt || content.content || ""}</p>
                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>{(content.engagement?.views || content.virality_score * 100 || 0).toLocaleString()} reads</span>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" />
                </div>
              </div>
            </div>
          </Card>
        )

      case "twitter":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-sky-500/10 border-sky-500/30 text-sky-400">
                    {content.source_platform || "Twitter"}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  {content.timestamp && <span className="text-xs text-gray-500">{content.timestamp}</span>}
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </div>
              {content.author && (
                <p className="text-sm text-gray-400">
                  <span className="text-white font-medium">{content.author}</span>
                </p>
              )}
              <p className="text-white text-sm leading-relaxed">{content.excerpt || content.content || content.title}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500 pt-2 border-t border-white/5">
                <div className="flex items-center gap-1">
                  <Heart className="w-4 h-4" />
                  <span>{(content.engagement?.likes || content.virality_score * 10 || 0).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Share2 className="w-4 h-4" />
                  <span>{(content.engagement?.shares || content.virality_score * 5 || 0).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <MessageSquare className="w-4 h-4" />
                  <span>{(content.engagement?.comments || content.virality_score * 3 || 0).toFixed(0)}</span>
                </div>
              </div>
            </div>
          </Card>
        )

      default:
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs">
                    {content.source_platform || content.source_name || "Article"}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  {content.timestamp && <span className="text-xs text-gray-500">{content.timestamp}</span>}
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </div>
              <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                {content.title}
              </h4>
              <p className="text-gray-400 text-sm line-clamp-2">{content.excerpt || content.content || ""}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500 pt-2 border-t border-white/5">
                <div className="flex items-center gap-1">
                  <Heart className="w-4 h-4" />
                  <span>{(content.engagement?.likes || content.virality_score * 10 || 0).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <MessageSquare className="w-4 h-4" />
                  <span>{(content.engagement?.comments || content.virality_score * 2 || 0).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Share2 className="w-4 h-4" />
                  <span>{(content.engagement?.shares || content.virality_score * 2 || 0).toFixed(0)}</span>
                </div>
              </div>
            </div>
          </Card>
        )
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black">
        <Navbar />
        <div className="container mx-auto px-6 py-24 flex items-center justify-center">
          <div className="text-white text-xl">Loading...</div>
        </div>
      </div>
    )
  }

  if (!countryData) {
    return (
      <div className="min-h-screen bg-black">
        <Navbar />
        <div className="container mx-auto px-6 py-24">
          <Link href="/countries">
            <Button variant="ghost" className="text-white hover:bg-white/10 mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Countries
            </Button>
          </Link>
          <div className="text-white text-xl">No data available for this country</div>
        </div>
      </div>
    )
  }

  // Prepare chart data
  const emotionalProfile = Object.entries(countryData.moodMeter).map(([emotion, value]) => ({
    emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
    value,
    fullMark: 100,
  }))

  const historicalSentiment = countryData.sentimentTrend.map((sentiment, index) => ({
    time: `${index * 2}:00`,
    sentiment,
    posts: Math.floor(sentiment * 100 + Math.random() * 1000),
  }))

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      <div className="container mx-auto px-6 py-24">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Back Button */}
          <Link href="/countries">
            <Button variant="ghost" className="text-white hover:bg-white/10 mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Countries
            </Button>
          </Link>

          {/* Enhanced Header with Gradient Background */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500/20 via-purple-500/10 to-pink-500/20 border border-white/10 p-8">
            <div className="relative z-10">
              <div className="flex items-center gap-4 mb-4">
                <span className="text-6xl">{countryData.flag}</span>
                <div>
                  <h1 className="text-5xl font-bold text-white mb-2">{countryData.name}</h1>
                  <div className="flex items-center gap-4 text-gray-400">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>Last Updated: {countryData.lastUpdated}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Category Filters */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Filter by Category</h3>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => (
                <Button
                  key={cat}
                  variant={category === cat ? "default" : "outline"}
                  size="sm"
                  onClick={() => setCategory(cat)}
                  className={cn(
                    "text-sm",
                    category === cat
                      ? "bg-blue-600 text-white hover:bg-blue-700"
                      : "bg-transparent text-gray-300 hover:bg-white/10 hover:text-white border-gray-600",
                  )}
                >
                  {cat}
                </Button>
              ))}
            </div>
          </div>

          {/* Top-level components - Only show for "All" category */}
          {category === "All" && (
            <>
              {/* Enhanced Mood Summary with Stats */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2 bg-white/5 border-white/10 p-6">
                  <h2 className="text-2xl font-semibold text-white mb-4">Current Mood Analysis</h2>
                  <p className="text-gray-300 text-lg leading-relaxed mb-6">{countryData.moodSummary}</p>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/5 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-purple-400">{countryData.categoryMetrics.viralityScore}</p>
                      <p className="text-sm text-gray-400 mt-1">Virality Score</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-blue-400">{countryData.categoryMetrics.totalPosts.toLocaleString()}</p>
                      <p className="text-sm text-gray-400 mt-1">Total Posts</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-4 text-center">
                      <p className="text-3xl font-bold text-green-400">{countryData.categoryMetrics.avgEngagement.toFixed(1)}k</p>
                      <p className="text-sm text-gray-400 mt-1">Avg Engagement</p>
                    </div>
                  </div>
                </Card>

                <Card className="bg-white/5 border-white/10 p-6">
                  <h2 className="text-xl font-semibold text-white mb-4">Quick Stats</h2>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Top Platforms</span>
                      <span className="text-white font-semibold">{countryData.platformBreakdown.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Total Engagement</span>
                      <span className="text-white font-semibold">
                        {((countryData.engagementStats.likes + countryData.engagementStats.comments + countryData.engagementStats.shares) / 1000).toFixed(0)}k
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Trending Topics</span>
                      <span className="text-white font-semibold">{countryData.topTopics.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Content Items</span>
                      <span className="text-white font-semibold">{countryData.representativeContent.length}</span>
                    </div>
                  </div>
                </Card>
              </div>

              {/* Added Comprehensive Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-white/5 border-white/10 p-6">
                  <h2 className="text-2xl font-semibold text-white mb-6">24-Hour Sentiment Trend</h2>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={historicalSentiment}>
                      <defs>
                        <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                      <XAxis dataKey="time" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                      <YAxis stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
                        labelStyle={{ color: "#fff" }}
                      />
                      <Area type="monotone" dataKey="sentiment" stroke="#3b82f6" fill="url(#sentimentGradient)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </Card>

                <Card className="bg-white/5 border-white/10 p-6">
                  <h2 className="text-2xl font-semibold text-white mb-6">Emotional Profile</h2>
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={emotionalProfile}>
                      <PolarGrid stroke="#ffffff20" />
                      <PolarAngleAxis dataKey="emotion" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                      <PolarRadiusAxis stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                      <Radar name="Emotion" dataKey="value" stroke="#ec4899" fill="#ec4899" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                </Card>
              </div>

              {/* Three Column Layout for Detailed Metrics */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column */}
                <div className="space-y-8">
                  {/* Mood Meter */}
                  <Card className="bg-white/5 border-white/10 p-6">
                    <h2 className="text-2xl font-semibold text-white mb-6">Mood Meter</h2>
                    <div className="space-y-4">
                      {Object.entries(countryData.moodMeter).map(([mood, value]) => (
                        <div key={mood} className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400 capitalize text-base">{mood}</span>
                            <span className="text-white font-medium text-base">{value}%</span>
                          </div>
                          <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${moodColors[mood as keyof typeof moodColors]} transition-all duration-500`}
                              style={{ width: `${value}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  {/* Platform Breakdown */}
                  <Card className="bg-white/5 border-white/10 p-6">
                    <h2 className="text-2xl font-semibold text-white mb-6">Platform Breakdown</h2>
                    <div className="space-y-4">
                      {countryData.platformBreakdown.map((platform, index) => (
                        <div key={index} className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400 text-lg">{platform.platform}</span>
                            <span className="text-white font-medium text-lg">{platform.percentage}%</span>
                          </div>
                          <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                              style={{ width: `${platform.percentage}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>

                {/* Middle Column */}
                <div className="space-y-8">
                  {/* Top Topics - Expanded */}
                  <Card className="bg-white/5 border-white/10 p-6">
                    <h2 className="text-2xl font-semibold text-white mb-6">Top Topics</h2>
                    <div className="flex flex-wrap gap-3">
                      {countryData.topTopics.map((topic, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className={`${sentimentColors[topic.sentiment]} cursor-pointer hover:scale-105 transition-transform text-sm py-2 px-3`}
                        >
                          #{topic.keyword}
                          <span className="ml-2 opacity-70">({topic.volume}k)</span>
                        </Badge>
                      ))}
                    </div>
                  </Card>

                  {/* Engagement Stats */}
                  <Card className="bg-white/5 border-white/10 p-6">
                    <h2 className="text-2xl font-semibold text-white mb-6">Engagement Stats</h2>
                    <div className="grid grid-cols-1 gap-6">
                      <div className="text-center p-6 bg-white/5 rounded-lg">
                        <p className="text-4xl font-bold text-white mb-2">
                          {(countryData.engagementStats.likes / 1000).toFixed(1)}k
                        </p>
                        <p className="text-sm text-gray-400">Likes</p>
                      </div>
                      <div className="text-center p-6 bg-white/5 rounded-lg">
                        <p className="text-4xl font-bold text-white mb-2">
                          {(countryData.engagementStats.shares / 1000).toFixed(1)}k
                        </p>
                        <p className="text-sm text-gray-400">Shares</p>
                      </div>
                      <div className="text-center p-6 bg-white/5 rounded-lg">
                        <p className="text-4xl font-bold text-white mb-2">
                          {(countryData.engagementStats.comments / 1000).toFixed(1)}k
                        </p>
                        <p className="text-sm text-gray-400">Comments</p>
                      </div>
                    </div>
                  </Card>
                </div>

                {/* Right Column - Sentiment Trend */}
                <div className="space-y-8">
                  <Card className="bg-white/5 border-white/10 p-6">
                    <h2 className="text-2xl font-semibold text-white mb-6">Sentiment Trend</h2>
                    <div className="h-32 flex items-end gap-2">
                      {countryData.sentimentTrend.map((value, index) => (
                        <div
                          key={index}
                          className="flex-1 bg-blue-500/30 rounded-t transition-all duration-300 hover:bg-blue-500/50"
                          style={{ height: `${value}%` }}
                        />
                      ))}
                    </div>
                    <p className="text-sm text-gray-500 mt-4">Past 12 hours</p>
                  </Card>
                </div>
              </div>
            </>
          )}

          {/* Category-Specific Content */}
          {category === "Politics" && countryData.categoryData ? (
            <PoliticsView data={countryData.categoryData} />
          ) : category === "Economics" && countryData.categoryData ? (
            <EconomicsView data={countryData.categoryData} />
          ) : category === "Memes" && (countryData.categoryData || countryData.allCategoryData?.memes) ? (
            <MemesView data={countryData.categoryData || countryData.allCategoryData?.memes!} />
          ) : category === "News" && countryData.categoryData ? (
            <NewsView data={countryData.categoryData} />
          ) : category === "Sports" && countryData.categoryData ? (
            <SportsView data={countryData.categoryData} />
          ) : category === "Google Trends" && countryData.categoryData ? (
            <GoogleTrendsView data={countryData.categoryData} />
          ) : (
            /* Default view for "All" category - show comprehensive data view */
            <ComprehensiveDataView countryData={countryData} onCategoryChange={setCategory} hideTopMetrics={false} />
          )}
        </div>
      </div>
    </div>
  )
}
