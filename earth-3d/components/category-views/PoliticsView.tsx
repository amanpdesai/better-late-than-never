"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Building2, Landmark, FileText, AlertCircle, Newspaper } from "lucide-react"
import { cn } from "@/lib/utils"
import type { PoliticsData } from "@/lib/types"

interface PoliticsViewProps {
  data: PoliticsData
}

export function PoliticsView({ data }: PoliticsViewProps) {
  const { leadership_and_government, recent_and_upcoming, political_climate } = data
  const recent_policies = recent_and_upcoming?.recent_policies || []
  const key_issues = political_climate?.key_issues || []
  const recent_headlines = political_climate?.recent_headlines || []

  return (
    <div className="space-y-4">
      {/* Leadership & Government */}
      {leadership_and_government && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Landmark className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Leadership & Government</h3>
          </div>

          <div className="space-y-4">
            {/* President/Prime Minister */}
            {leadership_and_government.president && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400 uppercase mb-1">Head of State</p>
                    <p className="text-white font-semibold">{leadership_and_government.president}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Legislature */}
            {leadership_and_government.legislature && (
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Landmark className="w-5 h-5 text-purple-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400 uppercase mb-1">Legislature</p>
                    <p className="text-white font-semibold">{leadership_and_government.legislature}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Key Issues */}
      {key_issues && key_issues.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 text-orange-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Key Issues</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {key_issues.map((issue, index) => (
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

      {/* Recent Policies */}
      {recent_policies && recent_policies.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-4 h-4 text-green-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Recent Policies</h3>
          </div>
          <div className="space-y-3">
            {recent_policies.map((policy, index) => (
              <a
                key={index}
                href={policy.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors group"
              >
                <p className="text-white text-sm leading-relaxed group-hover:text-blue-400 transition-colors">
                  {policy.title}
                </p>
                <p className="text-xs text-gray-500 mt-1">{policy.source}</p>
              </a>
            ))}
          </div>
        </Card>
      )}

      {/* Recent Headlines */}
      {recent_headlines && recent_headlines.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Newspaper className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Recent Headlines</h3>
          </div>
          <div className="space-y-3">
            {recent_headlines.map((item, index) => (
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
