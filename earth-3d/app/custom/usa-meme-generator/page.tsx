"use client"

import { Navbar } from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Sparkles, ImageIcon, Type, Palette, CheckCircle2, Send } from "lucide-react"
import { useState } from "react"
import ReactMarkdown from "react-markdown"

type MessageRole = "user" | "assistant"
type ContentType = "text" | "tool-call" | "markdown" | "image" | "pipeline"

interface MessageContent {
  type: ContentType
  content: string
  toolName?: string
  imageUrl?: string
}

interface Message {
  id: string
  role: MessageRole
  contents: MessageContent[]
}

const PIPELINE_STAGES = [
  { id: 1, name: "Understanding", icon: Sparkles, description: "Analyzing your request" },
  { id: 2, name: "Concept", icon: ImageIcon, description: "Generating meme concept" },
  { id: 3, name: "Text", icon: Type, description: "Crafting witty text" },
  { id: 4, name: "Design", icon: Palette, description: "Finalizing meme design" },
]

const DEMO_CONVERSATION: Message[] = [
  {
    id: "1",
    role: "user",
    contents: [{ type: "text", content: "Create a funny meme about American coffee culture" }],
  },
  {
    id: "2",
    role: "assistant",
    contents: [
      { type: "tool-call", content: "Analyzing American coffee culture references...", toolName: "analyze_culture" },
      {
        type: "tool-call",
        content: "Searching for popular coffee meme formats...",
        toolName: "search_meme_formats",
      },
    ],
  },
  {
    id: "3",
    role: "assistant",
    contents: [
      {
        type: "markdown",
        content: `## Meme Concept

**Format:** Distracted Boyfriend

**Theme:** American Coffee Addiction

**Layout:**
- **Boyfriend:** Average American
- **Girlfriend:** Regular Coffee
- **Other Woman:** Extra Large Iced Coffee with 5 pumps of vanilla

**Top Text:** "Me trying to cut back on caffeine"
**Bottom Text:** "Also me at 2 PM"`,
      },
    ],
  },
  {
    id: "4",
    role: "assistant",
    contents: [{ type: "pipeline", content: "" }],
  },
  {
    id: "5",
    role: "assistant",
    contents: [
      {
        type: "image",
        content: "Generated your USA coffee culture meme!",
        imageUrl: "/distracted-boyfriend-meme-about-american-coffee-cu.jpg",
      },
    ],
  },
]

export default function USAMemeGeneratorPage() {
  const [messages] = useState<Message[]>(DEMO_CONVERSATION)
  const [input, setInput] = useState("")

  return (
    <div className="min-h-screen bg-black flex flex-col">
      <Navbar />

      <main className="flex-1 container mx-auto px-6 pt-24 pb-24 flex flex-col max-w-5xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🇺🇸</div>
          <h1 className="text-4xl font-bold text-white mb-2">USA Meme Generator</h1>
          <p className="text-gray-400 text-balance">
            Create hilarious USA-themed memes powered by AI. Watch our intelligent pipeline in action.
          </p>
        </div>

        {/* Chat Messages Container */}
        <div className="flex-1 overflow-y-auto mb-6 space-y-4">
          {messages.map((message, index) => (
            <div key={message.id} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              {message.role === "assistant" && (
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-blue-500 flex items-center justify-center flex-shrink-0 text-xl">
                  🤖
                </div>
              )}

              <div
                className={`flex flex-col gap-2 max-w-[80%] ${message.role === "user" ? "items-end" : "items-start"}`}
              >
                {message.contents.map((content, contentIndex) => (
                  <div key={contentIndex} className="w-full">
                    {/* Text Content */}
                    {content.type === "text" && (
                      <div
                        className={`rounded-2xl px-5 py-3 ${
                          message.role === "user"
                            ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white"
                            : "bg-white/5 border border-white/10 text-gray-200"
                        }`}
                      >
                        <p className="text-[15px] leading-relaxed">{content.content}</p>
                      </div>
                    )}

                    {/* Tool Call Content */}
                    {content.type === "tool-call" && (
                      <div className="bg-white/5 border border-purple-500/30 rounded-xl px-4 py-3 flex items-center gap-3">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
                        <div className="flex-1">
                          <p className="text-xs text-purple-300 font-medium mb-0.5">{content.toolName}</p>
                          <p className="text-sm text-gray-300">{content.content}</p>
                        </div>
                      </div>
                    )}

                    {/* Markdown Content */}
                    {content.type === "markdown" && (
                      <div className="bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 rounded-xl px-5 py-4">
                        <div className="prose prose-invert prose-sm max-w-none">
                          <ReactMarkdown
                            components={{
                            h2: ({ children }) => (
                              <h2 className="text-xl font-bold text-white mb-3 mt-0">{children}</h2>
                            ),
                            p: ({ children }) => <p className="text-gray-300 mb-2 last:mb-0">{children}</p>,
                            strong: ({ children }) => (
                              <strong className="text-blue-300 font-semibold">{children}</strong>
                            ),
                            ul: ({ children }) => <ul className="space-y-1 ml-4">{children}</ul>,
                            li: ({ children }) => <li className="text-gray-300 text-sm">{children}</li>,
                          }}
                          >
                            {content.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}

                    {/* Pipeline Content */}
                    {content.type === "pipeline" && (
                      <Card className="bg-white/5 border border-white/10">
                        <CardContent className="pt-6">
                          <div className="flex flex-col space-y-4">
                            {PIPELINE_STAGES.map((stage, index) => {
                              const Icon = stage.icon
                              const isLast = index === PIPELINE_STAGES.length - 1
                              return (
                                <div key={stage.id} className="flex items-center">
                                  <div className="flex flex-col items-center">
                                    <div className="w-12 h-12 rounded-full bg-blue-500/20 border-2 border-blue-500/30 flex items-center justify-center">
                                      <CheckCircle2 className="w-6 h-6 text-blue-400" />
                                    </div>
                                    {!isLast && (
                                      <div className="w-0.5 h-8 bg-white/20 mt-2"></div>
                                    )}
                                  </div>
                                  <div className="ml-4 flex-1">
                                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                                      <div className="flex items-center gap-3 mb-2">
                                        <Icon className="w-5 h-5 text-blue-400" />
                                        <h3 className="font-semibold text-sm text-white">{stage.name}</h3>
                                      </div>
                                      <p className="text-xs text-gray-400">{stage.description}</p>
                                    </div>
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Image Content */}
                    {content.type === "image" && (
                      <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                        <div className="px-4 py-3 border-b border-white/10">
                          <p className="text-sm text-gray-300">{content.content}</p>
                        </div>
                        <div className="p-2">
                          <img
                            src={content.imageUrl || "/placeholder.svg"}
                            alt="Generated meme"
                            className="w-full rounded-lg"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {message.role === "user" && (
                <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 text-xl">
                  👤
                </div>
              )}
            </div>
          ))}
        </div>
      </main>

      {/* Fixed Input Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-black/80 backdrop-blur-md border-t border-white/10 p-4">
        <div className="container mx-auto max-w-5xl">
          <div className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe the meme you want to create..."
              className="flex-1 bg-white/5 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-blue-500"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  // Demo mode - input doesn't actually send
                }
              }}
            />
            <Button
              className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-6"
              disabled
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            This is a demo interface showing example interactions
          </p>
        </div>
      </div>
    </div>
  )
}
