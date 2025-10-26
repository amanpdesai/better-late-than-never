"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
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
  Flame,
  Eye,
  ArrowUp,
  MessageCircle,
  Share2,
  Clock,
  Users,
  Activity,
  Globe,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Minus
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { CountryData, Category } from "@/lib/types"

interface DataSummaryProps {
  countryData: CountryData
  onCategoryChange?: (category: Category) => void
}

export function DataSummary({ countryData, onCategoryChange }: DataSummaryProps) {
  const { 
    categoryBreakdown, 
    representativeContent, 
    platformBreakdown, 
    topTopics,
    moodSummary,
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

  // Get dominant sentiment
  const dominantSentiment = Object.entries(sentimentCounts).reduce((a, b) => 
    sentimentCounts[a[0]] > sentimentCounts[b[0]] ? a : b
  )?.[0] || 'neutral'

  // Calculate category health scores
  const categoryHealth = categoryBreakdown?.map(cat => ({
    ...cat,
    healthScore: cat.sentiment === 'positive' ? 85 : cat.sentiment === 'negative' ? 25 : 60
  })) || []

  // Get top performing content
  const topContent = representativeContent
    .sort((a, b) => b.virality_score - a.virality_score)
    .slice(0, 3)

  // Platform performance
  const topPlatforms = platformBreakdown.slice(0, 3)

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <CheckCircle className="w-3 h-3 text-green-400" />
      case 'negative': return <XCircle className="w-3 h-3 text-red-400" />
      default: return <Minus className="w-3 h-3 text-gray-400" />
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return "text-green-400"
      case 'negative': return "text-red-400"
      default: return "text-gray-400"
    }
  }

  const getCategoryIcon = (category: Category) => {
    switch (category) {
      case 'Memes': return <Flame className="w-3 h-3" />
      case 'News': return <Newspaper className="w-3 h-3" />
      case 'Politics': return <Landmark className="w-3 h-3" />
      case 'Economics': return <DollarSign className="w-3 h-3" />
      case 'Sports': return <Trophy className="w-3 h-3" />
      case 'Google Trends': return <Search className="w-3 h-3" />
      default: return <BarChart3 className="w-3 h-3" />
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

  return (
    <div className="space-y-3">
      {/* Country Pulse - Enhanced Overview */}
      <Card className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center">
            <Activity className="w-3 h-3 text-blue-400" />
          </div>
          <h3 className="text-sm font-semibold text-white uppercase">Country Pulse</h3>
          <Badge className={cn(
            "text-xs border-white/20",
            dominantSentiment === "positive" && "bg-green-500/10 text-green-400",
            dominantSentiment === "negative" && "bg-red-500/10 text-red-400",
            dominantSentiment === "neutral" && "bg-gray-500/10 text-gray-400"
          )}>
            {getSentimentIcon(dominantSentiment)}
            <span className="ml-1 capitalize">{dominantSentiment}</span>
          </Badge>
        </div>
        
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-2 bg-white/5 rounded-lg border border-white/10">
            <p className="text-lg font-bold text-white">{totalItems}</p>
            <p className="text-xs text-gray-400">Total Items</p>
          </div>
          <div className="text-center p-2 bg-white/5 rounded-lg border border-white/10">
            <p className="text-lg font-bold text-white">{Math.round(avgVirality)}</p>
            <p className="text-xs text-gray-400">Avg Virality</p>
          </div>
          <div className="text-center p-2 bg-white/5 rounded-lg border border-white/10">
            <p className="text-lg font-bold text-white">{(totalEngagement / 1000).toFixed(1)}k</p>
            <p className="text-xs text-gray-400">Engagement</p>
          </div>
        </div>

        {/* Mood Summary */}
        <div className="mt-3 p-2 bg-white/5 rounded-lg border border-white/10">
          <p className="text-gray-300 text-xs leading-relaxed line-clamp-2">
            {moodSummary}
          </p>
        </div>
      </Card>

      {/* Category Health Dashboard */}
      <Card className="bg-white/5 border-white/10 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center">
            <Target className="w-3 h-3 text-green-400" />
          </div>
          <h3 className="text-sm font-semibold text-white uppercase">Category Health</h3>
        </div>
        
        <div className="space-y-2">
          {categoryHealth.slice(0, 4).map((cat, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer group"
              onClick={() => onCategoryChange?.(cat.category)}
            >
              <div className="flex items-center gap-2">
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  cat.healthScore > 70 ? "bg-green-500" :
                  cat.healthScore > 40 ? "bg-yellow-500" :
                  "bg-red-500"
                )} />
                <Badge variant="outline" className={cn("text-xs", getCategoryColor(cat.category))}>
                  {getCategoryIcon(cat.category)}
                  <span className="ml-1">{cat.category}</span>
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{cat.count}</span>
                <span className={cn("text-xs font-medium", getSentimentColor(cat.sentiment))}>
                  {cat.healthScore}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Platform Performance */}
      <Card className="bg-white/5 border-white/10 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center">
            <TrendingUp className="w-3 h-3 text-purple-400" />
          </div>
          <h3 className="text-sm font-semibold text-white uppercase">Top Platforms</h3>
        </div>
        
        <div className="space-y-2">
          {topPlatforms.map((platform, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-white/5 rounded-lg border border-white/10">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-purple-500" />
                <span className="text-xs font-medium text-white">{platform.platform}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-16 h-1 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-500"
                    style={{ width: `${platform.percentage}%` }}
                  />
                </div>
                <span className="text-xs text-gray-400">{platform.percentage}%</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Trending Now */}
      <Card className="bg-white/5 border-white/10 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-full bg-yellow-500/20 flex items-center justify-center">
            <Zap className="w-3 h-3 text-yellow-400" />
          </div>
          <h3 className="text-sm font-semibold text-white uppercase">Trending Now</h3>
        </div>
        
        <div className="flex flex-wrap gap-1">
          {topTopics.slice(0, 6).map((topic, index) => (
            <Badge
              key={index}
              variant="outline"
              className={cn(
                "text-xs border-white/20",
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

      {/* Top Performing Content */}
      <Card className="bg-white/5 border-white/10 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-full bg-orange-500/20 flex items-center justify-center">
            <Flame className="w-3 h-3 text-orange-400" />
          </div>
          <h3 className="text-sm font-semibold text-white uppercase">Top Content</h3>
        </div>
        
        <div className="space-y-2">
          {topContent.map((content, index) => {
            const category = content.source_platform === 'reddit' ? 'Memes' : 
                           content.source_platform === 'espn' ? 'Sports' : 
                           content.source_platform === 'google_trends' ? 'Google Trends' : 
                           content.source_platform === 'youtube' ? 'Memes' : 'News'
            
            return (
              <div
                key={index}
                className="p-2 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors group cursor-pointer"
                onClick={() => onCategoryChange?.(category as Category)}
              >
                <div className="flex items-start gap-2">
                  <Badge variant="outline" className={cn("text-xs", getCategoryColor(category as Category))}>
                    {getCategoryIcon(category as Category)}
                    <span className="ml-1">{category}</span>
                  </Badge>
                  <span className="text-xs text-gray-500 ml-auto">★ {content.virality_score}</span>
                </div>
                <h4 className="text-white text-xs font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-1 mt-1">
                  {content.title}
                </h4>
                <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                  {(content.engagement?.likes || 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <Heart className="w-2 h-2" />
                      {((content.engagement?.likes || 0) / 1000).toFixed(1)}k
                    </span>
                  )}
                  {(content.engagement?.comments || 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-2 h-2" />
                      {((content.engagement?.comments || 0) / 1000).toFixed(1)}k
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="bg-white/5 border-white/10 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center">
            <Globe className="w-3 h-3 text-cyan-400" />
          </div>
          <h3 className="text-sm font-semibold text-white uppercase">Quick Access</h3>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          {categoryBreakdown?.slice(0, 4).map((cat, index) => (
            <Button
              key={index}
              variant="outline"
              size="sm"
              onClick={() => onCategoryChange?.(cat.category)}
              className={cn(
                "text-xs h-8 justify-start",
                getCategoryColor(cat.category)
              )}
            >
              {getCategoryIcon(cat.category)}
              <span className="ml-1">{cat.category}</span>
            </Button>
          ))}
        </div>
      </Card>
    </div>
  )
}