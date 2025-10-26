"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Building2, Landmark, FileText, AlertCircle, Newspaper } from "lucide-react"
import { cn } from "@/lib/utils"
import type { PoliticsData } from "@/lib/types"

interface PoliticsSummaryViewProps {
  data: PoliticsData
}

export function PoliticsSummaryView({ data }: PoliticsSummaryViewProps) {
  const { leadership_and_government, recent_and_upcoming, political_climate } = data
  const recent_policies = recent_and_upcoming?.recent_policies || []
  const key_issues = political_climate?.key_issues || []
  const recent_headlines = political_climate?.recent_headlines || []

  return (
    <div className="space-y-2">
      {/* Leadership & Government - Compact */}
      {leadership_and_government && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Landmark className="w-3 h-3 text-blue-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Leadership</h3>
          </div>

          <div className="space-y-2">
            {/* President/Prime Minister */}
            {leadership_and_government.president && (
              <div className="p-2 bg-white/5 rounded border border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-3 h-3 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400">Head of State</p>
                    <p className="text-white font-semibold text-xs">{leadership_and_government.president}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Legislature */}
            {leadership_and_government.legislature && (
              <div className="p-2 bg-white/5 rounded border border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Landmark className="w-3 h-3 text-purple-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400">Legislature</p>
                    <p className="text-white font-semibold text-xs">{leadership_and_government.legislature}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Key Issues - Compact */}
      {key_issues && key_issues.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-3 h-3 text-orange-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Key Issues</h3>
          </div>
          <div className="flex flex-wrap gap-1">
            {key_issues.slice(0, 3).map((issue, index) => (
              <Badge
                key={index}
                variant="outline"
                className="text-xs bg-orange-500/10 text-orange-300 border-orange-500/30"
              >
                {issue}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Recent Policies - Compact */}
      {recent_policies && recent_policies.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="w-3 h-3 text-green-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Recent Policies</h3>
          </div>
          <div className="space-y-1">
            {recent_policies.slice(0, 3).map((policy, index) => (
              <div
                key={index}
                className="p-2 bg-white/5 rounded border border-white/10"
              >
                <p className="text-white text-xs leading-relaxed line-clamp-2">
                  {policy.title}
                </p>
                <p className="text-xs text-gray-500 mt-1">{policy.source}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Recent Headlines - Compact */}
      {recent_headlines && recent_headlines.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Newspaper className="w-3 h-3 text-blue-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Latest Headlines</h3>
          </div>
          <div className="space-y-1">
            {recent_headlines.slice(0, 3).map((item, index) => (
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
    </div>
  )
}
