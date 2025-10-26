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
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <h3 className="text-lg font-semibold text-white uppercase">Top Market Gainers</h3>
            <Badge className="bg-green-600/20 text-green-300 border-green-500/30 text-xs">
              {market_data.top_gainers.length} stocks
            </Badge>
          </div>
          <div className="space-y-3">
            {market_data.top_gainers.map((stock, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 text-green-400 font-bold text-sm">
                    {index + 1}
                  </div>
                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
                    {stock.symbol}
                  </Badge>
                  <span className="text-white text-sm font-medium">{stock.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-green-400 font-semibold text-sm">+{stock.change_pct}%</p>
                    <p className="text-gray-400 text-xs">${parseFloat(stock.price).toFixed(2)}</p>
                  </div>
                  <TrendingUp className="w-4 h-4 text-green-400" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Market Data - Top Losers (if available) */}
      {market_data?.top_losers && market_data.top_losers.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingDown className="w-4 h-4 text-red-400" />
            <h3 className="text-lg font-semibold text-white uppercase">Top Market Losers</h3>
            <Badge className="bg-red-600/20 text-red-300 border-red-500/30 text-xs">
              {market_data.top_losers.length} stocks
            </Badge>
          </div>
          <div className="space-y-3">
            {market_data.top_losers.map((stock, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-red-500/20 text-red-400 font-bold text-sm">
                    {index + 1}
                  </div>
                  <Badge className="bg-red-500/20 text-red-300 border-red-500/30">
                    {stock.symbol}
                  </Badge>
                  <span className="text-white text-sm font-medium">{stock.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-red-400 font-semibold text-sm">{stock.change_pct}%</p>
                    <p className="text-gray-400 text-xs">${parseFloat(stock.price).toFixed(2)}</p>
                  </div>
                  <TrendingDown className="w-4 h-4 text-red-400" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Economic News Headlines */}
      {news_headlines && news_headlines.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Newspaper className="w-4 h-4 text-blue-400" />
            <h3 className="text-lg font-semibold text-white uppercase">Economic News Analysis</h3>
            <Badge className="bg-blue-600/20 text-blue-300 border-blue-500/30 text-xs">
              {news_headlines.length} articles
            </Badge>
          </div>
          <div className="space-y-4">
            {news_headlines.map((item, index) => (
              <a
                key={index}
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors group"
              >
                <div className="space-y-2">
                  <p className="text-white text-sm leading-relaxed group-hover:text-blue-400 transition-colors">
                    {item.headline}
                  </p>
                  <div className="flex items-center gap-3">
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
                    <span className="text-xs text-gray-500">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </a>
            ))}
          </div>
        </Card>
      )}

      {/* Data Sources Information */}
      <Card className="bg-white/5 border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-purple-400" />
          <h3 className="text-lg font-semibold text-white uppercase">Data Sources</h3>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-gray-400 uppercase mb-1">Economic Data</p>
            <p className="text-white text-sm">World Bank API, Federal Reserve</p>
          </div>
          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-gray-400 uppercase mb-1">Market Data</p>
            <p className="text-white text-sm">Google Finance, Yahoo Finance</p>
          </div>
          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-gray-400 uppercase mb-1">News Sources</p>
            <p className="text-white text-sm">Google News, Financial Times</p>
          </div>
          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-gray-400 uppercase mb-1">Last Updated</p>
            <p className="text-white text-sm">{new Date(data.timestamp).toLocaleString()}</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
