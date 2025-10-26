"use client"

import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Sparkles, Database, Globe, TrendingUp, Users, Zap } from "lucide-react"

export default function CustomPage() {
  const solutions = [
    {
      id: "usa-meme-generator",
      title: "USA Meme Generator",
      description:
        "Generate hilarious USA-themed memes using AI. Create patriotic, political, or just plain funny memes with custom text and imagery.",
      icon: "🇺🇸",
      href: "/custom/usa-meme-generator",
      tags: ["AI", "Memes", "USA"],
    },
  ]

  return (
    <div className="min-h-screen bg-black">
      <Navbar />

      <main className="container mx-auto px-6 pt-32 pb-20">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-blue-300 font-medium">Custom Solutions</span>
            </div>
            <h1 className="text-5xl font-bold text-white mb-4 text-balance">AI-Powered Tools & Solutions</h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto text-balance">
              Explore our collection of custom AI tools designed to solve unique problems and spark creativity.
            </p>
          </div>

          {/* Data Overview */}
          <div className="mb-16">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card className="bg-white/5 border-white/10">
                <CardContent className="p-6 text-center">
                  <Database className="w-8 h-8 text-blue-400 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-white mb-1">7</div>
                  <div className="text-sm text-gray-400">Data Categories</div>
                </CardContent>
              </Card>
              <Card className="bg-white/5 border-white/10">
                <CardContent className="p-6 text-center">
                  <Globe className="w-8 h-8 text-green-400 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-white mb-1">5</div>
                  <div className="text-sm text-gray-400">Countries</div>
                </CardContent>
              </Card>
              <Card className="bg-white/5 border-white/10">
                <CardContent className="p-6 text-center">
                  <TrendingUp className="w-8 h-8 text-purple-400 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-white mb-1">24/7</div>
                  <div className="text-sm text-gray-400">Data Updates</div>
                </CardContent>
              </Card>
              <Card className="bg-white/5 border-white/10">
                <CardContent className="p-6 text-center">
                  <Users className="w-8 h-8 text-orange-400 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-white mb-1">10+</div>
                  <div className="text-sm text-gray-400">Data Sources</div>
                </CardContent>
              </Card>
            </div>
            
            <div className="text-center">
              <p className="text-gray-400 max-w-3xl mx-auto">
                We collect real-time data across <span className="text-blue-300 font-medium">memes, economics, politics, news, Google Trends, YouTube, and sports</span> from 
                <span className="text-green-300 font-medium"> USA, UK, Canada, Australia, and India</span>. 
                Our custom applications transform this rich dataset into powerful AI tools.
              </p>
            </div>
          </div>

          {/* Solutions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {solutions.map((solution) => (
              <Link key={solution.id} href={solution.href}>
                <Card className="h-full bg-white/5 border-white/10 hover:border-blue-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10 cursor-pointer group">
                  <CardHeader>
                    <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">
                      {solution.icon}
                    </div>
                    <CardTitle className="text-white text-2xl mb-2">{solution.title}</CardTitle>
                    <CardDescription className="text-gray-400 text-base">{solution.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {solution.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-3 py-1 text-xs rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <Button className="w-full bg-blue-500 hover:bg-blue-600 text-white">Try it now</Button>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Coming Soon Section */}
          <div className="mt-16 text-center">
            <div className="inline-block px-6 py-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-gray-400">More custom solutions coming soon...</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}