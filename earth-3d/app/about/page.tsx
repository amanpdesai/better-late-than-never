"use client"

import { Navbar } from "@/components/navbar"
import { Card } from "@/components/ui/card"
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { Globe, TrendingUp, Users, Zap, Database, Brain, Shield, Clock } from "lucide-react"
import { useEffect, useState } from "react"

// Mock data for charts
const globalSentimentData = [
  { month: "Jan", positive: 45, neutral: 35, negative: 20 },
  { month: "Feb", positive: 48, neutral: 33, negative: 19 },
  { month: "Mar", positive: 52, neutral: 30, negative: 18 },
  { month: "Apr", positive: 49, neutral: 32, negative: 19 },
  { month: "May", positive: 55, neutral: 28, negative: 17 },
  { month: "Jun", positive: 58, neutral: 27, negative: 15 },
]

const categoryDistribution = [
  { name: "Politics", value: 28, color: "#3b82f6" },
  { name: "Sports", value: 18, color: "#10b981" },
  { name: "Entertainment", value: 22, color: "#f59e0b" },
  { name: "Technology", value: 15, color: "#8b5cf6" },
  { name: "Economics", value: 12, color: "#ef4444" },
  { name: "Memes", value: 5, color: "#ec4899" },
]

const dataSourcesData = [
  { source: "Twitter/X", posts: 2.4 },
  { source: "Reddit", posts: 1.8 },
  { source: "News", posts: 1.2 },
  { source: "Forums", posts: 0.9 },
  { source: "Blogs", posts: 0.6 },
]

const coverageData = [
  { region: "North America", countries: 23, coverage: 95 },
  { region: "Europe", countries: 44, coverage: 92 },
  { region: "Asia", countries: 48, coverage: 88 },
  { region: "South America", countries: 12, coverage: 85 },
  { region: "Africa", countries: 54, coverage: 78 },
  { region: "Oceania", countries: 14, coverage: 90 },
]

export default function AboutPage() {
  const [stats, setStats] = useState({
    countries: 0,
    dataPoints: 0,
    categories: 0,
    accuracy: 0,
  })

  useEffect(() => {
    const duration = 2000
    const steps = 60
    const interval = duration / steps

    let step = 0
    const timer = setInterval(() => {
      step++
      const progress = step / steps

      setStats({
        countries: Math.floor(195 * progress),
        dataPoints: Math.floor(50 * progress),
        categories: Math.floor(6 * progress),
        accuracy: Math.floor(94 * progress),
      })

      if (step >= steps) clearInterval(timer)
    }, interval)

    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen bg-black">
      <Navbar />

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-500/10 via-transparent to-transparent" />
        <div className="container mx-auto px-6 py-24">
          <div className="max-w-4xl mx-auto text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-4">
              <Zap className="w-4 h-4" />
              Real-time Global Sentiment Analysis
            </div>
            <h1 className="text-6xl font-bold text-white leading-tight">
              Understanding the World's
              <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Collective Emotions
              </span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
              Global Mood aggregates and analyzes millions of data points daily to visualize real-time sentiment across
              195 countries and 6 major categories.
            </p>
          </div>
        </div>
      </div>

      {/* Animated Stats */}
      <div className="container mx-auto px-6 -mt-8 mb-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
          <Card className="bg-slate-950/80 border-blue-500/30 p-6 text-center backdrop-blur-xl shadow-blue-900/30 shadow-lg">
            <div className="text-4xl font-bold text-blue-400 mb-2">{stats.countries}</div>
            <div className="text-sm text-gray-400">Countries Tracked</div>
          </Card>
          <Card className="bg-slate-950/80 border-purple-500/30 p-6 text-center backdrop-blur-xl shadow-purple-900/30 shadow-lg">
            <div className="text-4xl font-bold text-purple-400 mb-2">{stats.dataPoints}M+</div>
            <div className="text-sm text-gray-400">Daily Data Points</div>
          </Card>
          <Card className="bg-slate-950/80 border-green-500/30 p-6 text-center backdrop-blur-xl shadow-green-900/30 shadow-lg">
            <div className="text-4xl font-bold text-green-400 mb-2">{stats.categories}</div>
            <div className="text-sm text-gray-400">Content Categories</div>
          </Card>
          <Card className="bg-slate-950/80 border-orange-500/30 p-6 text-center backdrop-blur-xl shadow-orange-900/30 shadow-lg">
            <div className="text-4xl font-bold text-orange-400 mb-2">{stats.accuracy}%</div>
            <div className="text-sm text-gray-400">AI Accuracy</div>
          </Card>
        </div>
      </div>

      <div className="container mx-auto px-6 pb-24 space-y-16">
        {/* Mission Section with Chart */}
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-gray-300 text-sm">
                <Globe className="w-4 h-4" />
                Our Mission
              </div>
              <h2 className="text-4xl font-bold text-white">Mapping Global Sentiment in Real-Time</h2>
              <p className="text-gray-300 leading-relaxed text-lg">
                We believe understanding collective emotions is key to understanding our world. By analyzing social
                media, news, and online discussions across 195 countries, we provide unprecedented insights into what
                people are feeling, thinking, and talking about.
              </p>
              <div className="flex gap-4 pt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="text-sm text-gray-400">Positive</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-gray-500" />
                  <span className="text-sm text-gray-400">Neutral</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-sm text-gray-400">Negative</span>
                </div>
              </div>
            </div>
            <Card className="bg-slate-950/85 border-white/15 p-6 backdrop-blur-xl shadow-blue-900/30 shadow-xl">
              <h3 className="text-lg font-semibold text-white mb-4">Global Sentiment Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={globalSentimentData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="month" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: "8px" }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Area type="monotone" dataKey="positive" stackId="1" stroke="#10b981" fill="#10b98130" />
                  <Area type="monotone" dataKey="neutral" stackId="1" stroke="#6b7280" fill="#6b728030" />
                  <Area type="monotone" dataKey="negative" stackId="1" stroke="#ef4444" fill="#ef444430" />
                </AreaChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </div>

        {/* Features Grid */}
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-gray-400 text-lg">Advanced technology powering global insights</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="bg-slate-950/80 border-blue-500/30 p-6 space-y-4 backdrop-blur-xl shadow-blue-900/30 shadow-lg">
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Brain className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">AI-Powered Analysis</h3>
              <p className="text-gray-400">
                Advanced machine learning models process and categorize millions of posts with 94% accuracy.
              </p>
            </Card>
            <Card className="bg-slate-950/80 border-purple-500/30 p-6 space-y-4 backdrop-blur-xl shadow-purple-900/30 shadow-lg">
              <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Clock className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Real-Time Updates</h3>
              <p className="text-gray-400">
                Data refreshes every 15 minutes to capture the latest trends and sentiment shifts.
              </p>
            </Card>
            <Card className="bg-slate-950/80 border-green-500/30 p-6 space-y-4 backdrop-blur-xl shadow-green-900/30 shadow-lg">
              <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Trend Detection</h3>
              <p className="text-gray-400">
                Identify emerging topics and viral content before they reach mainstream attention.
              </p>
            </Card>
            <Card className="bg-slate-950/80 border-orange-500/30 p-6 space-y-4 backdrop-blur-xl shadow-orange-900/30 shadow-lg">
              <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center">
                <Database className="w-6 h-6 text-orange-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Multi-Source Data</h3>
              <p className="text-gray-400">
                Aggregate data from social media, news outlets, forums, and blogs for comprehensive coverage.
              </p>
            </Card>
            <Card className="bg-slate-950/80 border-pink-500/30 p-6 space-y-4 backdrop-blur-xl shadow-pink-900/30 shadow-lg">
              <div className="w-12 h-12 rounded-lg bg-pink-500/20 flex items-center justify-center">
                <Users className="w-6 h-6 text-pink-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Category Insights</h3>
              <p className="text-gray-400">
                Track sentiment across Politics, Sports, Entertainment, Technology, Economics, and Memes.
              </p>
            </Card>
            <Card className="bg-slate-950/80 border-cyan-500/30 p-6 space-y-4 backdrop-blur-xl shadow-cyan-900/30 shadow-lg">
              <div className="w-12 h-12 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                <Shield className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="text-xl font-semibold text-white">Privacy First</h3>
              <p className="text-gray-400">
                All data is anonymized and aggregated. We never store or display personal information.
              </p>
            </Card>
          </div>
        </div>

        {/* Data Sources & Category Distribution */}
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8">
          <Card className="bg-slate-950/85 border-white/15 p-6 backdrop-blur-xl shadow-blue-900/30 shadow-xl">
            <h3 className="text-xl font-semibold text-white mb-6">Data Sources</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dataSourcesData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis type="number" stroke="#666" />
                <YAxis dataKey="source" type="category" stroke="#666" width={80} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: "8px" }}
                  labelStyle={{ color: "#fff" }}
                />
                <Bar dataKey="posts" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="text-sm text-gray-400 mt-4">Daily posts analyzed (in millions)</p>
          </Card>

          <Card className="bg-slate-950/85 border-white/15 p-6 backdrop-blur-xl shadow-purple-900/30 shadow-xl">
            <h3 className="text-xl font-semibold text-white mb-6">Category Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {categoryDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #333", borderRadius: "8px" }}
                  labelStyle={{ color: "#fff" }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {categoryDistribution.map((cat) => (
                <div key={cat.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                  <span className="text-sm text-gray-400">
                    {cat.name} ({cat.value}%)
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Global Coverage */}
        <div className="max-w-6xl mx-auto">
          <Card className="bg-slate-950/85 border-white/15 p-8 backdrop-blur-xl shadow-blue-900/30 shadow-xl">
            <h3 className="text-2xl font-semibold text-white mb-6">Global Coverage</h3>
            <div className="space-y-4">
              {coverageData.map((region) => (
                <div key={region.region} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300">{region.region}</span>
                    <span className="text-gray-400">
                      {region.countries} countries • {region.coverage}% coverage
                    </span>
                  </div>
                  <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-1000"
                      style={{ width: `${region.coverage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* How It Works */}
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-gray-400 text-lg">Our four-step process for analyzing global sentiment</p>
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: "01", title: "Data Collection", desc: "Aggregate posts from multiple platforms in real-time" },
              { step: "02", title: "AI Processing", desc: "Analyze sentiment, topics, and engagement using ML models" },
              { step: "03", title: "Categorization", desc: "Sort content into 6 major categories by country" },
              { step: "04", title: "Visualization", desc: "Display insights on interactive 3D globe interface" },
            ].map((item, i) => (
              <div key={i} className="relative">
                <Card className="bg-slate-950/80 border-white/15 p-6 space-y-4 h-full backdrop-blur-xl shadow-blue-900/30 shadow-lg">
                  <div className="text-5xl font-bold text-white/10">{item.step}</div>
                  <h4 className="text-lg font-semibold text-white">{item.title}</h4>
                  <p className="text-gray-400 text-sm">{item.desc}</p>
                </Card>
                {i < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-3 w-6 h-0.5 bg-gradient-to-r from-blue-500 to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-4xl mx-auto">
          <Card className="bg-slate-950/90 border-blue-500/30 p-12 text-center space-y-6 backdrop-blur-2xl shadow-blue-900/40 shadow-2xl">
            <h2 className="text-3xl font-bold text-white">Start Exploring Global Sentiment</h2>
            <p className="text-gray-300 text-lg max-w-2xl mx-auto">
              Click on any country to dive deep into real-time sentiment data, trending topics, and emotional insights
              from around the world.
            </p>
            <a
              href="/"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            >
              <Globe className="w-5 h-5" />
              Explore the Globe
            </a>
          </Card>
        </div>
      </div>
    </div>
  )
}
