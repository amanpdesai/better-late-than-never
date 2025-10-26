"use client"

import { Navbar } from "@/components/navbar"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  ArrowLeft,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  MessageSquare,
  Heart,
  Share2,
  Play,
  ArrowUp,
  Eye,
  MessageCircle,
} from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts"

type Sentiment = "positive" | "negative" | "neutral"
type MoodKey = "joy" | "curiosity" | "anger" | "confusion" | "sadness"
type ContentKind = "video" | "reddit" | "news" | "twitter" | "generic"

interface RepresentativeContentBase {
  title: string
  excerpt: string
  engagement: number
  platform: string
  sentiment: Sentiment
  timestamp: string
  type: ContentKind
  url: string
}

type VideoContent = RepresentativeContentBase & {
  type: "video"
  thumbnail?: string
  author?: string
  views?: number
}

type RedditContent = RepresentativeContentBase & {
  type: "reddit"
  upvotes?: number
  comments?: number
  source?: string
}

type NewsContent = RepresentativeContentBase & {
  type: "news"
  thumbnail?: string
  source?: string
}

type TwitterContent = RepresentativeContentBase & {
  type: "twitter"
  author?: string
}

type GenericContent = RepresentativeContentBase & {
  type: "generic"
}

type RepresentativeContent = VideoContent | RedditContent | NewsContent | TwitterContent | GenericContent

interface CountryExpandedData {
  name: string
  flag: string
  lastUpdated: string
  moodSummary: string
  moodMeter: Record<MoodKey, number>
  sentimentTrend: number[]
  topTopics: { keyword: string; sentiment: Sentiment; volume: number }[]
  representativeContent: RepresentativeContent[]
  categoryMetrics: { totalPosts: number; avgEngagement: number; viralityScore: number }
  platformBreakdown: { platform: string; percentage: number }[]
  engagementStats: { likes: number; shares: number; comments: number }
}

const mockExpandedData: CountryExpandedData = {
  name: "United Kingdom",
  flag: "🇬🇧",
  lastUpdated: "02:00 UTC",
  moodSummary: "The UK's internet mood is ironic and fast-paced, with humor trending toward tech culture.",
  moodMeter: {
    joy: 35,
    curiosity: 28,
    anger: 15,
    confusion: 12,
    sadness: 10,
  },
  sentimentTrend: [45, 52, 48, 55, 60, 58, 62, 65, 63, 68, 70, 72],
  topTopics: [
    { keyword: "AIRevolution", sentiment: "positive" as const, volume: 234 },
    { keyword: "TechNews", sentiment: "neutral" as const, volume: 189 },
    { keyword: "ClimateAction", sentiment: "negative" as const, volume: 156 },
    { keyword: "Innovation", sentiment: "positive" as const, volume: 142 },
    { keyword: "BreakingNews", sentiment: "neutral" as const, volume: 128 },
    { keyword: "StartupLife", sentiment: "positive" as const, volume: 115 },
    { keyword: "PolicyDebate", sentiment: "neutral" as const, volume: 98 },
    { keyword: "CyberSecurity", sentiment: "negative" as const, volume: 87 },
  ],
  representativeContent: [
    {
      title: "AI Breakthrough: New Model Achieves 99% Accuracy",
      excerpt:
        "Researchers unveil groundbreaking AI system that achieves human-level comprehension in complex reasoning tasks...",
      engagement: 45600,
      platform: "YouTube",
      sentiment: "positive" as const,
      timestamp: "2 hours ago",
      type: "video" as const,
      thumbnail: "/ai-technology-breakthrough.jpg",
      author: "TechVision",
      views: 1240000,
      url: "https://youtube.com/watch?v=example",
    },
    {
      title: "What's your take on the new AI regulations?",
      excerpt:
        "The government just announced sweeping changes to AI development laws. This could change everything for startups and big tech companies alike. Thoughts?",
      engagement: 32400,
      platform: "Reddit",
      sentiment: "neutral" as const,
      timestamp: "4 hours ago",
      type: "reddit" as const,
      upvotes: 8900,
      comments: 1240,
      source: "technology",
      url: "https://reddit.com/r/technology/example",
    },
    {
      title: "Tech Giants Face Historic Antitrust Ruling",
      excerpt:
        "In a landmark decision, regulators impose strict new requirements on major technology platforms, signaling a shift in digital market oversight...",
      engagement: 28900,
      platform: "BBC News",
      sentiment: "neutral" as const,
      timestamp: "6 hours ago",
      type: "news" as const,
      thumbnail: "/tech-companies-regulation.jpg",
      source: "BBC News",
      url: "https://bbc.com/news/example",
    },
    {
      title:
        "Just witnessed the most incredible AI demo at the conference. The future is here and it's mind-blowing. 🤯",
      excerpt:
        "Just witnessed the most incredible AI demo at the conference. The future is here and it's mind-blowing. 🤯 #AI #TechConf #Innovation",
      engagement: 24500,
      platform: "Twitter",
      sentiment: "positive" as const,
      timestamp: "8 hours ago",
      type: "twitter" as const,
      author: "@TechGuru",
      url: "https://twitter.com/example",
    },
    {
      title: "Startup Raises Record $500M Series C",
      excerpt:
        "Local AI startup secures massive funding round led by top venture capital firms, valuing the company at $2.5 billion...",
      engagement: 21300,
      platform: "TechCrunch",
      sentiment: "positive" as const,
      timestamp: "10 hours ago",
      type: "news" as const,
      thumbnail: "/startup-funding-celebration.jpg",
      source: "TechCrunch",
      url: "https://techcrunch.com/example",
    },
    {
      title: "The Future of Work: AI Edition",
      excerpt:
        "Deep dive into how artificial intelligence is reshaping the workplace, featuring interviews with industry leaders and workers adapting to change...",
      engagement: 19800,
      platform: "YouTube",
      sentiment: "neutral" as const,
      timestamp: "12 hours ago",
      type: "video" as const,
      thumbnail: "/future-of-work-ai.png",
      author: "WorkTech Insights",
      views: 890000,
      url: "https://youtube.com/watch?v=example2",
    },
    {
      title: "ELI5: How do large language models actually work?",
      excerpt:
        "I keep hearing about GPT and other LLMs but I don't really understand the underlying technology. Can someone explain it in simple terms?",
      engagement: 18200,
      platform: "Reddit",
      sentiment: "neutral" as const,
      timestamp: "14 hours ago",
      type: "reddit" as const,
      upvotes: 5600,
      comments: 892,
      source: "explainlikeimfive",
      url: "https://reddit.com/r/explainlikeimfive/example",
    },
    {
      title: "Privacy advocates raise concerns over new data collection practices",
      excerpt:
        "New report reveals concerning trends in how tech companies are collecting and using personal data, sparking debate about digital privacy rights...",
      engagement: 16900,
      platform: "The Guardian",
      sentiment: "negative" as const,
      timestamp: "16 hours ago",
      type: "news" as const,
      thumbnail: "/data-privacy-concerns.jpg",
      source: "The Guardian",
      url: "https://theguardian.com/example",
    },
  ],
  categoryMetrics: {
    totalPosts: 156789,
    avgEngagement: 12.4,
    viralityScore: 87,
  },
  platformBreakdown: [
    { platform: "Twitter", percentage: 35 },
    { platform: "Reddit", percentage: 28 },
    { platform: "TikTok", percentage: 22 },
    { platform: "YouTube", percentage: 15 },
  ],
  engagementStats: {
    likes: 2340000,
    shares: 890000,
    comments: 456000,
  },
}

const historicalSentiment = [
  { time: "00:00", sentiment: 65, posts: 8500 },
  { time: "02:00", sentiment: 62, posts: 6200 },
  { time: "04:00", sentiment: 58, posts: 4100 },
  { time: "06:00", sentiment: 61, posts: 7800 },
  { time: "08:00", sentiment: 68, posts: 12400 },
  { time: "10:00", sentiment: 72, posts: 15600 },
  { time: "12:00", sentiment: 75, posts: 18900 },
  { time: "14:00", sentiment: 73, posts: 17200 },
  { time: "16:00", sentiment: 70, posts: 16100 },
  { time: "18:00", sentiment: 68, posts: 14500 },
  { time: "20:00", sentiment: 71, posts: 13800 },
  { time: "22:00", sentiment: 72, posts: 11200 },
]

const categoryComparison = [
  { category: "Memes", score: 85 },
  { category: "Politics", score: 45 },
  { category: "Sports", score: 78 },
  { category: "Tech", score: 72 },
  { category: "Entertainment", score: 81 },
]

const emotionalProfile = [
  { emotion: "Joy", value: 35, fullMark: 100 },
  { emotion: "Curiosity", value: 28, fullMark: 100 },
  { emotion: "Anger", value: 15, fullMark: 100 },
  { emotion: "Confusion", value: 12, fullMark: 100 },
  { emotion: "Sadness", value: 10, fullMark: 100 },
]

const topInfluencers = [
  { name: "@TechGuru", followers: "2.4M", engagement: 94, posts: 156 },
  { name: "@MemeLord", followers: "1.8M", engagement: 89, posts: 234 },
  { name: "@NewsDaily", followers: "3.1M", engagement: 76, posts: 89 },
  { name: "@SportsFan", followers: "1.2M", engagement: 82, posts: 178 },
]

const trendingHashtags: { tag: string; growth: number; sentiment: Sentiment }[] = [
  { tag: "#AIRevolution", growth: 234, sentiment: "positive" },
  { tag: "#TechNews", growth: 189, sentiment: "neutral" },
  { tag: "#ClimateAction", growth: -45, sentiment: "negative" },
  { tag: "#Innovation", growth: 142, sentiment: "positive" },
  { tag: "#BreakingNews", growth: 78, sentiment: "neutral" },
  { tag: "#StartupLife", growth: 115, sentiment: "positive" },
]

export default function CountryDetailPage() {
  const searchParams = useSearchParams()
  const category = searchParams.get("category") || "Memes"

  const moodColors: Record<MoodKey, string> = {
    joy: "bg-yellow-500",
    curiosity: "bg-blue-500",
    anger: "bg-red-500",
    confusion: "bg-purple-500",
    sadness: "bg-gray-500",
  }

  const sentimentColors: Record<Sentiment, string> = {
    positive: "text-green-500 bg-green-500/10 border-green-500/20",
    negative: "text-red-500 bg-red-500/10 border-red-500/20",
    neutral: "text-gray-500 bg-gray-500/10 border-gray-500/20",
  }

  const renderContentCard = (content: RepresentativeContent, index: number) => {
    const baseCardClasses = "bg-white/5 border-white/10 p-5 hover:bg-white/10 transition-all cursor-pointer group"

    switch (content.type) {
      case "video":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              <div className="relative h-48 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-lg overflow-hidden">
                <img
                  src={content.thumbnail || "/placeholder.svg"}
                  alt={content.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center group-hover:bg-black/30 transition-colors">
                  <div className="w-16 h-16 rounded-full bg-red-600 flex items-center justify-center">
                    <Play className="w-8 h-8 text-white ml-1" fill="white" />
                  </div>
                </div>
                {content.views && (
                  <div className="absolute bottom-3 right-3 bg-black/80 px-3 py-1 rounded text-sm text-white flex items-center gap-2">
                    <Eye className="w-4 h-4" />
                    {(content.views / 1000).toFixed(0)}k views
                  </div>
                )}
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-red-500/10 border-red-500/30 text-red-400">
                    {content.platform}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  <span className="text-xs text-gray-500">{content.timestamp}</span>
                </div>
                <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                  {content.title}
                </h4>
                {content.author && <p className="text-sm text-gray-400">by {content.author}</p>}
                <div className="flex items-center justify-between pt-3 border-t border-white/5">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Heart className="w-4 h-4" />
                      <span>{(content.engagement * 0.6).toFixed(0)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageSquare className="w-4 h-4" />
                      <span>{(content.engagement * 0.2).toFixed(0)}</span>
                    </div>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" />
                </div>
              </div>
            </div>
          </Card>
        )

      case "reddit":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-orange-500/10 border-orange-500/30 text-orange-400">
                    {content.platform}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  <span className="text-xs text-gray-500">{content.timestamp}</span>
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </div>
              <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                {content.title}
              </h4>
              <p className="text-gray-400 text-sm line-clamp-2">{content.excerpt}</p>
              <div className="flex items-center gap-4 text-sm pt-2 border-t border-white/5">
                <div className="flex items-center gap-1 text-orange-400">
                  <ArrowUp className="w-4 h-4" />
                  <span className="font-medium">{content.upvotes?.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1 text-gray-400">
                  <MessageCircle className="w-4 h-4" />
                  <span>{content.comments?.toLocaleString()}</span>
                </div>
                {content.source && <span className="text-gray-500">r/{content.source}</span>}
              </div>
            </div>
          </Card>
        )

      case "news":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              {content.thumbnail && (
                <div className="relative h-48 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-lg overflow-hidden">
                  <img
                    src={content.thumbnail || "/placeholder.svg"}
                    alt={content.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-blue-500/10 border-blue-500/30 text-blue-400">
                    News
                  </Badge>
                  {content.source && <span className="text-xs text-gray-400 font-medium">{content.source}</span>}
                  <span className="text-xs text-gray-500">{content.timestamp}</span>
                </div>
                <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                  {content.title}
                </h4>
                <p className="text-gray-400 text-sm line-clamp-2">{content.excerpt}</p>
                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>{content.engagement.toLocaleString()} reads</span>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" />
                </div>
              </div>
            </div>
          </Card>
        )

      case "twitter":
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-sky-500/10 border-sky-500/30 text-sky-400">
                    {content.platform}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  <span className="text-xs text-gray-500">{content.timestamp}</span>
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </div>
              {content.author && (
                <p className="text-sm text-gray-400">
                  <span className="text-white font-medium">{content.author}</span>
                </p>
              )}
              <p className="text-white text-sm leading-relaxed">{content.excerpt}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500 pt-2 border-t border-white/5">
                <div className="flex items-center gap-1">
                  <Heart className="w-4 h-4" />
                  <span>{(content.engagement * 0.5).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Share2 className="w-4 h-4" />
                  <span>{(content.engagement * 0.3).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <MessageSquare className="w-4 h-4" />
                  <span>{(content.engagement * 0.2).toFixed(0)}</span>
                </div>
              </div>
            </div>
          </Card>
        )

      default:
        return (
          <Card key={index} className={baseCardClasses}>
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs">
                    {content.platform}
                  </Badge>
                  <Badge variant="outline" className={`text-xs ${sentimentColors[content.sentiment]}`}>
                    {content.sentiment}
                  </Badge>
                  <span className="text-xs text-gray-500">{content.timestamp}</span>
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </div>
              <h4 className="text-white font-medium leading-snug group-hover:text-blue-400 transition-colors">
                {content.title}
              </h4>
              <p className="text-gray-400 text-sm line-clamp-2">{content.excerpt}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500 pt-2 border-t border-white/5">
                <div className="flex items-center gap-1">
                  <Heart className="w-4 h-4" />
                  <span>{(content.engagement * 0.6).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <MessageSquare className="w-4 h-4" />
                  <span>{(content.engagement * 0.2).toFixed(0)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Share2 className="w-4 h-4" />
                  <span>{(content.engagement * 0.2).toFixed(0)}</span>
                </div>
              </div>
            </div>
          </Card>
        )
    }
  }

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      <div className="container mx-auto px-6 py-24">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Back Button */}
          <Link href="/countries">
            <Button variant="ghost" className="text-white hover:bg-white/10 mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Countries
            </Button>
          </Link>

          {/* Enhanced Header with Gradient Background */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500/20 via-purple-500/10 to-pink-500/20 border border-white/10 p-8">
            <div className="relative z-10">
              <h1 className="text-5xl font-bold text-white mb-2">{mockExpandedData.name}</h1>
              <div className="flex items-center gap-4 text-gray-400">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>Last Updated: {mockExpandedData.lastUpdated}</span>
                </div>
                <Badge variant="outline" className="text-blue-400 border-blue-400/30">
                  Category: {category}
                </Badge>
              </div>
            </div>
          </div>

          {/* Enhanced Mood Summary with Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2 bg-white/5 border-white/10 p-6">
              <h2 className="text-2xl font-semibold text-white mb-4">Current Mood Analysis</h2>
              <p className="text-gray-300 text-lg leading-relaxed mb-6">{mockExpandedData.moodSummary}</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white/5 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-green-400">+12%</p>
                  <p className="text-sm text-gray-400 mt-1">vs Yesterday</p>
                </div>
                <div className="bg-white/5 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-blue-400">72</p>
                  <p className="text-sm text-gray-400 mt-1">Sentiment Score</p>
                </div>
                <div className="bg-white/5 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-purple-400">#3</p>
                  <p className="text-sm text-gray-400 mt-1">Global Rank</p>
                </div>
              </div>
            </Card>

            <Card className="bg-white/5 border-white/10 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Quick Stats</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Active Users</span>
                  <span className="text-white font-semibold">2.4M</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Posts Today</span>
                  <span className="text-white font-semibold">156K</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Trending Topics</span>
                  <span className="text-white font-semibold">24</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Viral Content</span>
                  <span className="text-white font-semibold">8</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Added Comprehensive Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white/5 border-white/10 p-6">
              <h2 className="text-2xl font-semibold text-white mb-6">24-Hour Sentiment Trend</h2>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={historicalSentiment}>
                  <defs>
                    <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="time" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <YAxis stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Area
                    type="monotone"
                    dataKey="sentiment"
                    stroke="#3b82f6"
                    fill="url(#sentimentGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            <Card className="bg-white/5 border-white/10 p-6">
              <h2 className="text-2xl font-semibold text-white mb-6">Post Volume Over Time</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={historicalSentiment}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="time" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <YAxis stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Bar dataKey="posts" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="bg-white/5 border-white/10 p-6">
              <h2 className="text-2xl font-semibold text-white mb-6">Category Sentiment Comparison</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryComparison} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis type="number" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <YAxis dataKey="category" type="category" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} width={100} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Bar dataKey="score" fill="#10b981" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="bg-white/5 border-white/10 p-6">
              <h2 className="text-2xl font-semibold text-white mb-6">Emotional Profile</h2>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={emotionalProfile}>
                  <PolarGrid stroke="#ffffff20" />
                  <PolarAngleAxis dataKey="emotion" stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <PolarRadiusAxis stroke="#9ca3af" tick={{ fill: "#9ca3af" }} />
                  <Radar name="Emotion" dataKey="value" stroke="#ec4899" fill="#ec4899" fillOpacity={0.3} />
                </RadarChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Three Column Layout for Detailed Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column */}
            <div className="space-y-8">
              {/* Mood Meter */}
              <Card className="bg-white/5 border-white/10 p-6">
                <h2 className="text-2xl font-semibold text-white mb-6">Mood Meter</h2>
                <div className="space-y-4">
                  {Object.entries(mockExpandedData.moodMeter).map(([mood, value]) => (
                    <div key={mood} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400 capitalize text-base">{mood}</span>
                        <span className="text-white font-medium text-base">{value}%</span>
                      </div>
                      <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${moodColors[mood as keyof typeof moodColors]} transition-all duration-500`}
                          style={{ width: `${value}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Platform Breakdown */}
              <Card className="bg-white/5 border-white/10 p-6">
                <h2 className="text-2xl font-semibold text-white mb-6">Platform Breakdown</h2>
                <div className="space-y-4">
                  {mockExpandedData.platformBreakdown.map((platform, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400 text-lg">{platform.platform}</span>
                        <span className="text-white font-medium text-lg">{platform.percentage}%</span>
                      </div>
                      <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                          style={{ width: `${platform.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Right Column */}
            <div className="space-y-8">
              {/* Sentiment Trend */}
              <Card className="bg-white/5 border-white/10 p-6">
                <h2 className="text-2xl font-semibold text-white mb-6">Sentiment Trend</h2>
                <div className="h-32 flex items-end gap-2">
                  {mockExpandedData.sentimentTrend.map((value, index) => (
                    <div
                      key={index}
                      className="flex-1 bg-blue-500/30 rounded-t transition-all duration-300 hover:bg-blue-500/50"
                      style={{ height: `${value}%` }}
                    />
                  ))}
                </div>
                <p className="text-sm text-gray-500 mt-4">Past 12 hours</p>
              </Card>

              {/* Top Topics - Expanded */}
              <Card className="bg-white/5 border-white/10 p-6">
                <h2 className="text-2xl font-semibold text-white mb-6">Top Topics</h2>
                <div className="flex flex-wrap gap-3">
                  {mockExpandedData.topTopics.map((topic, index) => (
                    <Badge
                      key={index}
                      variant="outline"
                      className={`${sentimentColors[topic.sentiment]} cursor-pointer hover:scale-105 transition-transform text-sm py-2 px-3`}
                    >
                      #{topic.keyword}
                      <span className="ml-2 opacity-70">({topic.volume}k)</span>
                    </Badge>
                  ))}
                </div>
              </Card>

              {/* Engagement Stats */}
              <Card className="bg-white/5 border-white/10 p-6">
                <h2 className="text-2xl font-semibold text-white mb-6">Engagement Stats</h2>
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center p-6 bg-white/5 rounded-lg">
                    <p className="text-4xl font-bold text-white mb-2">
                      {(mockExpandedData.engagementStats.likes / 1000).toFixed(1)}k
                    </p>
                    <p className="text-sm text-gray-400">Likes</p>
                  </div>
                  <div className="text-center p-6 bg-white/5 rounded-lg">
                    <p className="text-4xl font-bold text-white mb-2">
                      {(mockExpandedData.engagementStats.shares / 1000).toFixed(1)}k
                    </p>
                    <p className="text-sm text-gray-400">Shares</p>
                  </div>
                  <div className="text-center p-6 bg-white/5 rounded-lg">
                    <p className="text-4xl font-bold text-white mb-2">
                      {(mockExpandedData.engagementStats.comments / 1000).toFixed(1)}k
                    </p>
                    <p className="text-sm text-gray-400">Comments</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Additional Column */}
            <div className="space-y-8">
              {/* Trending Hashtags */}
              <Card className="bg-white/5 border-white/10 p-6">
                <h2 className="text-2xl font-semibold text-white mb-6">Trending Hashtags</h2>
                <div className="space-y-3">
                  {trendingHashtags.map((hashtag, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <Badge
                          variant="outline"
                          className={sentimentColors[hashtag.sentiment as keyof typeof sentimentColors]}
                        >
                          {hashtag.tag}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        {hashtag.growth > 0 ? (
                          <TrendingUp className="w-4 h-4 text-green-400" />
                        ) : hashtag.growth < 0 ? (
                          <TrendingDown className="w-4 h-4 text-red-400" />
                        ) : (
                          <Minus className="w-4 h-4 text-gray-400" />
                        )}
                        <span
                          className={`text-sm font-medium ${hashtag.growth > 0 ? "text-green-400" : hashtag.growth < 0 ? "text-red-400" : "text-gray-400"}`}
                        >
                          {hashtag.growth > 0 ? "+" : ""}
                          {hashtag.growth}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Top Influencers */}
              <Card className="bg-white/5 border-white/10 p-6">
                <h2 className="text-2xl font-semibold text-white mb-6">Top Influencers</h2>
                <div className="space-y-3">
                  {topInfluencers.map((influencer, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                    >
                      <div>
                        <p className="text-white font-medium">{influencer.name}</p>
                        <p className="text-sm text-gray-400">{influencer.followers} followers</p>
                      </div>
                      <div className="text-right">
                        <p className="text-white font-semibold">{influencer.engagement}%</p>
                        <p className="text-xs text-gray-400">{influencer.posts} posts</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>

          {/* Enhanced Representative Content with Better Layout */}
          <Card className="bg-white/5 border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-white">Representative Content</h2>
              <Button variant="outline" className="border-white/10 text-gray-400 hover:bg-white/10 bg-transparent">
                View All
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockExpandedData.representativeContent.map((content, index) => renderContentCard(content, index))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
