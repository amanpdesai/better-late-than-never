"use client"

import { useEffect, useRef, useState, Suspense, type ComponentProps } from "react"
import { Canvas, useFrame, useLoader } from "@react-three/fiber"
import { OrbitControls, Stars, Html, useProgress } from "@react-three/drei"
import { TextureLoader, Vector3, Mesh } from "three"
import { OrbitControls as OrbitControlsImpl } from "three-stdlib"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Play, Pause, RotateCcw, ZoomIn, ZoomOut } from "lucide-react"
import { CountryInfoPanel } from "@/components/country-info-panel"
import { CountryMesh } from "@/components/country-mesh"
import { CountryTooltip } from "@/components/country-tooltip"
import { cn } from "@/lib/utils"
import countriesData from "@/data/countries-simple.json"

const EARTH_RADIUS = 0.85
const ATMOSPHERE_SCALE = 1.05
const PANEL_WIDTH_DESKTOP = 480
const PANEL_TRANSITION_MS = 320
type CountryPanelProps = ComponentProps<typeof CountryInfoPanel>

// Mock data for each country
const COUNTRY_DATA_MAP: Record<string, NonNullable<CountryPanelProps["countryData"]>> = {
  Russia: {
    name: "Russia",
    flag: "🇷🇺",
    lastUpdated: "Live · updated 1m ago",
    moodSummary: "Russian social media shows mixed sentiment with strong interest in technology and domestic politics.",
    moodMeter: { joy: 28, curiosity: 32, anger: 18, confusion: 12, sadness: 10 },
    sentimentTrend: [65, 67, 64, 66, 68, 67, 69, 68, 70, 71, 69, 72],
    topTopics: [
      { keyword: "TechInnovation", sentiment: "positive", volume: 245 },
      { keyword: "Politics", sentiment: "neutral", volume: 198 },
      { keyword: "Economy", sentiment: "negative", volume: 156 },
    ],
    representativeContent: [
      {
        title: "New Tech Hub Opens in Moscow",
        excerpt: "Major investment in AI and robotics expected to create thousands of jobs.",
        engagement: 42000,
        platform: "VK",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 456789, avgEngagement: 12.3, viralityScore: 76 },
    platformBreakdown: [
      { platform: "VK", percentage: 45 },
      { platform: "Telegram", percentage: 30 },
      { platform: "Twitter / X", percentage: 15 },
      { platform: "YouTube", percentage: 10 },
    ],
    engagementStats: { likes: 3200000, shares: 1400000, comments: 980000 },
  },
  Canada: {
    name: "Canada",
    flag: "🇨🇦",
    lastUpdated: "Live · updated 2m ago",
    moodSummary: "Canadian online conversations show optimism around environmental initiatives and social policies.",
    moodMeter: { joy: 42, curiosity: 28, anger: 8, confusion: 10, sadness: 12 },
    sentimentTrend: [72, 74, 73, 75, 76, 75, 77, 78, 76, 79, 80, 81],
    topTopics: [
      { keyword: "ClimateAction", sentiment: "positive", volume: 289 },
      { keyword: "Healthcare", sentiment: "positive", volume: 234 },
      { keyword: "Hockey", sentiment: "positive", volume: 187 },
    ],
    representativeContent: [
      {
        title: "Canada Leads in Clean Energy Investment",
        excerpt: "New federal funding aims to make Canada carbon-neutral by 2050.",
        engagement: 38500,
        platform: "CBC News",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 342156, avgEngagement: 16.7, viralityScore: 82 },
    platformBreakdown: [
      { platform: "Twitter / X", percentage: 35 },
      { platform: "Reddit", percentage: 28 },
      { platform: "Facebook", percentage: 22 },
      { platform: "Instagram", percentage: 15 },
    ],
    engagementStats: { likes: 2800000, shares: 1200000, comments: 890000 },
  },
  "United States": {
    name: "United States",
    flag: "🇺🇸",
    lastUpdated: "Live · updated 30s ago",
    moodSummary: "US social media reflects diverse opinions on tech innovation, politics, and cultural trends.",
    moodMeter: { joy: 32, curiosity: 24, anger: 22, confusion: 14, sadness: 8 },
    sentimentTrend: [70, 68, 69, 71, 70, 72, 71, 73, 72, 74, 73, 75],
    topTopics: [
      { keyword: "AIRevolution", sentiment: "positive", volume: 523 },
      { keyword: "Politics2024", sentiment: "neutral", volume: 487 },
      { keyword: "TechStocks", sentiment: "positive", volume: 356 },
    ],
    representativeContent: [
      {
        title: "Silicon Valley Unveils Next-Gen AI Model",
        excerpt: "Major breakthrough in natural language processing could transform industries.",
        engagement: 125000,
        platform: "Twitter",
        sentiment: "positive",
        type: "twitter",
        author: "@TechNews",
      },
    ],
    categoryMetrics: { totalPosts: 1245678, avgEngagement: 18.9, viralityScore: 92 },
    platformBreakdown: [
      { platform: "Twitter / X", percentage: 38 },
      { platform: "Reddit", percentage: 24 },
      { platform: "TikTok", percentage: 20 },
      { platform: "YouTube", percentage: 18 },
    ],
    engagementStats: { likes: 8900000, shares: 3400000, comments: 2100000 },
  },
  China: {
    name: "China",
    flag: "🇨🇳",
    lastUpdated: "Live · updated 3m ago",
    moodSummary: "Chinese social platforms show strong enthusiasm for technological advancement and economic growth.",
    moodMeter: { joy: 38, curiosity: 30, anger: 12, confusion: 10, sadness: 10 },
    sentimentTrend: [75, 76, 77, 78, 76, 79, 80, 78, 81, 82, 80, 83],
    topTopics: [
      { keyword: "5GTechnology", sentiment: "positive", volume: 678 },
      { keyword: "GreenEnergy", sentiment: "positive", volume: 542 },
      { keyword: "Innovation", sentiment: "positive", volume: 423 },
    ],
    representativeContent: [
      {
        title: "China Launches Advanced Space Station Module",
        excerpt: "New module enhances scientific research capabilities in orbit.",
        engagement: 245000,
        platform: "Weibo",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 2345678, avgEngagement: 22.4, viralityScore: 95 },
    platformBreakdown: [
      { platform: "WeChat", percentage: 42 },
      { platform: "Weibo", percentage: 35 },
      { platform: "Douyin", percentage: 18 },
      { platform: "Bilibili", percentage: 5 },
    ],
    engagementStats: { likes: 15000000, shares: 6700000, comments: 4200000 },
  },
  Brazil: {
    name: "Brazil",
    flag: "🇧🇷",
    lastUpdated: "Live · updated 1m ago",
    moodSummary: "Brazilian online discourse shows passion for sports, music, and environmental conservation efforts.",
    moodMeter: { joy: 45, curiosity: 22, anger: 15, confusion: 8, sadness: 10 },
    sentimentTrend: [71, 73, 72, 74, 75, 73, 76, 77, 75, 78, 79, 77],
    topTopics: [
      { keyword: "AmazonConservation", sentiment: "positive", volume: 312 },
      { keyword: "Futebol", sentiment: "positive", volume: 298 },
      { keyword: "Carnival2024", sentiment: "positive", volume: 245 },
    ],
    representativeContent: [
      {
        title: "Brazil Announces Major Rainforest Protection Plan",
        excerpt: "Government pledges billions to protect Amazon ecosystem and indigenous communities.",
        engagement: 87000,
        platform: "Twitter",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 678234, avgEngagement: 19.2, viralityScore: 87 },
    platformBreakdown: [
      { platform: "Twitter / X", percentage: 32 },
      { platform: "Instagram", percentage: 28 },
      { platform: "WhatsApp", percentage: 25 },
      { platform: "TikTok", percentage: 15 },
    ],
    engagementStats: { likes: 6200000, shares: 2800000, comments: 1900000 },
  },
  Australia: {
    name: "Australia",
    flag: "🇦🇺",
    lastUpdated: "Live · updated 2m ago",
    moodSummary: "Australian social media buzzes with beach culture, sports enthusiasm, and environmental awareness.",
    moodMeter: { joy: 48, curiosity: 24, anger: 10, confusion: 8, sadness: 10 },
    sentimentTrend: [76, 77, 78, 77, 79, 80, 78, 81, 80, 82, 81, 83],
    topTopics: [
      { keyword: "Cricket", sentiment: "positive", volume: 256 },
      { keyword: "ReefConservation", sentiment: "positive", volume: 198 },
      { keyword: "SurfLife", sentiment: "positive", volume: 167 },
    ],
    representativeContent: [
      {
        title: "Great Barrier Reef Shows Signs of Recovery",
        excerpt: "Marine biologists report positive coral regeneration after conservation efforts.",
        engagement: 52000,
        platform: "ABC News",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 287654, avgEngagement: 15.4, viralityScore: 81 },
    platformBreakdown: [
      { platform: "Instagram", percentage: 35 },
      { platform: "Facebook", percentage: 28 },
      { platform: "Twitter / X", percentage: 22 },
      { platform: "TikTok", percentage: 15 },
    ],
    engagementStats: { likes: 3100000, shares: 1300000, comments: 920000 },
  },
  India: {
    name: "India",
    flag: "🇮🇳",
    lastUpdated: "Live · updated 45s ago",
    moodSummary: "Indian digital sphere showcases vibrant discussions on tech startups, cricket, and cultural festivals.",
    moodMeter: { joy: 40, curiosity: 28, anger: 12, confusion: 10, sadness: 10 },
    sentimentTrend: [73, 75, 74, 76, 77, 76, 78, 79, 77, 80, 81, 79],
    topTopics: [
      { keyword: "StartupIndia", sentiment: "positive", volume: 512 },
      { keyword: "IPL2024", sentiment: "positive", volume: 487 },
      { keyword: "DigitalIndia", sentiment: "positive", volume: 398 },
    ],
    representativeContent: [
      {
        title: "Indian Tech Startups Secure Record Funding",
        excerpt: "Venture capital flows into AI and fintech sectors at unprecedented levels.",
        engagement: 98000,
        platform: "Economic Times",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 1876543, avgEngagement: 21.3, viralityScore: 94 },
    platformBreakdown: [
      { platform: "WhatsApp", percentage: 38 },
      { platform: "Instagram", percentage: 28 },
      { platform: "Twitter / X", percentage: 20 },
      { platform: "YouTube", percentage: 14 },
    ],
    engagementStats: { likes: 12500000, shares: 5600000, comments: 3800000 },
  },
  Argentina: {
    name: "Argentina",
    flag: "🇦🇷",
    lastUpdated: "Live · updated 3m ago",
    moodSummary: "Argentine social networks pulse with football passion, tango culture, and economic discussions.",
    moodMeter: { joy: 38, curiosity: 20, anger: 18, confusion: 14, sadness: 10 },
    sentimentTrend: [68, 70, 69, 71, 70, 72, 71, 73, 72, 74, 73, 75],
    topTopics: [
      { keyword: "Fútbol", sentiment: "positive", volume: 342 },
      { keyword: "TangoFestival", sentiment: "positive", volume: 234 },
      { keyword: "EconomíaDigital", sentiment: "neutral", volume: 198 },
    ],
    representativeContent: [
      {
        title: "Argentina Wins Copa America Qualifier",
        excerpt: "National team's stellar performance ignites celebration across the country.",
        engagement: 76000,
        platform: "TyC Sports",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 512876, avgEngagement: 17.8, viralityScore: 85 },
    platformBreakdown: [
      { platform: "Twitter / X", percentage: 36 },
      { platform: "Instagram", percentage: 32 },
      { platform: "Facebook", percentage: 20 },
      { platform: "TikTok", percentage: 12 },
    ],
    engagementStats: { likes: 4800000, shares: 2100000, comments: 1450000 },
  },
  Kazakhstan: {
    name: "Kazakhstan",
    flag: "🇰🇿",
    lastUpdated: "Live · updated 4m ago",
    moodSummary: "Kazakh online community focuses on modernization efforts and cultural heritage preservation.",
    moodMeter: { joy: 35, curiosity: 30, anger: 12, confusion: 13, sadness: 10 },
    sentimentTrend: [70, 71, 72, 71, 73, 74, 72, 75, 74, 76, 75, 77],
    topTopics: [
      { keyword: "DigitalKazakhstan", sentiment: "positive", volume: 187 },
      { keyword: "NomadCulture", sentiment: "positive", volume: 156 },
      { keyword: "SpaceProgram", sentiment: "positive", volume: 134 },
    ],
    representativeContent: [
      {
        title: "Kazakhstan Launches New Tech Hub in Astana",
        excerpt: "Government invests in innovation center to attract global tech companies.",
        engagement: 34000,
        platform: "Tengri News",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 198765, avgEngagement: 13.2, viralityScore: 72 },
    platformBreakdown: [
      { platform: "Telegram", percentage: 42 },
      { platform: "VK", percentage: 28 },
      { platform: "Instagram", percentage: 18 },
      { platform: "Twitter / X", percentage: 12 },
    ],
    engagementStats: { likes: 2100000, shares: 890000, comments: 620000 },
  },
  Algeria: {
    name: "Algeria",
    flag: "🇩🇿",
    lastUpdated: "Live · updated 5m ago",
    moodSummary: "Algerian digital conversations highlight youth movements, renewable energy, and cultural pride.",
    moodMeter: { joy: 32, curiosity: 26, anger: 16, confusion: 14, sadness: 12 },
    sentimentTrend: [67, 68, 69, 68, 70, 71, 69, 72, 71, 73, 72, 74],
    topTopics: [
      { keyword: "SolarEnergy", sentiment: "positive", volume: 213 },
      { keyword: "YouthVoice", sentiment: "neutral", volume: 189 },
      { keyword: "CulturalHeritage", sentiment: "positive", volume: 167 },
    ],
    representativeContent: [
      {
        title: "Algeria's Sahara Solar Project Expands",
        excerpt: "Massive solar farm aims to power North Africa and export to Europe.",
        engagement: 41000,
        platform: "Al Jazeera",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 234567, avgEngagement: 14.1, viralityScore: 74 },
    platformBreakdown: [
      { platform: "Facebook", percentage: 38 },
      { platform: "Instagram", percentage: 28 },
      { platform: "Twitter / X", percentage: 20 },
      { platform: "YouTube", percentage: 14 },
    ],
    engagementStats: { likes: 2600000, shares: 1100000, comments: 750000 },
  },
  "Democratic Republic of Congo": {
    name: "Democratic Republic of Congo",
    flag: "🇨🇩",
    lastUpdated: "Live · updated 6m ago",
    moodSummary: "Congolese social media centers on music culture, natural resources, and community development.",
    moodMeter: { joy: 36, curiosity: 24, anger: 18, confusion: 12, sadness: 10 },
    sentimentTrend: [65, 66, 67, 66, 68, 69, 67, 70, 69, 71, 70, 72],
    topTopics: [
      { keyword: "CongoMusic", sentiment: "positive", volume: 198 },
      { keyword: "CommunityDev", sentiment: "positive", volume: 167 },
      { keyword: "ResourceRights", sentiment: "neutral", volume: 145 },
    ],
    representativeContent: [
      {
        title: "Congolese Music Festival Goes Global",
        excerpt: "Local artists gain international recognition, showcasing rich cultural heritage.",
        engagement: 38000,
        platform: "Radio Okapi",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 156789, avgEngagement: 12.8, viralityScore: 70 },
    platformBreakdown: [
      { platform: "Facebook", percentage: 45 },
      { platform: "WhatsApp", percentage: 30 },
      { platform: "Twitter / X", percentage: 15 },
      { platform: "Instagram", percentage: 10 },
    ],
    engagementStats: { likes: 1800000, shares: 780000, comments: 540000 },
  },
  "Saudi Arabia": {
    name: "Saudi Arabia",
    flag: "🇸🇦",
    lastUpdated: "Live · updated 2m ago",
    moodSummary: "Saudi social platforms highlight Vision 2030 progress, entertainment growth, and tech innovation.",
    moodMeter: { joy: 42, curiosity: 28, anger: 10, confusion: 10, sadness: 10 },
    sentimentTrend: [74, 75, 76, 75, 77, 78, 76, 79, 78, 80, 79, 81],
    topTopics: [
      { keyword: "Vision2030", sentiment: "positive", volume: 387 },
      { keyword: "EntertainmentSector", sentiment: "positive", volume: 298 },
      { keyword: "SmartCities", sentiment: "positive", volume: 267 },
    ],
    representativeContent: [
      {
        title: "NEOM Smart City Reaches Major Milestone",
        excerpt: "Futuristic urban development showcases Saudi Arabia's ambitious transformation.",
        engagement: 89000,
        platform: "Arab News",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 567890, avgEngagement: 19.6, viralityScore: 88 },
    platformBreakdown: [
      { platform: "Twitter / X", percentage: 42 },
      { platform: "Instagram", percentage: 28 },
      { platform: "Snapchat", percentage: 18 },
      { platform: "TikTok", percentage: 12 },
    ],
    engagementStats: { likes: 5800000, shares: 2400000, comments: 1650000 },
  },
  Mexico: {
    name: "Mexico",
    flag: "🇲🇽",
    lastUpdated: "Live · updated 1m ago",
    moodSummary: "Mexican digital sphere celebrates cultural traditions, food heritage, and creative industries.",
    moodMeter: { joy: 44, curiosity: 26, anger: 12, confusion: 10, sadness: 8 },
    sentimentTrend: [72, 73, 74, 73, 75, 76, 74, 77, 76, 78, 77, 79],
    topTopics: [
      { keyword: "DíaDeMuertos", sentiment: "positive", volume: 412 },
      { keyword: "TacoTuesday", sentiment: "positive", volume: 356 },
      { keyword: "MexicanCinema", sentiment: "positive", volume: 287 },
    ],
    representativeContent: [
      {
        title: "Mexican Film Wins International Award",
        excerpt: "Director's latest work praised for authentic storytelling and visual mastery.",
        engagement: 72000,
        platform: "Milenio",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 789234, avgEngagement: 18.4, viralityScore: 86 },
    platformBreakdown: [
      { platform: "Facebook", percentage: 35 },
      { platform: "WhatsApp", percentage: 28 },
      { platform: "Instagram", percentage: 22 },
      { platform: "TikTok", percentage: 15 },
    ],
    engagementStats: { likes: 6800000, shares: 2900000, comments: 1980000 },
  },
  Indonesia: {
    name: "Indonesia",
    flag: "🇮🇩",
    lastUpdated: "Live · updated 2m ago",
    moodSummary: "Indonesian social networks thrive with diverse content spanning tech startups to traditional culture.",
    moodMeter: { joy: 46, curiosity: 26, anger: 10, confusion: 10, sadness: 8 },
    sentimentTrend: [75, 76, 77, 76, 78, 79, 77, 80, 79, 81, 80, 82],
    topTopics: [
      { keyword: "TechJakarta", sentiment: "positive", volume: 498 },
      { keyword: "BatikFashion", sentiment: "positive", volume: 376 },
      { keyword: "IslandParadise", sentiment: "positive", volume: 334 },
    ],
    representativeContent: [
      {
        title: "Indonesian Unicorns Lead Southeast Asian Tech Boom",
        excerpt: "Homegrown startups achieve billion-dollar valuations, transforming regional economy.",
        engagement: 112000,
        platform: "Kompas",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 1567890, avgEngagement: 20.8, viralityScore: 91 },
    platformBreakdown: [
      { platform: "Instagram", percentage: 36 },
      { platform: "TikTok", percentage: 28 },
      { platform: "WhatsApp", percentage: 22 },
      { platform: "Twitter / X", percentage: 14 },
    ],
    engagementStats: { likes: 11200000, shares: 4900000, comments: 3400000 },
  },
  Libya: {
    name: "Libya",
    flag: "🇱🇾",
    lastUpdated: "Live · updated 7m ago",
    moodSummary: "Libyan online discussions focus on rebuilding efforts, cultural preservation, and youth initiatives.",
    moodMeter: { joy: 28, curiosity: 24, anger: 20, confusion: 16, sadness: 12 },
    sentimentTrend: [64, 65, 66, 65, 67, 68, 66, 69, 68, 70, 69, 71],
    topTopics: [
      { keyword: "Reconstruction", sentiment: "neutral", volume: 178 },
      { keyword: "Heritage", sentiment: "positive", volume: 145 },
      { keyword: "YouthInitiatives", sentiment: "positive", volume: 123 },
    ],
    representativeContent: [
      {
        title: "Libyan Youth Launch Community Rebuilding Project",
        excerpt: "Grassroots movement aims to restore historic sites and public spaces.",
        engagement: 29000,
        platform: "Libya Observer",
        sentiment: "positive",
        type: "news",
        thumbnail: "/placeholder.svg",
      },
    ],
    categoryMetrics: { totalPosts: 123456, avgEngagement: 11.4, viralityScore: 65 },
    platformBreakdown: [
      { platform: "Facebook", percentage: 48 },
      { platform: "WhatsApp", percentage: 28 },
      { platform: "Twitter / X", percentage: 16 },
      { platform: "Instagram", percentage: 8 },
    ],
    engagementStats: { likes: 1400000, shares: 590000, comments: 410000 },
  },
}

const GLOBAL_MOOD_PANEL_DATA: NonNullable<CountryPanelProps["countryData"]> = {
  name: "Global Mood Index",
  flag: "🌍",
  lastUpdated: "Live · updated 2m ago",
  moodSummary:
    "Real-time social sentiment shows an optimistic tone across major regions. Curiosity around AI breakthroughs and sustainability leads the conversation while concern over data privacy keeps a cautious undertone.",
  moodMeter: {
    joy: 34,
    curiosity: 26,
    anger: 14,
    confusion: 12,
    sadness: 14,
  },
  sentimentTrend: [68, 70, 69, 71, 73, 72, 75, 74, 73, 76, 78, 79],
  topTopics: [
    { keyword: "AIRevolution", sentiment: "positive", volume: 312 },
    { keyword: "ClimateAction", sentiment: "positive", volume: 188 },
    { keyword: "DataPrivacy", sentiment: "neutral", volume: 142 },
    { keyword: "SpaceTech", sentiment: "positive", volume: 117 },
    { keyword: "GlobalEconomy", sentiment: "negative", volume: 96 },
    { keyword: "Wellbeing", sentiment: "positive", volume: 84 },
  ],
  representativeContent: [
    {
      title: "UN Climate Accord Gains Momentum After Landmark Vote",
      excerpt: "Global leaders rally behind a sweeping plan to accelerate clean tech investments through 2030.",
      engagement: 56200,
      platform: "YouTube",
      sentiment: "positive",
      timestamp: "Just now",
      type: "video",
      thumbnail: "/ai-technology-breakthrough.jpg",
      author: "PlanetWatch",
      views: 1250000,
      url: "https://example.com/video",
    },
    {
      title: "How do you stay optimistic about the future of work?",
      excerpt: "Remote-first teams share rituals that keep distributed cultures energized and connected.",
      engagement: 31800,
      platform: "Reddit",
      sentiment: "neutral",
      timestamp: "10 minutes ago",
      type: "reddit",
      upvotes: 9200,
      comments: 1430,
      source: "futureofwork",
      url: "https://example.com/thread",
    },
    {
      title: "Global privacy bill sparks debate among tech giants",
      excerpt: "New guardrails would standardize data collection rules across 45 countries starting next year.",
      engagement: 28750,
      platform: "World News",
      sentiment: "neutral",
      timestamp: "35 minutes ago",
      type: "news",
      thumbnail: "/data-privacy-concerns.jpg",
      source: "Global Desk",
      url: "https://example.com/article",
    },
    {
      title: "Space-based solar farms just hit a new efficiency record ☀️🛰️",
      excerpt:
        "Prototype arrays beamed down enough power for 4,000 homes. Feels like sci-fi becoming real life. #SpaceTech",
      engagement: 22100,
      platform: "Twitter",
      sentiment: "positive",
      timestamp: "1 hour ago",
      type: "twitter",
      author: "@orbital_jess",
      url: "https://example.com/post",
    },
  ],
  categoryMetrics: {
    totalPosts: 872345,
    avgEngagement: 14.8,
    viralityScore: 88,
  },
  platformBreakdown: [
    { platform: "Twitter / X", percentage: 32 },
    { platform: "Reddit", percentage: 21 },
    { platform: "TikTok", percentage: 19 },
    { platform: "YouTube", percentage: 17 },
    { platform: "News", percentage: 11 },
  ],
  engagementStats: {
    likes: 5200000,
    shares: 2100000,
    comments: 1650000,
  },
}

function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="flex flex-col items-center space-y-4">
        <div className="w-32 h-32 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-white text-lg font-medium">Loading Earth... {Math.round(progress)}%</p>
      </div>
    </Html>
  )
}

export default function Component() {
  const [autoRotate, setAutoRotate] = useState(true)
  const [panelMounted, setPanelMounted] = useState(false)
  const [panelOpen, setPanelOpen] = useState(false)
  const [panelCategory, setPanelCategory] = useState<CountryPanelProps["category"]>("Memes")
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null)
  const [isDesktop, setIsDesktop] = useState(false)
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null)
  const [tooltipVisible, setTooltipVisible] = useState(false)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isMouseDown, setIsMouseDown] = useState(false)
  const controlsRef = useRef<OrbitControlsImpl>(null)
  const closeTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)")
    const update = () => setIsDesktop(media.matches)
    update()
    media.addEventListener("change", update)
    return () => media.removeEventListener("change", update)
  }, [])

  useEffect(() => {
    const offsetValue = panelOpen && isDesktop ? `${PANEL_WIDTH_DESKTOP}px` : "0px"
    document.body.style.setProperty("--panel-offset", offsetValue)
  }, [panelOpen, isDesktop])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }

    const handleMouseDown = () => {
      setIsMouseDown(true)
      setTooltipVisible(false)
    }

    const handleMouseUp = () => {
      setIsMouseDown(false)
    }

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mousedown", handleMouseDown)
    window.addEventListener("mouseup", handleMouseUp)

    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mousedown", handleMouseDown)
      window.removeEventListener("mouseup", handleMouseUp)
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current)
      }
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
      document.body.style.removeProperty("--panel-offset")
    }
  }, [])

  const handleOpenPanel = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
    }
    if (!panelMounted) {
      setPanelMounted(true)
      requestAnimationFrame(() => setPanelOpen(true))
    } else {
      setPanelOpen(true)
    }
  }

  const handleCountryClick = (countryName: string) => {
    console.log("==============================================")
    console.log("🌍 COUNTRY CLICKED:", countryName)
    console.log("==============================================")
    console.log("Country Code:", countriesData.features.find(f => f.properties.name === countryName)?.properties.code)
    console.log("Country Data Available:", !!COUNTRY_DATA_MAP[countryName])
    if (COUNTRY_DATA_MAP[countryName]) {
      console.log("Flag:", COUNTRY_DATA_MAP[countryName].flag)
      console.log("Mood Summary:", COUNTRY_DATA_MAP[countryName].moodSummary)
      console.log("Total Posts:", COUNTRY_DATA_MAP[countryName].categoryMetrics.totalPosts.toLocaleString())
      console.log("Virality Score:", COUNTRY_DATA_MAP[countryName].categoryMetrics.viralityScore)
    }
    console.log("==============================================")
    setSelectedCountry(countryName)
    handleOpenPanel()
  }

  const handleCountryHover = (countryName: string | null) => {
    // Clear any existing hover timeout
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current)
    }

    setHoveredCountry(countryName)

    if (countryName && !isMouseDown) {
      // Debounce: only show tooltip after 300ms of hovering
      hoverTimeoutRef.current = setTimeout(() => {
        setTooltipVisible(true)
      }, 300)
    } else {
      // Immediately hide tooltip when not hovering or mouse is down
      setTooltipVisible(false)
    }
  }

  const handleClosePanel = () => {
    setPanelOpen(false)
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
    }
    closeTimeoutRef.current = setTimeout(() => {
      setPanelMounted(false)
    }, PANEL_TRANSITION_MS)
  }

  const handleReset = () => {
    if (controlsRef.current) {
      controlsRef.current.reset()
    }
  }

  const handleZoomIn = () => {
    if (controlsRef.current) {
      const camera = controlsRef.current.object
      const direction = new Vector3()
      camera.getWorldDirection(direction)
      camera.position.addScaledVector(direction, 0.5)
      controlsRef.current.update()
    }
  }

  const handleZoomOut = () => {
    if (controlsRef.current) {
      const camera = controlsRef.current.object
      const direction = new Vector3()
      camera.getWorldDirection(direction)
      camera.position.addScaledVector(direction, -0.5)
      controlsRef.current.update()
    }
  }

  const desktopOffset = panelOpen && isDesktop ? PANEL_WIDTH_DESKTOP : 0

  return (
    <div
      className={cn(
        "relative h-screen bg-gradient-to-b from-black via-gray-900 to-black overflow-hidden transition-all duration-500 ease-in-out",
      )}
      style={
        isDesktop
          ? {
              width: `calc(100% - ${desktopOffset}px)`,
              marginRight: `${desktopOffset}px`,
            }
          : undefined
      }
    >
      {/* Global Mood toggle */}
      <div className="absolute top-6 right-6 z-20 flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          className="border-none bg-white/10 text-white hover:bg-white/20 hover:border-white/40 mt-20"
          onClick={handleOpenPanel}
        >
          View Global Mood
        </Button>
      </div>

      {/* Controls Panel */}
      <div className="absolute bottom-6 left-6 z-10">
        <Card className="bg-black/70 border-white/20 backdrop-blur-sm p-4">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setAutoRotate(!autoRotate)}
              className="text-white hover:bg-white/10"
            >
              {autoRotate ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleReset} className="text-white hover:bg-white/10">
              <RotateCcw className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleZoomIn} className="text-white hover:bg-white/10">
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleZoomOut} className="text-white hover:bg-white/10">
              <ZoomOut className="w-4 h-4" />
            </Button>
          </div>
          <div className="mt-3 text-xs text-gray-400">
            <p>Left click: Rotate • Scroll: Zoom • Right click: Pan</p>
          </div>
        </Card>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 3], fov: 45 }} gl={{ antialias: true, alpha: true }} dpr={[1, 2]}>
        <Suspense fallback={<Loader />}>
          {/* Enhanced Lighting */}
          <ambientLight intensity={0.6} color="#ffffff" />
          <directionalLight
            position={[5, 3, 5]}
            intensity={1.5}
            color="#ffffff"
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-5, -3, -5]} intensity={0.5} color="#ffffff" />

          {/* Earth with Atmosphere */}
          <Earth autoRotate={autoRotate} onCountryClick={handleCountryClick} onCountryHover={handleCountryHover} />
          <Atmosphere />

          {/* Enhanced Starfield */}
          <Stars radius={300} depth={60} count={25000} factor={8} saturation={0} fade speed={0.5} />

          {/* Orbit Controls */}
          <OrbitControls
            ref={controlsRef}
            enableZoom={true}
            enablePan={true}
            enableRotate={true}
            autoRotate={autoRotate}
            autoRotateSpeed={0.3}
            minDistance={1.8}
            maxDistance={8}
            enableDamping={true}
            dampingFactor={0.05}
            rotateSpeed={0.5}
            zoomSpeed={0.8}
            panSpeed={0.8}
          />
        </Suspense>
      </Canvas>

      {/* Subtle Grid Overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-5">
        <div className="w-full h-full bg-[radial-gradient(circle_at_center,transparent_0%,rgba(255,255,255,0.1)_100%)]"></div>
      </div>

      {panelMounted && (
        <CountryInfoPanel
          countryData={selectedCountry ? COUNTRY_DATA_MAP[selectedCountry] || GLOBAL_MOOD_PANEL_DATA : GLOBAL_MOOD_PANEL_DATA}
          category={panelCategory}
          onCategoryChange={setPanelCategory}
          onClose={handleClosePanel}
          showFullPageLink={false}
          isOpen={panelOpen}
        />
      )}

      {/* Country Hover Tooltip */}
      {hoveredCountry && COUNTRY_DATA_MAP[hoveredCountry] && (
        <CountryTooltip
          countryName={hoveredCountry}
          countryFlag={COUNTRY_DATA_MAP[hoveredCountry].flag}
          position={mousePosition}
          visible={tooltipVisible && !isMouseDown}
        />
      )}
    </div>
  )
}

function Earth({
  autoRotate,
  onCountryClick,
  onCountryHover
}: {
  autoRotate: boolean;
  onCountryClick: (countryName: string) => void;
  onCountryHover: (countryName: string | null) => void;
}) {
  const meshRef = useRef<Mesh>(null)
  const groupRef = useRef<any>(null)
  const earthTexture = useLoader(TextureLoader, "/assets/3d/texture_earth.jpg")

  useFrame((state, delta) => {
    if (meshRef.current && autoRotate) {
      meshRef.current.rotation.y += delta * 0.05
    }
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y += delta * 0.05
    }
  })

  return (
    <>
      <mesh ref={meshRef} castShadow receiveShadow>
        <sphereGeometry args={[EARTH_RADIUS, 128, 128]} />
        <meshStandardMaterial map={earthTexture} roughness={0.7} metalness={0.1} bumpScale={0.05} transparent={false} />
      </mesh>

      {/* Country overlays */}
      <group ref={groupRef}>
        {countriesData.features.map((feature) => (
          <CountryMesh
            key={feature.properties.code}
            name={feature.properties.name}
            coordinates={feature.geometry.coordinates}
            radius={EARTH_RADIUS}
            onClick={onCountryClick}
            onHover={onCountryHover}
            color="#3b82f6"
            hoverColor="#60a5fa"
          />
        ))}
      </group>
    </>
  )
}

function Atmosphere() {
  return (
    <mesh>
      <sphereGeometry args={[EARTH_RADIUS * ATMOSPHERE_SCALE, 64, 64]} />
      <meshBasicMaterial color="#4a90e2" transparent={true} opacity={0.1} side={2} />
    </mesh>
  )
}
