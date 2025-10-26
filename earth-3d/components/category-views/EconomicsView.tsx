"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Newspaper } from "lucide-react"
import { cn } from "@/lib/utils"
import type { EconomicsData } from "@/lib/types"

interface EconomicsViewProps {
  data: EconomicsData
}

export function EconomicsView({ data }: EconomicsViewProps) {
  const { economic_indicators, market_data, news_headlines } = data

  return (
    <div className="space-y-4">
      {/* Economic Indicators */}
      {economic_indicators && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Economic Indicators</h3>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* GDP Growth */}
            {economic_indicators.gdp_growth && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs text-gray-400 uppercase">GDP Growth</p>
                  {economic_indicators.gdp_growth.value > 0 ? (
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-400" />
                  )}
                </div>
                <p className={cn(
                  "text-2xl font-bold",
                  economic_indicators.gdp_growth.value > 0 ? "text-green-400" : "text-red-400"
                )}>
                  {economic_indicators.gdp_growth.value > 0 ? "+" : ""}{economic_indicators.gdp_growth.value}%
                </p>
              </div>
            )}

            {/* Inflation Rate */}
            {economic_indicators.inflation_rate && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs text-gray-400 uppercase">Inflation</p>
                  {economic_indicators.inflation_rate.value > 3 ? (
                    <TrendingUp className="w-4 h-4 text-red-400" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-green-400" />
                  )}
                </div>
                <p className={cn(
                  "text-2xl font-bold",
                  economic_indicators.inflation_rate.value > 3 ? "text-red-400" : "text-yellow-400"
                )}>
                  {economic_indicators.inflation_rate.value}%
                </p>
              </div>
            )}

            {/* Unemployment Rate */}
            {economic_indicators.unemployment_rate && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs text-gray-400 uppercase">Unemployment</p>
                  {economic_indicators.unemployment_rate.value > 5 ? (
                    <TrendingUp className="w-4 h-4 text-red-400" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-green-400" />
                  )}
                </div>
                <p className={cn(
                  "text-2xl font-bold",
                  economic_indicators.unemployment_rate.value > 5 ? "text-red-400" : "text-green-400"
                )}>
                  {economic_indicators.unemployment_rate.value}%
                </p>
              </div>
            )}

            {/* Stock Index */}
            {economic_indicators.stock_index && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs text-gray-400 uppercase">{economic_indicators.stock_index.name}</p>
                  <DollarSign className="w-4 h-4 text-blue-400" />
                </div>
                <p className="text-2xl font-bold text-blue-400">
                  {economic_indicators.stock_index.value.toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Market Data - Top Gainers */}
      {market_data?.top_gainers && market_data.top_gainers.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Top Gainers</h3>
          </div>
          <div className="space-y-2">
            {market_data.top_gainers.map((stock, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
                    {stock.symbol}
                  </Badge>
                  <span className="text-white text-sm font-medium">{stock.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-400 font-semibold">+{stock.change_pct}%</span>
                  <TrendingUp className="w-4 h-4 text-green-400" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Economic News Headlines */}
      {news_headlines && news_headlines.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Newspaper className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Economic News</h3>
          </div>
          <div className="space-y-3">
            {news_headlines.map((item, index) => (
              <a
                key={index}
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors group"
              >
                <p className="text-white text-sm leading-relaxed group-hover:text-blue-400 transition-colors">
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
              </a>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
