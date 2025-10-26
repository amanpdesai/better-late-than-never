"use client"

import { Navbar } from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Sparkles, ImageIcon, Type, Palette, CheckCircle2, Send, Loader2 } from "lucide-react"
import { useState, useEffect } from "react"
import ReactMarkdown from "react-markdown"

type MessageRole = "user" | "assistant"
type ContentType = "text" | "tool-call" | "markdown" | "image" | "video" | "pipeline" | "error"

interface MessageContent {
  type: ContentType
  content: string
  toolName?: string
  imageUrl?: string
  videoUrl?: string
  stages?: Array<{
    id: number
    name: string
    status: "pending" | "running" | "completed" | "failed"
    description: string
  }>
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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

export default function USAMemeGeneratorPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  // Debug logging
  if (process.env.NEXT_PUBLIC_DEBUG === "true") {
    console.log("🔧 Frontend Debug Info:")
    console.log("  API URL:", API_BASE_URL)
    console.log("  Environment:", process.env.NODE_ENV)
  }

  const generateId = () => Math.random().toString(36).substr(2, 9)

  const addMessage = (role: MessageRole, contents: MessageContent[]) => {
    const newMessage: Message = {
      id: generateId(),
      role,
      contents
    }
    setMessages(prev => [...prev, newMessage])
    return newMessage.id
  }

  const updatePipelineStage = (messageId: string, stageId: number, status: "running" | "completed" | "failed", description?: string) => {
    setMessages(prev => prev.map(msg => {
      if (msg.id === messageId) {
        return {
          ...msg,
          contents: msg.contents.map(content => {
            if (content.type === "pipeline" && content.stages) {
              return {
                ...content,
                stages: content.stages.map(stage => {
                  if (stage.id === stageId) {
                    return {
                      ...stage,
                      status,
                      description: description || stage.description
                    }
                  }
                  return stage
                })
              }
            }
            return content
          })
        }
      }
      return msg
    }))
  }

  const simulatePipelineProgress = async (pipelineId: string) => {
    // Stage 1: Understanding
    await new Promise(resolve => setTimeout(resolve, 1000))
    updatePipelineStage(pipelineId, 1, "running", "Analyzing your request...")
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    updatePipelineStage(pipelineId, 1, "completed", "Classified content type")
    
    // Stage 2: Concept
    await new Promise(resolve => setTimeout(resolve, 500))
    updatePipelineStage(pipelineId, 2, "running", "Selecting relevant clusters...")
    
    await new Promise(resolve => setTimeout(resolve, 2000))
    updatePipelineStage(pipelineId, 2, "completed", "Selected relevant clusters")
    
    // Stage 3: Text
    await new Promise(resolve => setTimeout(resolve, 500))
    updatePipelineStage(pipelineId, 3, "running", "Generating contextual text...")
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    updatePipelineStage(pipelineId, 3, "completed", "Generated contextual text")
    
    // Stage 4: Design
    await new Promise(resolve => setTimeout(resolve, 500))
    updatePipelineStage(pipelineId, 4, "running", "Creating final meme...")
  }

  const generateMeme = async (prompt: string) => {
    setIsLoading(true)
    
    // Add user message
    addMessage("user", [{ type: "text", content: prompt }])
    
    // Add initial pipeline message
    const pipelineId = addMessage("assistant", [{
      type: "pipeline",
      content: "",
      stages: [
        { id: 1, name: "Understanding", status: "pending", description: "Analyzing your request" },
        { id: 2, name: "Concept", status: "pending", description: "Generating meme concept" },
        { id: 3, name: "Text", status: "pending", description: "Crafting witty text" },
        { id: 4, name: "Design", status: "pending", description: "Finalizing meme design" }
      ]
    }])

    // Start pipeline simulation
    const pipelinePromise = simulatePipelineProgress(pipelineId)

    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      })

      const data = await response.json()

      // Wait for pipeline simulation to complete
      await pipelinePromise

      if (data.status === "success") {
        // Complete the final stage
        updatePipelineStage(pipelineId, 4, "completed", `Created ${data.content_type} meme`)
        
        // Add success message
        const content: MessageContent = {
          type: data.content_type === "image" ? "image" : "video",
          content: `Generated your ${data.content_type} meme!`,
          imageUrl: data.content_type === "image" ? `data:image/png;base64,${data.data}` : undefined,
          videoUrl: data.content_type === "video" ? `data:video/mp4;base64,${data.data}` : undefined
        }
        
        addMessage("assistant", [content])
      } else {
        // Mark current stage as failed
        updatePipelineStage(pipelineId, 4, "failed", "Generation failed")
        
        // Add error message
        addMessage("assistant", [{
          type: "error",
          content: `Error: ${data.message}`
        }])
      }
    } catch (error) {
      // Mark current stage as failed
      updatePipelineStage(pipelineId, 4, "failed", "Network error")
      
      // Add error message with better error handling
      let errorMessage = "Unknown error"
      if (error instanceof Error) {
        errorMessage = error.message
      } else if (typeof error === 'string') {
        errorMessage = error
      } else if (error && typeof error === 'object' && 'message' in error) {
        errorMessage = String(error.message)
      }
      
      addMessage("assistant", [{
        type: "error",
        content: `Error: ${errorMessage}`
      }])
    } finally {
      setIsLoading(false)
    }
  }

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
                            {(content.stages || PIPELINE_STAGES.map(s => ({ ...s, status: "pending" as const, description: s.description }))).map((stage, index) => {
                              const Icon = PIPELINE_STAGES.find(s => s.id === stage.id)?.icon || Sparkles
                              const isLast = index === (content.stages || PIPELINE_STAGES).length - 1
                              
                              // Determine status styling
                              let statusColor = "bg-white/20"
                              let statusIcon = null
                              let statusText = ""
                              
                              const stageStatus = "status" in stage ? stage.status : "pending"
                              
                              if (stageStatus === "completed") {
                                statusColor = "bg-green-500/20 border-green-500/30"
                                statusIcon = <CheckCircle2 className="w-6 h-6 text-green-400" />
                                statusText = "Completed"
                              } else if (stageStatus === "running") {
                                statusColor = "bg-blue-500/20 border-blue-500/30"
                                statusIcon = <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
                                statusText = "Running"
                              } else if (stageStatus === "failed") {
                                statusColor = "bg-red-500/20 border-red-500/30"
                                statusIcon = <div className="w-6 h-6 text-red-400">✕</div>
                                statusText = "Failed"
                              } else {
                                statusColor = "bg-white/20 border-white/20"
                                statusIcon = <div className="w-6 h-6 text-gray-400">○</div>
                                statusText = "Pending"
                              }
                              
                              return (
                                <div key={stage.id} className="flex items-center">
                                  <div className="flex flex-col items-center">
                                    <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center ${statusColor}`}>
                                      {statusIcon}
                                    </div>
                                    {!isLast && (
                                      <div className={`w-0.5 h-8 mt-2 ${
                                        stageStatus === "completed" ? "bg-green-400/50" : 
                                        stageStatus === "running" ? "bg-blue-400/50" :
                                        stageStatus === "failed" ? "bg-red-400/50" : "bg-white/20"
                                      }`}></div>
                                    )}
                                  </div>
                                  <div className="ml-4 flex-1">
                                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                                      <div className="flex items-center gap-3 mb-2">
                                        <Icon className="w-5 h-5 text-blue-400" />
                                        <h3 className="font-semibold text-sm text-white">{stage.name}</h3>
                                        <span className={`text-xs px-2 py-1 rounded-full ${
                                          stageStatus === "completed" ? "bg-green-500/20 text-green-300" :
                                          stageStatus === "running" ? "bg-blue-500/20 text-blue-300" :
                                          stageStatus === "failed" ? "bg-red-500/20 text-red-300" :
                                          "bg-gray-500/20 text-gray-300"
                                        }`}>
                                          {statusText}
                                        </span>
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

                    {/* Video Content */}
                    {content.type === "video" && (
                      <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                        <div className="px-4 py-3 border-b border-white/10">
                          <p className="text-sm text-gray-300">{content.content}</p>
                        </div>
                        <div className="p-2">
                          <video
                            src={content.videoUrl}
                            controls
                            className="w-full rounded-lg"
                            autoPlay
                            muted
                            loop
                          >
                            Your browser does not support the video tag.
                          </video>
                        </div>
                      </div>
                    )}

                    {/* Error Content */}
                    {content.type === "error" && (
                      <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-red-400 rounded-full" />
                          <p className="text-sm text-red-300">{content.content}</p>
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
                  if (input.trim() && !isLoading) {
                    generateMeme(input.trim())
                    setInput("")
                  }
                }
              }}
            />
            <Button
              className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-6"
              disabled={!input.trim() || isLoading}
              onClick={() => {
                if (input.trim() && !isLoading) {
                  generateMeme(input.trim())
                  setInput("")
                }
              }}
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {isLoading ? "Generating your meme..." : "Describe the meme you want to create"}
          </p>
        </div>
      </div>
    </div>
  )
}
