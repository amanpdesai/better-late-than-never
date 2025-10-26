"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Video, MessageSquare, TrendingUp, ExternalLink, Play, Heart } from "lucide-react"
import { cn } from "@/lib/utils"
import type { MemesData } from "@/lib/types"

interface MemesSummaryViewProps {
  data: MemesData
}

export function MemesSummaryView({ data }: MemesSummaryViewProps) {
  const { items, summary } = data

  if (!items || items.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-3">
        <p className="text-gray-400 text-center text-xs">No memes available</p>
      </Card>
    )
  }

  // Calculate platform breakdown from items
  const redditItems = items.filter(item => item.source_platform === 'reddit')
  const youtubeItems = items.filter(item => item.source_platform === 'youtube')
  const totalPosts = items.length
  const redditCount = redditItems.length
  const youtubeCount = youtubeItems.length

  // Calculate sentiment breakdown
  const sentimentCounts = items.reduce((acc, item) => {
    acc[item.sentiment] = (acc[item.sentiment] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // Sort by virality score
  const sortedItems = [...items].sort((a, b) => b.virality_score - a.virality_score)

  return (
    <div className="space-y-2">
      {/* Platform Stats - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-3 h-3 text-purple-400" />
          <h3 className="text-xs font-semibold text-white uppercase">Platforms</h3>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="text-center p-2 bg-orange-500/10 rounded border border-orange-500/30">
            <p className="text-lg font-bold text-orange-400">{redditCount}</p>
            <p className="text-xs text-orange-300">Reddit</p>
          </div>
          <div className="text-center p-2 bg-red-500/10 rounded border border-red-500/30">
            <p className="text-lg font-bold text-red-400">{youtubeCount}</p>
            <p className="text-xs text-red-300">YouTube</p>
          </div>
        </div>
      </Card>

      {/* Sentiment Overview - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center gap-2 mb-2">
          <Heart className="w-3 h-3 text-pink-400" />
          <h3 className="text-xs font-semibold text-white uppercase">Sentiment</h3>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div className="text-center p-2 bg-green-500/10 rounded border border-green-500/30">
            <p className="text-lg font-bold text-green-400">{sentimentCounts.positive || 0}</p>
            <p className="text-xs text-green-300">Positive</p>
          </div>
          <div className="text-center p-2 bg-gray-500/10 rounded border border-gray-500/30">
            <p className="text-lg font-bold text-gray-400">{sentimentCounts.neutral || 0}</p>
            <p className="text-xs text-gray-300">Neutral</p>
          </div>
          <div className="text-center p-2 bg-red-500/10 rounded border border-red-500/30">
            <p className="text-lg font-bold text-red-400">{sentimentCounts.negative || 0}</p>
            <p className="text-xs text-red-300">Negative</p>
          </div>
        </div>
      </Card>

      {/* Top Memes - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-white uppercase">Top Memes</h3>
          <Badge className="bg-purple-600/20 text-purple-300 border-purple-500/30 text-xs">
            {items.length}
          </Badge>
        </div>

        <div className="space-y-1">
          {sortedItems.slice(0, 10).map((item, index) => {
            const isReddit = item.source_platform === 'reddit'
            const isVideo = item.is_video || item.source_platform === 'youtube'

            return (
              <div
                key={`${item.source_platform}-${index}`}
                className="p-2 bg-white/5 rounded border border-white/10 hover:bg-white/10 transition-colors group"
              >
                {/* Header with platform badge */}
                <div className="flex items-center gap-1 flex-wrap mb-1">
                  <Badge
                    variant="outline"
                    className={cn(
                      "text-xs border-white/20",
                      isReddit
                        ? "bg-orange-500/10 text-orange-400 border-orange-500/30"
                        : "bg-red-500/10 text-red-400 border-red-500/30"
                    )}
                  >
                    {isReddit ? (
                      <>
                        <MessageSquare className="w-2 h-2 mr-1" />
                        Reddit
                      </>
                    ) : (
                      <>
                        <Video className="w-2 h-2 mr-1" />
                        YouTube
                      </>
                    )}
                  </Badge>

                  <Badge
                    variant="outline"
                    className={cn(
                      "text-xs border-white/20",
                      item.sentiment === "positive" && "text-green-400 bg-green-500/10",
                      item.sentiment === "negative" && "text-red-400 bg-red-500/10",
                      item.sentiment === "neutral" && "text-gray-400 bg-gray-500/10"
                    )}
                  >
                    {item.sentiment}
                  </Badge>

                  <span className="text-xs text-gray-500 ml-auto">★ {item.virality_score}</span>
                </div>

                {/* Media Preview - Small */}
                {(item.media?.thumbnail || item.media?.images?.[0]) && (
                  <div className="relative h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded overflow-hidden mb-1">
                    <img
                      src={item.media.thumbnail || item.media.images?.[0]}
                      alt={item.title}
                      className="w-full h-full object-cover"
                    />
                    {isVideo && (
                      <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                        <div className="w-6 h-6 rounded-full bg-red-600 flex items-center justify-center">
                          <Play className="w-3 h-3 text-white ml-0.5" fill="white" />
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Title */}
                <h4 className="text-white text-xs font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-1">
                  {item.title}
                </h4>

                {/* Engagement Stats - Compact */}
                <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                  {(item.engagement?.likes || 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-2 h-2" />
                      <span className="text-gray-400">{(item.engagement?.likes || 0).toLocaleString()}</span>
                    </span>
                  )}
                  {(item.engagement?.comments || 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-2 h-2" />
                      <span className="text-gray-400">{(item.engagement?.comments || 0).toLocaleString()}</span>
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>
    </div>
  )
}
