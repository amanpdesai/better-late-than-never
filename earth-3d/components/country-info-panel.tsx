"use client"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { X, ArrowRight, BarChart3, TrendingUp, TrendingDown, Eye, ExternalLink, Building2, Landmark } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import type { CountryData, Category } from "@/lib/types"
import { PoliticsSummaryView } from "@/components/category-views/summary/PoliticsSummaryView"
import { EconomicsSummaryView } from "@/components/category-views/summary/EconomicsSummaryView"
import { MemesSummaryView } from "@/components/category-views/summary/MemesSummaryView"
import { NewsSummaryView } from "@/components/category-views/summary/NewsSummaryView"
import { SportsSummaryView } from "@/components/category-views/summary/SportsSummaryView"
import { GoogleTrendsSummaryView } from "@/components/category-views/summary/GoogleTrendsSummaryView"
import { DataSummary } from "@/components/data-summary"

interface CountryInfoPanelProps {
  countryData: CountryData | null
  onClose: () => void
  category?: Category
  onCategoryChange?: (category: Category) => void
  showFullPageLink?: boolean
  isOpen?: boolean
}

const CATEGORIES: Category[] = ["All", "Memes", "News", "Politics", "Economics", "Sports", "Google Trends"]

export function CountryInfoPanel({
  countryData,
  onClose,
  category = "All",
  onCategoryChange,
  showFullPageLink = true,
  isOpen = false,
}: CountryInfoPanelProps) {
  if (!countryData) {
    return (
      <div
        className={cn(
          "fixed right-0 top-0 h-full w-full md:w-[480px] bg-black/95 border-l border-white/20 shadow-2xl overflow-y-auto transition-transform duration-300 z-40",
          isOpen ? "translate-x-0" : "translate-x-full",
        )}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Loading...</h2>
            <Button variant="ghost" size="icon" onClick={onClose} className="text-white hover:bg-white/10">
              <X className="w-5 h-5" />
            </Button>
          </div>
          <div className="flex items-center justify-center h-64">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        </div>
      </div>
    )
  }

  const countrySlug = countryData.name.toLowerCase().replace(/\s+/g, "-")

  return (
    <div
      className={cn(
        "fixed right-0 top-0 h-full w-full md:w-[480px] bg-black/95 border-l border-white/20 shadow-2xl overflow-y-auto transition-transform duration-300 z-40",
        isOpen ? "translate-x-0" : "translate-x-full",
      )}
    >
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <span className="text-5xl">{countryData.flag}</span>
            <div>
              <h2 className="text-2xl font-bold text-white">{countryData.name}</h2>
              <p className="text-sm text-gray-400">{countryData.lastUpdated}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {showFullPageLink && (
              <Link href={`/country/${countrySlug}?category=${category}`}>
                <Button variant="ghost" size="icon" className="text-white hover:bg-white/10 hover:text-blue-300">
                  <Eye className="w-5 h-5" />
                </Button>
              </Link>
            )}
            <Button variant="ghost" size="icon" onClick={onClose} className="text-white hover:bg-white/10 hover:text-white">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Category Filters */}
        {onCategoryChange && (
          <div className="space-y-3">
            <h3 className="text-xs font-semibold text-gray-400 uppercase">Filter by Category</h3>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => (
                <Button
                  key={cat}
                  variant={category === cat ? "default" : "outline"}
                  size="sm"
                  onClick={() => onCategoryChange(cat)}
                  className={cn(
                    "text-xs",
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
        )}

        {/* Overview Stats - Only show when "All" is selected */}
        {category === "All" && (
          <Card className="bg-white/5 border-white/10 p-5">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-4 h-4 text-blue-400" />
              <h3 className="text-sm font-semibold text-white uppercase">Overview</h3>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <p className="text-2xl font-bold text-white">{countryData.categoryMetrics.totalPosts}</p>
                <p className="text-xs text-gray-400 mt-1">Posts</p>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <p className="text-2xl font-bold text-white">{countryData.categoryMetrics.viralityScore}</p>
                <p className="text-xs text-gray-400 mt-1">Virality</p>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <p className="text-2xl font-bold text-white">{countryData.categoryMetrics.avgEngagement.toFixed(1)}k</p>
                <p className="text-xs text-gray-400 mt-1">Engagement</p>
              </div>
            </div>
          </Card>
        )}

        {/* Category Breakdown - Only show when "All" is selected */}
        {category === "All" && countryData.categoryBreakdown && countryData.categoryBreakdown.length > 0 && (
          <Card className="bg-white/5 border-white/10 p-5">
            <h3 className="text-sm font-semibold text-white mb-4 uppercase">Category Breakdown</h3>
            <div className="space-y-2">
              {countryData.categoryBreakdown.map((cat, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer" onClick={() => onCategoryChange?.(cat.category)}>
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-2 h-2 rounded-full",
                      cat.sentiment === "positive" ? "bg-green-500" :
                      cat.sentiment === "negative" ? "bg-red-500" :
                      "bg-gray-500"
                    )} />
                    <span className="text-sm font-medium text-white">{cat.category}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-400">{cat.count} posts</span>
                    <Eye className="w-3 h-3 text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Mood Analysis - Only show when "All" is selected */}
        {category === "All" && (
          <Card className="bg-white/5 border-white/10 p-5">
            <h3 className="text-sm font-semibold text-white mb-3 uppercase">Mood Analysis</h3>
            <p className="text-gray-300 text-sm leading-relaxed mb-4">{countryData.moodSummary}</p>
            <div className="space-y-3">
              {Object.entries(countryData.moodMeter).map(([mood, value]) => (
                <div key={mood} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-white capitalize">{mood}</span>
                    <span className="text-gray-400">{value}%</span>
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
        )}

        {/* Top Topics - Only show when "All" is selected */}
        {category === "All" && (
          <Card className="bg-white/5 border-white/10 p-5">
            <h3 className="text-sm font-semibold text-white mb-4 uppercase">Trending Topics</h3>
            <div className="flex flex-wrap gap-2">
              {countryData.topTopics.map((topic, index) => (
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
        )}

        {/* Platform Distribution - Only show when "All" is selected */}
        {category === "All" && (
          <Card className="bg-white/5 border-white/10 p-5">
            <h3 className="text-sm font-semibold text-white mb-4 uppercase">Platform Distribution</h3>
            <div className="space-y-3">
              {countryData.platformBreakdown.map((platform, index) => (
                <div key={index} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-white">{platform.platform}</span>
                    <span className="text-gray-400">{platform.percentage}%</span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                      style={{ width: `${platform.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Category-Specific Content */}
        {category === "Politics" && countryData.categoryData ? (
          <PoliticsSummaryView data={countryData.categoryData as any} />
        ) : category === "Economics" && countryData.categoryData ? (
          <EconomicsSummaryView data={countryData.categoryData as any} />
        ) : category === "Memes" && countryData.categoryData ? (
          <MemesSummaryView data={countryData.categoryData as any} />
        ) : category === "News" && countryData.categoryData ? (
          <NewsSummaryView data={countryData.categoryData as any} />
        ) : category === "Sports" && countryData.categoryData ? (
          <SportsSummaryView data={countryData.categoryData as any} />
        ) : category === "Google Trends" && countryData.categoryData ? (
          <GoogleTrendsSummaryView data={countryData.categoryData as any} />
        ) : (
          /* Default view for "All" category - show data summary */
          <DataSummary countryData={countryData} onCategoryChange={onCategoryChange} />
        )}

        <div></div>

        {/* View Full Analysis Button */}
        {showFullPageLink && (
          <Link href={`/country/${countrySlug}?category=${category}`}>
            <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-lg group">
              View Full Analysis
              <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        )}
      </div>
    </div>
  )
}
