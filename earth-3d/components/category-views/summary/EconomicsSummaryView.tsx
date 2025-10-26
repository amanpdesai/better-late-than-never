"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Newspaper } from "lucide-react"
import { cn } from "@/lib/utils"
import type { EconomicsData } from "@/lib/types"

interface EconomicsSummaryViewProps {
  data: EconomicsData
}

export function EconomicsSummaryView({ data }: EconomicsSummaryViewProps) {
  const { economic_indicators, market_data, news_headlines, sentiment } = data

  return (
    <div className="space-y-2">
      {/* Key Economic Indicators - Compact */}
      {economic_indicators && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-3 h-3 text-blue-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Key Indicators</h3>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {/* GDP Growth */}
            {economic_indicators.gdp_growth && (
              <div className="p-2 bg-white/5 rounded border border-white/10">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs text-gray-400">GDP</p>
                  {economic_indicators.gdp_growth.value > 0 ? (
                    <TrendingUp className="w-3 h-3 text-green-400" />
                  ) : (
                    <TrendingDown className="w-3 h-3 text-red-400" />
                  )}
                </div>
                <p className={cn(
                  "text-lg font-bold",
                  economic_indicators.gdp_growth.value > 0 ? "text-green-400" : "text-red-400"
                )}>
                  {economic_indicators.gdp_growth.value > 0 ? "+" : ""}{economic_indicators.gdp_growth.value}%
                </p>
              </div>
            )}

            {/* Inflation Rate */}
            {economic_indicators.inflation_rate && (
              <div className="p-2 bg-white/5 rounded border border-white/10">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs text-gray-400">Inflation</p>
                  {economic_indicators.inflation_rate.value > 3 ? (
                    <TrendingUp className="w-3 h-3 text-red-400" />
                  ) : (
                    <TrendingDown className="w-3 h-3 text-green-400" />
                  )}
                </div>
                <p className={cn(
                  "text-lg font-bold",
                  economic_indicators.inflation_rate.value > 3 ? "text-red-400" : "text-yellow-400"
                )}>
                  {economic_indicators.inflation_rate.value}%
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Top Market Gainers - Compact */}
      {market_data?.top_gainers && market_data.top_gainers.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-3 h-3 text-green-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Top Gainers</h3>
          </div>
          <div className="space-y-1">
            {market_data.top_gainers.slice(0, 3).map((stock, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10"
              >
                <div className="flex items-center gap-2">
                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30 text-xs">
                    {stock.symbol}
                  </Badge>
                  <span className="text-white text-xs font-medium truncate">{stock.name}</span>
                </div>
                <span className="text-green-400 font-semibold text-xs">+{stock.change_pct}%</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Latest Economic News - Compact */}
      {news_headlines && news_headlines.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Newspaper className="w-3 h-3 text-blue-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Latest News</h3>
          </div>
          <div className="space-y-1">
            {news_headlines.slice(0, 2).map((item, index) => (
              <div
                key={index}
                className="p-2 bg-white/5 rounded border border-white/10"
              >
                <p className="text-white text-xs leading-relaxed line-clamp-2">
                  {item.headline}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-xs text-gray-500">{item.source}</p>
                  {item.sentiment && (
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-xs",
                        item.sentiment === "positive" && "bg-green-500/10 text-green-400 border-green-500/30",
                        item.sentiment === "negative" && "bg-red-500/10 text-red-400 border-red-500/30",
                        item.sentiment === "neutral" && "bg-gray-500/10 text-gray-400 border-gray-500/30"
                      )}
                    >
                      {item.sentiment}
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Overall Sentiment */}
      {sentiment && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Overall Sentiment</span>
            <Badge
              variant="outline"
              className={cn(
                "text-xs",
                sentiment.overall === "positive" && "bg-green-500/10 text-green-400 border-green-500/30",
                sentiment.overall === "negative" && "bg-red-500/10 text-red-400 border-red-500/30",
                sentiment.overall === "neutral" && "bg-gray-500/10 text-gray-400 border-gray-500/30"
              )}
            >
              {sentiment.overall} ({sentiment.score}/100)
            </Badge>
          </div>
        </Card>
      )}
    </div>
  )
}
