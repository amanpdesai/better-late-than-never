"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { usePathname } from "next/navigation"
import { Earth } from "lucide-react"

export function Navbar() {
  const pathname = usePathname()

  const navItems = [
    { name: "World", href: "/" },
    { name: "About", href: "/about" },
    { name: "Countries", href: "/countries" },
  ]

  return (
    <nav
      className="fixed top-0 left-0 z-40 bg-black/20 backdrop-blur-md border-b border-white/10 w-full transition-[right] duration-300 ease-in-out"
      style={{ right: "var(--panel-offset, 0px)" }}
    >
      <div
        className="container mx-auto py-4 flex items-center gap-4"
        style={{
          paddingLeft: "1.5rem",
          paddingRight: "calc(1rem + var(--panel-offset, 0px))",
          justifyContent: "space-between",
        }}
      >
        <div className="flex items-center gap-2 text-white">
          <Earth className="h-6 w-6 text-blue-400" aria-hidden />
          <span className="text-xl font-bold text-white">Global Mood</span>
        </div>
        <div className="flex items-center gap-2 ml-auto">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <Button
                variant="ghost"
                className={`text-white hover:bg-white/10 hover:text-blue-300 transition-colors ${
                  pathname === item.href ? "bg-white/10" : ""
                }`}
              >
                {item.name}
              </Button>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}
