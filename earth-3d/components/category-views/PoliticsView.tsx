"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Building2, Landmark, FileText, AlertCircle, Newspaper, Filter, ExternalLink, Clock } from "lucide-react"
import { cn } from "@/lib/utils"
import type { PoliticsData } from "@/lib/types"
import { useState } from "react"

interface PoliticsViewProps {
  data: PoliticsData
}

type FilterType = 'all' | 'positive' | 'negative' | 'neutral'

export function PoliticsView({ data }: PoliticsViewProps) {
  const { leadership_and_government, recent_and_upcoming, political_climate } = data
  const recent_policies = recent_and_upcoming?.recent_policies || []
  const key_issues = political_climate?.key_issues || []
  const recent_headlines = political_climate?.recent_headlines || []
  const [policyFilter, setPolicyFilter] = useState<FilterType>('all')
  const [headlineFilter, setHeadlineFilter] = useState<FilterType>('all')

  return (
    <div className="space-y-4">
      {/* Complete Leadership Structure - Enhanced */}
      {leadership_and_government && (
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Landmark className="w-4 h-4 text-blue-400" />
            <h3 className="text-lg font-semibold text-white uppercase">Complete Leadership Structure</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* President/Prime Minister */}
            {leadership_and_government.president && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-6 h-6 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400 uppercase mb-1">Head of State</p>
                    <p className="text-white font-semibold text-base">{leadership_and_government.president}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Legislature */}
            {leadership_and_government.legislature && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Landmark className="w-6 h-6 text-purple-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400 uppercase mb-1">Legislature</p>
                    <p className="text-white font-semibold text-base">{leadership_and_government.legislature}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Key Issues */}
      {key_issues && key_issues.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 text-orange-400" />
            <h3 className="text-lg font-semibold text-white uppercase">All Key Issues</h3>
            <Badge className="bg-orange-600/20 text-orange-300 border-orange-500/30 text-xs">
              {key_issues.length} issues
            </Badge>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {key_issues.map((issue, index) => (
              <div
                key={index}
                className="p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-orange-500/20 flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="w-3 h-3 text-orange-400" />
                  </div>
                  <span className="text-white text-sm font-medium">{issue}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Recent Policies */}
      {recent_policies && recent_policies.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-4 h-4 text-green-400" />
            <h3 className="text-lg font-semibold text-white uppercase">Recent Policies</h3>
            <Badge className="bg-green-600/20 text-green-300 border-green-500/30 text-xs">
              {recent_policies.length} policies
            </Badge>
          </div>

          {/* Filter Buttons */}
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400 mr-2">Filter by sentiment:</span>
            <div className="flex gap-2">
              <Button
                variant={policyFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPolicyFilter('all')}
                className={cn(
                  "text-xs",
                  policyFilter === 'all' 
                    ? "bg-blue-600 hover:bg-blue-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                All ({recent_policies.length})
              </Button>
              <Button
                variant={policyFilter === 'positive' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPolicyFilter('positive')}
                className={cn(
                  "text-xs",
                  policyFilter === 'positive' 
                    ? "bg-green-600 hover:bg-green-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                Positive ({recent_policies.filter(p => (p as any).sentiment === 'positive').length})
              </Button>
              <Button
                variant={policyFilter === 'negative' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPolicyFilter('negative')}
                className={cn(
                  "text-xs",
                  policyFilter === 'negative' 
                    ? "bg-red-600 hover:bg-red-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                Negative ({recent_policies.filter(p => (p as any).sentiment === 'negative').length})
              </Button>
              <Button
                variant={policyFilter === 'neutral' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPolicyFilter('neutral')}
                className={cn(
                  "text-xs",
                  policyFilter === 'neutral' 
                    ? "bg-gray-600 hover:bg-gray-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                Neutral ({recent_policies.filter(p => (p as any).sentiment === 'neutral').length})
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recent_policies
              .filter(policy => {
                if (policyFilter === 'positive') return (policy as any).sentiment === 'positive'
                if (policyFilter === 'negative') return (policy as any).sentiment === 'negative'
                if (policyFilter === 'neutral') return (policy as any).sentiment === 'neutral'
                return true // 'all'
              })
              .map((policy, index) => (
                <Card
                  key={index}
                  className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group cursor-pointer"
                  onClick={() => {
                    if (policy.url) {
                      window.open(policy.url, '_blank', 'noopener,noreferrer')
                    }
                  }}
                >
                  <div className="p-4 space-y-3">
                    {/* Header with badges */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                        <FileText className="w-3 h-3 mr-1" />
                        Policy
                      </Badge>

                      {(policy as any).sentiment && (
                        <Badge
                          variant="outline"
                          className={cn(
                            "text-xs border-white/20",
                            (policy as any).sentiment === "positive" && "text-green-400 bg-green-500/10",
                            (policy as any).sentiment === "negative" && "text-red-400 bg-red-500/10",
                            (policy as any).sentiment === "neutral" && "text-gray-400 bg-gray-500/10"
                          )}
                        >
                          {(policy as any).sentiment}
                        </Badge>
                      )}

                      <span className="text-xs text-gray-500 ml-auto">★ 50</span>
                    </div>

                    {/* Title */}
                    <h4 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                      {policy.title}
                    </h4>

                    {/* Source */}
                    {policy.source && (
                      <p className="text-gray-400 text-xs">
                        Source: {policy.source}
                      </p>
                    )}

                    {/* Click hint */}
                    {policy.url && (
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <ExternalLink className="w-3 h-3" />
                        <span className="truncate">Click card to read policy</span>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
          </div>
        </Card>
      )}

      {/* Recent Headlines */}
      {recent_headlines && recent_headlines.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Newspaper className="w-4 h-4 text-blue-400" />
            <h3 className="text-lg font-semibold text-white uppercase">Recent Headlines</h3>
            <Badge className="bg-blue-600/20 text-blue-300 border-blue-500/30 text-xs">
              {recent_headlines.length} headlines
            </Badge>
          </div>

          {/* Filter Buttons */}
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400 mr-2">Filter by sentiment:</span>
            <div className="flex gap-2">
              <Button
                variant={headlineFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setHeadlineFilter('all')}
                className={cn(
                  "text-xs",
                  headlineFilter === 'all' 
                    ? "bg-blue-600 hover:bg-blue-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                All ({recent_headlines.length})
              </Button>
              <Button
                variant={headlineFilter === 'positive' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setHeadlineFilter('positive')}
                className={cn(
                  "text-xs",
                  headlineFilter === 'positive' 
                    ? "bg-green-600 hover:bg-green-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                Positive ({recent_headlines.filter(h => h.sentiment === 'positive').length})
              </Button>
              <Button
                variant={headlineFilter === 'negative' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setHeadlineFilter('negative')}
                className={cn(
                  "text-xs",
                  headlineFilter === 'negative' 
                    ? "bg-red-600 hover:bg-red-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                Negative ({recent_headlines.filter(h => h.sentiment === 'negative').length})
              </Button>
              <Button
                variant={headlineFilter === 'neutral' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setHeadlineFilter('neutral')}
                className={cn(
                  "text-xs",
                  headlineFilter === 'neutral' 
                    ? "bg-gray-600 hover:bg-gray-700 text-white" 
                    : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
                )}
              >
                Neutral ({recent_headlines.filter(h => h.sentiment === 'neutral').length})
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recent_headlines
              .filter(headline => {
                if (headlineFilter === 'positive') return headline.sentiment === 'positive'
                if (headlineFilter === 'negative') return headline.sentiment === 'negative'
                if (headlineFilter === 'neutral') return headline.sentiment === 'neutral'
                return true // 'all'
              })
              .map((headline, index) => (
                <Card
                  key={index}
                  className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group cursor-pointer"
                  onClick={() => {
                    if (headline.url) {
                      window.open(headline.url, '_blank', 'noopener,noreferrer')
                    }
                  }}
                >
                  <div className="p-4 space-y-3">
                    {/* Header with badges */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                        <Newspaper className="w-3 h-3 mr-1" />
                        {headline.source}
                      </Badge>

                      {headline.sentiment && (
                        <Badge
                          variant="outline"
                          className={cn(
                            "text-xs border-white/20",
                            headline.sentiment === "positive" && "text-green-400 bg-green-500/10",
                            headline.sentiment === "negative" && "text-red-400 bg-red-500/10",
                            headline.sentiment === "neutral" && "text-gray-400 bg-gray-500/10"
                          )}
                        >
                          {headline.sentiment}
                        </Badge>
                      )}

                      <span className="text-xs text-gray-500 ml-auto">★ 50</span>
                    </div>

                    {/* Title */}
                    <h4 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                      {headline.headline}
                    </h4>

                    {/* Click hint */}
                    {headline.url && (
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <ExternalLink className="w-3 h-3" />
                        <span className="truncate">Click card to read headline</span>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
          </div>
        </Card>
      )}
    </div>
  )
}