"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Video, MessageSquare, TrendingUp, ExternalLink, Play } from "lucide-react"
import { cn } from "@/lib/utils"
import type { MemesData } from "@/lib/types"

interface MemesViewProps {
  data: MemesData
}

export function MemesView({ data }: MemesViewProps) {
  const { items } = data

  if (!items || items.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-5">
        <p className="text-gray-400 text-center">No memes available</p>
      </Card>
    )
  }

  // Calculate platform breakdown from items
  const redditItems = items.filter(item => item.source_platform === 'reddit')
  const youtubeItems = items.filter(item => item.source_platform === 'youtube')
  const totalPosts = items.length
  const redditCount = redditItems.length
  const youtubeCount = youtubeItems.length

  // Sort by virality score
  const sortedItems = [...items].sort((a, b) => b.virality_score - a.virality_score)

  return (
    <div className="space-y-4">
      {/* Platform Stats */}
      <Card className="bg-white/5 border-white/10 p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-semibold text-white uppercase">Platform Breakdown</h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-3 bg-white/5 rounded-lg">
            <p className="text-2xl font-bold text-white">{totalPosts}</p>
            <p className="text-xs text-gray-400 mt-1">Total Memes</p>
          </div>
          <div className="text-center p-3 bg-orange-500/10 rounded-lg border border-orange-500/30">
            <p className="text-2xl font-bold text-orange-400">{redditCount}</p>
            <p className="text-xs text-orange-300 mt-1">Reddit Posts</p>
          </div>
          <div className="text-center p-3 bg-red-500/10 rounded-lg border border-red-500/30">
            <p className="text-2xl font-bold text-red-400">{youtubeCount}</p>
            <p className="text-xs text-red-300 mt-1">YouTube Videos</p>
          </div>
        </div>
      </Card>

      {/* Combined Content Feed */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-white uppercase">Trending Memes</h3>
        {combinedContent.slice(0, 15).map((item, index) => {
          const isReddit = item.platform === 'reddit'
          const engagement = isReddit
            ? { upvotes: item.upvotes, comments: item.comments }
            : { likes: item.likes, comments: item.comments }

          return (
            <Card
              key={`${item.platform}-${index}`}
              className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group"
            >
              <div className="p-4 space-y-3">
                {/* Header with platform badge */}
                <div className="flex items-center gap-2 flex-wrap">
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
                        <MessageSquare className="w-3 h-3 mr-1" />
                        Reddit
                      </>
                    ) : (
                      <>
                        <Video className="w-3 h-3 mr-1" />
                        YouTube
                      </>
                    )}
                  </Badge>

                  {isReddit && item.subreddit && (
                    <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                      r/{item.subreddit}
                    </Badge>
                  )}

                  {!isReddit && item.channel && (
                    <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                      {item.channel}
                    </Badge>
                  )}
                </div>

                {/* Title */}
                <h4 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                  {item.title}
                </h4>

                {/* Engagement Stats */}
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  {isReddit ? (
                    <>
                      {item.upvotes !== undefined && (
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          <span className="text-gray-400">{item.upvotes.toLocaleString()}</span> upvotes
                        </span>
                      )}
                      {item.comments !== undefined && (
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          <span className="text-gray-400">{item.comments.toLocaleString()}</span> comments
                        </span>
                      )}
                    </>
                  ) : (
                    <>
                      {item.likes !== undefined && (
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          <span className="text-gray-400">{item.likes.toLocaleString()}</span> likes
                        </span>
                      )}
                      {item.comments !== undefined && (
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          <span className="text-gray-400">{item.comments.toLocaleString()}</span> comments
                        </span>
                      )}
                    </>
                  )}
                </div>

                {/* Link */}
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-gray-500 hover:text-blue-400 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span className="truncate">View on {isReddit ? 'Reddit' : 'YouTube'}</span>
                  </a>
                )}
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
