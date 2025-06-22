"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, FileText, X, Play, Pause, Square, RotateCcw } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function StoryReader() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [storyText, setStoryText] = useState("")
  const [fileName, setFileName] = useState("")
  const [isUploading, setIsUploading] = useState(false)

  // Highlighting states
  const [words, setWords] = useState<string[]>([])
  const [currentWordIndex, setCurrentWordIndex] = useState(-1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1000) // milliseconds per word

  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const textContainerRef = useRef<HTMLDivElement>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Split text into words when story is loaded
  useEffect(() => {
    if (storyText) {
      const wordArray = storyText.split(/(\s+)/).filter((word) => word.trim().length > 0)
      setWords(wordArray)
      setCurrentWordIndex(-1)
    }
  }, [storyText])

  // Handle highlighting interval
  useEffect(() => {
    if (isPlaying && words.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentWordIndex((prev) => {
          if (prev >= words.length - 1) {
            setIsPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, speed)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isPlaying, words.length, speed])

  // Auto-scroll to keep highlighted word in view
  useEffect(() => {
    if (currentWordIndex >= 0 && textContainerRef.current && scrollAreaRef.current) {
      const highlightedElement = textContainerRef.current.querySelector(`[data-word-index="${currentWordIndex}"]`)
      if (highlightedElement) {
        const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
        if (scrollContainer) {
          const containerRect = scrollContainer.getBoundingClientRect()
          const elementRect = highlightedElement.getBoundingClientRect()

          // Calculate the position to center the highlighted word
          const containerCenter = containerRect.height / 2
          const elementTop = elementRect.top - containerRect.top + scrollContainer.scrollTop
          const scrollTo = elementTop - containerCenter

          scrollContainer.scrollTo({
            top: Math.max(0, scrollTo),
            behavior: "smooth",
          })
        }
      }
    }
  }, [currentWordIndex])

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.type !== "text/plain") {
      alert("Please upload a .txt file")
      return
    }

    setIsUploading(true)
    setFileName(file.name)

    try {
      const text = await file.text()
      setStoryText(text)

      // Simulate upload delay for better UX
      setTimeout(() => {
        setIsUploading(false)
        setIsModalOpen(false)
      }, 1000)
    } catch (error) {
      console.error("Error reading file:", error)
      setIsUploading(false)
      alert("Error reading file. Please try again.")
    }
  }

  const clearStory = () => {
    setStoryText("")
    setFileName("")
    setWords([])
    setCurrentWordIndex(-1)
    setIsPlaying(false)
  }

  const handlePlay = () => {
    if (currentWordIndex === -1) {
      setCurrentWordIndex(0)
    }
    setIsPlaying(true)
  }

  const handlePause = () => {
    setIsPlaying(false)
  }

  const handleStop = () => {
    setIsPlaying(false)
    setCurrentWordIndex(-1)
  }

  const handleRestart = () => {
    setIsPlaying(false)
    setCurrentWordIndex(-1)
    setTimeout(() => {
      setCurrentWordIndex(0)
      setIsPlaying(true)
    }, 100)
  }

  const renderHighlightedText = () => {
    if (!storyText || words.length === 0) return null

    let wordIndex = 0
    const lines = storyText.split("\n")

    return lines.map((line, lineIndex) => {
      const lineWords = line.split(/(\s+)/)
      const renderedLine = lineWords.map((segment, segmentIndex) => {
        if (segment.trim().length === 0) {
          return <span key={`${lineIndex}-${segmentIndex}`}>{segment}</span>
        }

        const isHighlighted = wordIndex === currentWordIndex
        const currentIndex = wordIndex
        wordIndex++

        return (
          <span
            key={`${lineIndex}-${segmentIndex}`}
            data-word-index={currentIndex}
            className={`${
              isHighlighted ? "bg-yellow-300 text-yellow-900 px-1 rounded shadow-sm transition-all duration-200" : ""
            }`}
          >
            {segment}
          </span>
        )
      })

      return (
        <div key={lineIndex} className="leading-relaxed">
          {renderedLine}
          {lineIndex < lines.length - 1 && <br />}
        </div>
      )
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Story Reader</h1>
          <p className="text-gray-600">Upload a text file to read your story with guided highlighting</p>
        </div>

        {/* Upload Button */}
        {!storyText && (
          <div className="text-center">
            <Button
              onClick={() => setIsModalOpen(true)}
              size="lg"
              className="bg-amber-600 hover:bg-amber-700 text-white px-8 py-3"
            >
              <Upload className="w-5 h-5 mr-2" />
              Upload Story
            </Button>
          </div>
        )}

        {/* Story Display */}
        {storyText && (
          <div className="relative">
            {/* Controls */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                {!isPlaying ? (
                  <Button onClick={handlePlay} size="sm" className="bg-green-600 hover:bg-green-700 text-white">
                    <Play className="w-4 h-4 mr-1" />
                    Play
                  </Button>
                ) : (
                  <Button onClick={handlePause} size="sm" className="bg-orange-600 hover:bg-orange-700 text-white">
                    <Pause className="w-4 h-4 mr-1" />
                    Pause
                  </Button>
                )}

                <Button onClick={handleStop} size="sm" variant="outline">
                  <Square className="w-4 h-4 mr-1" />
                  Stop
                </Button>

                <Button onClick={handleRestart} size="sm" variant="outline">
                  <RotateCcw className="w-4 h-4 mr-1" />
                  Restart
                </Button>

                {/* Speed Control */}
                <div className="flex items-center gap-2 ml-4">
                  <Label htmlFor="speed" className="text-sm">
                    Speed:
                  </Label>
                  <select
                    id="speed"
                    value={speed}
                    onChange={(e) => setSpeed(Number(e.target.value))}
                    className="text-sm border border-gray-300 rounded px-2 py-1"
                  >
                    <option value={2000}>Slow (2s)</option>
                    <option value={1500}>Normal (1.5s)</option>
                    <option value={1000}>Fast (1s)</option>
                    <option value={500}>Very Fast (0.5s)</option>
                  </select>
                </div>
              </div>

              <Button onClick={clearStory} variant="outline" size="sm" className="bg-white hover:bg-gray-50">
                <X className="w-4 h-4 mr-2" />
                Clear
              </Button>
            </div>

            {/* Progress indicator */}
            {words.length > 0 && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>
                    {currentWordIndex + 1} / {words.length} words
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-amber-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentWordIndex + 1) / words.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Paper-like container */}
            <div className="bg-white shadow-2xl rounded-lg overflow-hidden border border-gray-200">
              {/* Paper header */}
              <div className="bg-gray-50 px-8 py-4 border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-gray-600" />
                  <h2 className="text-lg font-semibold text-gray-800">{fileName}</h2>
                </div>
              </div>

              {/* Story content */}
              <ScrollArea className="h-[600px]" ref={scrollAreaRef}>
                <div className="p-8" ref={textContainerRef}>
                  <div className="prose prose-lg max-w-none">
                    <div className="text-gray-800 font-serif text-base">{renderHighlightedText()}</div>
                  </div>
                </div>
              </ScrollArea>

              {/* Paper footer with decorative lines */}
              <div className="bg-gray-50 px-8 py-3 border-t border-gray-200">
                <div className="flex justify-center space-x-2">
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Modal */}
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Upload Your Story</DialogTitle>
              <DialogDescription>
                Choose a .txt file containing your story to display it with guided reading highlights.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="story-file">Story File (.txt)</Label>
                <Input
                  id="story-file"
                  type="file"
                  accept=".txt"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                  className="cursor-pointer"
                />
              </div>

              {isUploading && (
                <div className="flex items-center justify-center py-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-amber-600 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm text-gray-600">Processing your story...</span>
                  </div>
                </div>
              )}

              <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-md">
                <strong>Tip:</strong> The story will be displayed with word-by-word highlighting to guide your reading
                pace.
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
