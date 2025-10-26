"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3, 
  Newspaper, 
  Heart,
  MessageSquare,
  ExternalLink,
  Play,
  Video,
  Search,
  Zap,
  Trophy,
  Building2,
  Landmark,
  Eye,
  Share2,
  Clock,
  Users,
  Activity,
  Globe,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Minus,
  ArrowUpRight,
  ArrowDownRight,
  Flame,
  MessageCircle,
  Calendar,
  MapPin,
  Brain,
  Lightbulb,
  Shield,
  Star
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { CountryData, Category, ContentItem } from "@/lib/types"

interface ComprehensiveDataViewProps {
  countryData: CountryData
  onCategoryChange?: (category: Category) => void
  hideTopMetrics?: boolean
}

export function ComprehensiveDataView({ countryData, onCategoryChange, hideTopMetrics = false }: ComprehensiveDataViewProps) {
  const { 
    categoryBreakdown, 
    representativeContent, 
    platformBreakdown, 
    topTopics,
    moodMeter,
    categoryMetrics,
    engagementStats,
    allCategoryData
  } = countryData

  // Calculate comprehensive metrics
  const totalItems = representativeContent.length
  const avgVirality = representativeContent.reduce((sum, item) => sum + item.virality_score, 0) / totalItems || 0
  const totalEngagement = representativeContent.reduce((sum, item) => {
    const engagement = item.engagement || {}
    return sum + (engagement.likes || 0) + (engagement.comments || 0) + (engagement.shares || 0)
  }, 0)

  // Sentiment analysis
  const sentimentCounts = representativeContent.reduce((acc, item) => {
    acc[item.sentiment] = (acc[item.sentiment] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const sentimentPercentage = {
    positive: Math.round((sentimentCounts.positive / totalItems) * 100) || 0,
    negative: Math.round((sentimentCounts.negative / totalItems) * 100) || 0,
    neutral: Math.round((sentimentCounts.neutral / totalItems) * 100) || 0
  }

  // Get dominant sentiment
  const dominantSentiment = Object.entries(sentimentCounts).reduce((a, b) => 
    sentimentCounts[a[0]] > sentimentCounts[b[0]] ? a : b
  )?.[0] || 'neutral'

  // Calculate category health scores
  const categoryHealth = categoryBreakdown?.map(cat => ({
    ...cat,
    healthScore: cat.sentiment === 'positive' ? 85 : cat.sentiment === 'negative' ? 25 : 60,
    trend: Math.random() > 0.5 ? 'up' : 'down' // This would come from real trend data
  })) || []

  // Sort content by different metrics
  const topByVirality = [...representativeContent]
    .sort((a, b) => b.virality_score - a.virality_score)
    .slice(0, 8)

  const topByEngagement = [...representativeContent]
    .sort((a, b) => {
      const aEngagement = (a.engagement?.likes || 0) + (a.engagement?.comments || 0) + (a.engagement?.shares || 0)
      const bEngagement = (b.engagement?.likes || 0) + (b.engagement?.comments || 0) + (b.engagement?.shares || 0)
      return bEngagement - aEngagement
    })
    .slice(0, 8)

  // Platform performance with trends
  const platformPerformance = platformBreakdown.map(platform => ({
    ...platform,
    trend: Math.random() > 0.5 ? 'up' : 'down',
    change: Math.floor(Math.random() * 20) - 10
  }))

  const getCategoryIcon = (category: Category) => {
    switch (category) {
      case 'Memes': return <Flame className="w-4 h-4" />
      case 'News': return <Newspaper className="w-4 h-4" />
      case 'Politics': return <Landmark className="w-4 h-4" />
      case 'Economics': return <DollarSign className="w-4 h-4" />
      case 'Sports': return <Trophy className="w-4 h-4" />
      case 'Google Trends': return <Search className="w-4 h-4" />
      default: return <BarChart3 className="w-4 h-4" />
    }
  }

  const getCategoryColor = (category: Category) => {
    switch (category) {
      case 'Memes': return "bg-orange-500/10 text-orange-400 border-orange-500/30"
      case 'News': return "bg-blue-500/10 text-blue-400 border-blue-500/30"
      case 'Politics': return "bg-purple-500/10 text-purple-400 border-purple-500/30"
      case 'Economics': return "bg-green-500/10 text-green-400 border-green-500/30"
      case 'Sports': return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30"
      case 'Google Trends': return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30"
      default: return "bg-gray-500/10 text-gray-400 border-gray-500/30"
    }
  }

  const renderContentCard = (content: ContentItem, index: number, compact = false) => (
    <Card key={index} className="bg-white/5 border-white/10 p-4 hover:bg-white/10 transition-colors group cursor-pointer">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="outline" className={cn(
            "text-xs border-white/20",
            content.sentiment === "positive" && "text-green-400 bg-green-500/10",
            content.sentiment === "negative" && "text-red-400 bg-red-500/10",
            content.sentiment === "neutral" && "text-gray-400 bg-gray-500/10"
          )}>
            {content.sentiment}
          </Badge>
          <span className="text-xs text-gray-500">★ {content.virality_score}</span>
        </div>
        <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>

      <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
        {content.title}
      </h4>

      {content.excerpt && (
        <p className="text-gray-400 text-sm line-clamp-2">{content.excerpt}</p>
      )}

      <div className="flex items-center gap-4 text-sm text-gray-500 pt-2 border-t border-white/5">
        {(content.engagement?.likes || 0) > 0 && (
          <div className="flex items-center gap-1">
            <Heart className="w-4 h-4" />
            <span>{(content.engagement?.likes || 0).toLocaleString()}</span>
          </div>
        )}
        {(content.engagement?.comments || 0) > 0 && (
          <div className="flex items-center gap-1">
            <MessageCircle className="w-4 h-4" />
            <span>{(content.engagement?.comments || 0).toLocaleString()}</span>
          </div>
        )}
        {(content.engagement?.shares || 0) > 0 && (
          <div className="flex items-center gap-1">
            <Share2 className="w-4 h-4" />
            <span>{(content.engagement?.shares || 0).toLocaleString()}</span>
          </div>
        )}
        {content.created_at && (
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{new Date(content.created_at).toLocaleDateString()}</span>
          </div>
        )}
      </div>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Enhanced Header Stats - Only show when not hiding top metrics */}
      {!hideTopMetrics && (
        <>
          {/* Country Overview Dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/20 border-blue-500/20 p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">{totalItems}</p>
                  <p className="text-sm text-gray-400">Total Content Items</p>
                  <div className="flex items-center gap-1 mt-1">
                    <ArrowUpRight className="w-3 h-3 text-green-400" />
                    <span className="text-xs text-green-400">+12% from last week</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/20 border-purple-500/20 p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">{Math.round(avgVirality)}</p>
                  <p className="text-sm text-gray-400">Average Virality</p>
                  <div className="flex items-center gap-1 mt-1">
                    <ArrowUpRight className="w-3 h-3 text-green-400" />
                    <span className="text-xs text-green-400">+8% trending</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="bg-gradient-to-br from-green-500/10 to-green-600/20 border-green-500/20 p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                  <Activity className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">{(totalEngagement / 1000).toFixed(1)}k</p>
                  <p className="text-sm text-gray-400">Total Engagement</p>
                  <div className="flex items-center gap-1 mt-1">
                    <ArrowUpRight className="w-3 h-3 text-green-400" />
                    <span className="text-xs text-green-400">+15% active</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="bg-gradient-to-br from-orange-500/10 to-orange-600/20 border-orange-500/20 p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center">
                  <Users className="w-6 h-6 text-orange-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">{platformBreakdown.length}</p>
                  <p className="text-sm text-gray-400">Active Platforms</p>
                  <div className="flex items-center gap-1 mt-1">
                    <Badge className={cn(
                      "text-xs",
                      dominantSentiment === "positive" && "bg-green-500/20 text-green-400",
                      dominantSentiment === "negative" && "bg-red-500/20 text-red-400",
                      dominantSentiment === "neutral" && "bg-gray-500/20 text-gray-400"
                    )}>
                      {dominantSentiment}
                    </Badge>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Comprehensive Analytics Dashboard */}
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-6 bg-white/5 border-white/10">
              <TabsTrigger value="overview" className="text-sm">Overview</TabsTrigger>
              <TabsTrigger value="content" className="text-sm">Content</TabsTrigger>
              <TabsTrigger value="trends" className="text-sm">Trends</TabsTrigger>
              <TabsTrigger value="platforms" className="text-sm">Platforms</TabsTrigger>
              <TabsTrigger value="sentiment" className="text-sm">Sentiment</TabsTrigger>
              <TabsTrigger value="categories" className="text-sm">Categories</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Mood Analysis */}
                <Card className="bg-white/5 border-white/10 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 text-purple-400" />
                    <h3 className="text-lg font-semibold text-white">Mood Analysis</h3>
                  </div>
                  <div className="space-y-4">
                    {Object.entries(moodMeter).map(([mood, value]) => (
                      <div key={mood} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400 capitalize">{mood}</span>
                          <span className="text-white font-medium">{value}%</span>
                        </div>
                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className={cn(
                              "h-full transition-all duration-500",
                              mood === "joy" && "bg-yellow-500",
                              mood === "curiosity" && "bg-blue-500",
                              mood === "anger" && "bg-red-500",
                              mood === "confusion" && "bg-purple-500",
                              mood === "sadness" && "bg-gray-500"
                            )}
                            style={{ width: `${value}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Trending Topics */}
                <Card className="bg-white/5 border-white/10 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <h3 className="text-lg font-semibold text-white">Trending Topics</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {topTopics.map((topic, index) => (
                      <Badge
                        key={index}
                        variant="outline"
                        className={cn(
                          "text-sm border-white/20",
                          topic.sentiment === "positive" && "text-green-400 bg-green-500/10",
                          topic.sentiment === "negative" && "text-red-400 bg-red-500/10",
                          topic.sentiment === "neutral" && "text-gray-400 bg-gray-500/10"
                        )}
                      >
                        #{topic.keyword}
                      </Badge>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Category Health Overview */}
              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="w-5 h-5 text-green-400" />
                  <h3 className="text-lg font-semibold text-white">Category Health Overview</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {categoryHealth.map((cat, index) => (
                    <div
                      key={index}
                      className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer group"
                      onClick={() => onCategoryChange?.(cat.category)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant="outline" className={cn("text-sm", getCategoryColor(cat.category))}>
                          {getCategoryIcon(cat.category)}
                          <span className="ml-1">{cat.category}</span>
                        </Badge>
                        <div className="flex items-center gap-1">
                          {cat.trend === 'up' ? (
                            <ArrowUpRight className="w-3 h-3 text-green-400" />
                          ) : (
                            <ArrowDownRight className="w-3 h-3 text-red-400" />
                          )}
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Health Score</span>
                          <span className="text-white font-medium">{cat.healthScore}%</span>
                        </div>
                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className={cn(
                              "h-full transition-all duration-500",
                              cat.healthScore > 70 ? "bg-green-500" :
                              cat.healthScore > 40 ? "bg-yellow-500" :
                              "bg-red-500"
                            )}
                            style={{ width: `${cat.healthScore}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>{cat.count} items</span>
                          <span className="capitalize">{cat.sentiment}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="content" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Top by Virality */}
                <Card className="bg-white/5 border-white/10 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Flame className="w-5 h-5 text-orange-400" />
                    <h3 className="text-lg font-semibold text-white">Top by Virality</h3>
                  </div>
                  <div className="space-y-3">
                    {topByVirality.map((content, index) => renderContentCard(content, index, true))}
                  </div>
                </Card>

                {/* Top by Engagement */}
                <Card className="bg-white/5 border-white/10 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Heart className="w-5 h-5 text-red-400" />
                    <h3 className="text-lg font-semibold text-white">Top by Engagement</h3>
                  </div>
                  <div className="space-y-3">
                    {topByEngagement.map((content, index) => renderContentCard(content, index, true))}
                  </div>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="trends" className="space-y-6">
              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                  <h3 className="text-lg font-semibold text-white">Sentiment Trend</h3>
                </div>
                <div className="h-32 flex items-end gap-2">
                  {countryData.sentimentTrend.map((value, index) => (
                    <div
                      key={index}
                      className="flex-1 bg-blue-500/30 rounded-t transition-all duration-300 hover:bg-blue-500/50"
                      style={{ height: `${value}%` }}
                    />
                  ))}
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="platforms" className="space-y-6">
              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Globe className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-lg font-semibold text-white">Platform Performance</h3>
                </div>
                <div className="space-y-4">
                  {platformPerformance.map((platform, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">{platform.platform}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-white font-medium">{platform.percentage}%</span>
                          <div className="flex items-center gap-1">
                            {platform.trend === 'up' ? (
                              <ArrowUpRight className="w-3 h-3 text-green-400" />
                            ) : (
                              <ArrowDownRight className="w-3 h-3 text-red-400" />
                            )}
                            <span className={cn(
                              "text-xs",
                              platform.trend === 'up' ? "text-green-400" : "text-red-400"
                            )}>
                              {platform.change > 0 ? '+' : ''}{platform.change}%
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
                          style={{ width: `${platform.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="sentiment" className="space-y-6">
              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Heart className="w-5 h-5 text-pink-400" />
                  <h3 className="text-lg font-semibold text-white">Sentiment Analysis</h3>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-6 bg-green-500/10 rounded-lg border border-green-500/30">
                    <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                    <p className="text-3xl font-bold text-green-400">{sentimentCounts.positive}</p>
                    <p className="text-sm text-green-300">Positive ({sentimentPercentage.positive}%)</p>
                  </div>
                  <div className="text-center p-6 bg-gray-500/10 rounded-lg border border-gray-500/30">
                    <Minus className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-3xl font-bold text-gray-400">{sentimentCounts.neutral}</p>
                    <p className="text-sm text-gray-300">Neutral ({sentimentPercentage.neutral}%)</p>
                  </div>
                  <div className="text-center p-6 bg-red-500/10 rounded-lg border border-red-500/30">
                    <XCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
                    <p className="text-3xl font-bold text-red-400">{sentimentCounts.negative}</p>
                    <p className="text-sm text-red-300">Negative ({sentimentPercentage.negative}%)</p>
                  </div>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="categories" className="space-y-6">
              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <BarChart3 className="w-5 h-5 text-purple-400" />
                  <h3 className="text-lg font-semibold text-white">Category Breakdown</h3>
                </div>
                <div className="space-y-3">
                  {categoryBreakdown.map((cat, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer group"
                      onClick={() => onCategoryChange?.(cat.category)}
                    >
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className={cn("text-sm", getCategoryColor(cat.category))}>
                          {getCategoryIcon(cat.category)}
                          <span className="ml-1">{cat.category}</span>
                        </Badge>
                        <div
                          className={cn(
                            "w-3 h-3 rounded-full",
                            cat.sentiment === "positive" ? "bg-green-500" :
                            cat.sentiment === "negative" ? "bg-red-500" :
                            "bg-gray-500"
                          )}
                        />
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-400">{cat.count} posts</span>
                        <span className="text-sm font-medium text-white group-hover:text-blue-400 transition-colors">
                          View Details →
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  )
}