"use client"

import { Navbar } from "@/components/navbar"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import Link from "next/link"
import { useState } from "react"
import { Search, TrendingUp, Globe, Users } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const countries = [
  {
    name: "United Kingdom",
    flag: "🇬🇧",
    slug: "united-kingdom",
    mood: "Ironic & Fast-paced",
    sentiment: 72,
    posts: 156789,
    region: "Europe",
    trending: true,
  },
  {
    name: "United States",
    flag: "🇺🇸",
    slug: "united-states",
    mood: "Energetic & Divided",
    sentiment: 65,
    posts: 892341,
    region: "North America",
    trending: true,
  },
  {
    name: "Japan",
    flag: "🇯🇵",
    slug: "japan",
    mood: "Curious & Creative",
    sentiment: 78,
    posts: 234567,
    region: "Asia",
    trending: false,
  },
  {
    name: "Germany",
    flag: "🇩🇪",
    slug: "germany",
    mood: "Analytical & Pragmatic",
    sentiment: 68,
    posts: 178923,
    region: "Europe",
    trending: false,
  },
  {
    name: "Brazil",
    flag: "🇧🇷",
    slug: "brazil",
    mood: "Passionate & Vibrant",
    sentiment: 81,
    posts: 345678,
    region: "South America",
    trending: true,
  },
  {
    name: "Australia",
    flag: "🇦🇺",
    slug: "australia",
    mood: "Laid-back & Humorous",
    sentiment: 75,
    posts: 123456,
    region: "Oceania",
    trending: false,
  },
  {
    name: "France",
    flag: "🇫🇷",
    slug: "france",
    mood: "Expressive & Cultural",
    sentiment: 70,
    posts: 198765,
    region: "Europe",
    trending: false,
  },
  {
    name: "South Korea",
    flag: "🇰🇷",
    slug: "south-korea",
    mood: "Dynamic & Tech-savvy",
    sentiment: 76,
    posts: 267890,
    region: "Asia",
    trending: true,
  },
  {
    name: "Canada",
    flag: "🇨🇦",
    slug: "canada",
    mood: "Friendly & Diverse",
    sentiment: 73,
    posts: 145678,
    region: "North America",
    trending: false,
  },
]

const regionalData = [
  { region: "Europe", countries: 3, posts: 534477 },
  { region: "North America", countries: 2, posts: 1038019 },
  { region: "Asia", countries: 2, posts: 502457 },
  { region: "South America", countries: 1, posts: 345678 },
  { region: "Oceania", countries: 1, posts: 123456 },
]

const sentimentDistribution = [
  { name: "Positive (70-100)", value: 5, color: "#10b981" },
  { name: "Neutral (50-69)", value: 3, color: "#6b7280" },
  { name: "Negative (0-49)", value: 1, color: "#ef4444" },
]

export default function CountriesPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null)

  const filteredCountries = countries.filter((country) => {
    const matchesSearch = country.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRegion = !selectedRegion || country.region === selectedRegion
    return matchesSearch && matchesRegion
  })

  const regions = Array.from(new Set(countries.map((c) => c.region)))

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      <div className="container mx-auto px-6 py-24">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-4">
            <div className="inline-block">
              <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Global Sentiment Explorer
              </h1>
            </div>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
              Dive into real-time sentiment data from countries around the world. Discover trends, moods, and
              conversations shaping our digital landscape.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="bg-slate-950/80 border-blue-500/30 p-6 backdrop-blur-xl shadow-blue-900/30 shadow-lg">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-500/20 rounded-lg">
                  <Globe className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">{countries.length}</p>
                  <p className="text-sm text-gray-400">Countries Tracked</p>
                </div>
              </div>
            </Card>
            <Card className="bg-slate-950/80 border-purple-500/30 p-6 backdrop-blur-xl shadow-purple-900/30 shadow-lg">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-purple-500/20 rounded-lg">
                  <Users className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">
                    {(countries.reduce((sum, c) => sum + c.posts, 0) / 1000000).toFixed(1)}M
                  </p>
                  <p className="text-sm text-gray-400">Total Posts</p>
                </div>
              </div>
            </Card>
            <Card className="bg-slate-950/80 border-green-500/30 p-6 backdrop-blur-xl shadow-green-900/30 shadow-lg">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-green-500/20 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">
                    {Math.round(countries.reduce((sum, c) => sum + c.sentiment, 0) / countries.length)}%
                  </p>
                  <p className="text-sm text-gray-400">Avg Sentiment</p>
                </div>
              </div>
            </Card>
            <Card className="bg-slate-950/80 border-pink-500/30 p-6 backdrop-blur-xl shadow-pink-900/30 shadow-lg">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-pink-500/20 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-pink-400" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white">{countries.filter((c) => c.trending).length}</p>
                  <p className="text-sm text-gray-400">Trending Now</p>
                </div>
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-slate-950/85 border-white/15 p-6 backdrop-blur-xl shadow-blue-900/30 shadow-xl">
              <h3 className="text-xl font-semibold text-white mb-6">Regional Distribution</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={regionalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="region" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <YAxis stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <Bar dataKey="posts" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="bg-slate-950/85 border-white/15 p-6 backdrop-blur-xl shadow-purple-900/30 shadow-xl">
              <h3 className="text-xl font-semibold text-white mb-6">Sentiment Distribution</h3>
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={sentimentDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {sentimentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 space-y-2">
                {sentimentDistribution.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-gray-400">{item.name}</span>
                    </div>
                    <span className="text-white font-medium">{item.value} countries</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <Card className="bg-slate-950/85 border-white/15 p-6 backdrop-blur-xl shadow-blue-900/30 shadow-xl">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  placeholder="Search countries..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-white/5 border-white/10 text-white placeholder:text-gray-500"
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={selectedRegion === null ? "default" : "outline"}
                  onClick={() => setSelectedRegion(null)}
                  className={
                    selectedRegion === null
                      ? "bg-blue-500 hover:bg-blue-600"
                      : "border-white/10 text-gray-400 hover:bg-white/10"
                  }
                >
                  All Regions
                </Button>
                {regions.map((region) => (
                  <Button
                    key={region}
                    variant={selectedRegion === region ? "default" : "outline"}
                    onClick={() => setSelectedRegion(region)}
                    className={
                      selectedRegion === region
                        ? "bg-blue-500 hover:bg-blue-600"
                        : "border-white/10 text-gray-400 hover:bg-white/10"
                    }
                  >
                    {region}
                  </Button>
                ))}
              </div>
            </div>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCountries.map((country) => (
              <Link key={country.slug} href={`/country/${country.slug}`}>
                <Card className="bg-slate-950/80 border-white/10 p-6 hover:bg-slate-900/80 transition-all cursor-pointer group h-full backdrop-blur-xl shadow-lg shadow-blue-900/20">
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-4xl">{country.flag}</span>
                        <div>
                          <h3 className="text-xl font-semibold text-white group-hover:text-blue-400 transition-colors">
                            {country.name}
                          </h3>
                          <p className="text-sm text-gray-500">{country.region}</p>
                        </div>
                      </div>
                      {country.trending && (
                        <Badge className="bg-pink-500/20 text-pink-400 border-pink-500/30">
                          <TrendingUp className="w-3 h-3 mr-1" />
                          Trending
                        </Badge>
                      )}
                    </div>

                    <Badge variant="outline" className="text-gray-400 border-white/20">
                      {country.mood}
                    </Badge>

                    <div className="space-y-3 pt-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-400">Sentiment Score</span>
                        <span className="text-lg font-semibold text-white">{country.sentiment}%</span>
                      </div>
                      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                          style={{ width: `${country.sentiment}%` }}
                        />
                      </div>

                      <div className="flex justify-between items-center pt-1">
                        <span className="text-sm text-gray-400">Total Posts</span>
                        <span className="text-sm font-medium text-white">{country.posts.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>

          {filteredCountries.length === 0 && (
            <Card className="bg-slate-950/85 border-white/15 p-12 backdrop-blur-xl shadow-blue-900/30 shadow-xl">
              <div className="text-center space-y-4">
                <Globe className="w-16 h-16 text-gray-600 mx-auto" />
                <h3 className="text-xl font-semibold text-white">No countries found</h3>
                <p className="text-gray-400">Try adjusting your search or filter criteria</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
