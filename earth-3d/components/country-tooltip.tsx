"use client"

import { Card } from "@/components/ui/card"

interface CountryTooltipProps {
  countryName: string
  countryFlag: string
  position: { x: number; y: number }
  visible: boolean
}

export function CountryTooltip({ countryName, countryFlag, position, visible }: CountryTooltipProps) {
  if (!visible) return null

  return (
    <div
      className="fixed pointer-events-none z-50 transition-opacity duration-200"
      style={{
        left: `${position.x + 20}px`,
        top: `${position.y + 20}px`,
        opacity: visible ? 1 : 0,
      }}
    >
      <Card className="bg-black/90 border-white/20 backdrop-blur-xl p-3 shadow-2xl">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{countryFlag}</span>
          <div>
            <p className="text-white font-semibold text-sm">{countryName}</p>
            <p className="text-gray-400 text-xs">Click to view details</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
