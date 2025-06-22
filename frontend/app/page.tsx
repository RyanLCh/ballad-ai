"use client"

import React, { useState, useEffect, useRef, useMemo, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, FileText, X, Play, Pause, Square, RotateCcw } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

// Updated interfaces for timing data
interface WordTiming {
  word: string
  start: number
  end: number
  line: number
}

interface TextSegment {
  content: string
  isWord: boolean
  wordIndex: number
  lineIndex: number
  segmentIndex: number
  timing?: WordTiming
}

// Memoized component for rendering individual text segments
const TextSegment = React.memo(({
  segment,
  currentTime,
  isPlaying
}: {
  segment: TextSegment
  currentTime: number
  isPlaying: boolean
}) => {
  const isHighlighted = segment.isWord &&
    segment.timing &&
    isPlaying &&
    currentTime >= segment.timing.start &&
    currentTime <= segment.timing.end

  return (
    <span
      data-word-index={segment.isWord ? segment.wordIndex : undefined}
      className={`${isHighlighted ? "bg-yellow-300 text-yellow-900 px-1 rounded shadow-sm transition-all duration-200" : ""
        }`}
    >
      {segment.content}
    </span>
  )
})

TextSegment.displayName = "TextSegment"

// Memoized component for rendering text lines
const TextLine = React.memo(({
  segments,
  lineIndex,
  currentTime,
  isPlaying,
  isLastLine
}: {
  segments: TextSegment[]
  lineIndex: number
  currentTime: number
  isPlaying: boolean
  isLastLine: boolean
}) => {
  return (
    <div className="leading-relaxed">
      {segments.map((segment) => (
        <TextSegment
          key={`${segment.lineIndex}-${segment.segmentIndex}`}
          segment={segment}
          currentTime={currentTime}
          isPlaying={isPlaying}
        />
      ))}
      {!isLastLine && <br />}
    </div>
  )
})

TextLine.displayName = "TextLine"

// Memoized component for rendering the entire text content
const TextContent = React.memo(({
  textStructure,
  currentTime,
  isPlaying
}: {
  textStructure: TextSegment[][]
  currentTime: number
  isPlaying: boolean
}) => {
  return (
    <div className="text-gray-800 font-serif text-base">
      {textStructure.map((lineSegments, lineIndex) => (
        <TextLine
          key={lineIndex}
          segments={lineSegments}
          lineIndex={lineIndex}
          currentTime={currentTime}
          isPlaying={isPlaying}
          isLastLine={lineIndex === textStructure.length - 1}
        />
      ))}
    </div>
  )
})

TextContent.displayName = "TextContent"

export default function StoryReader() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [wordTimings, setWordTimings] = useState<WordTiming[]>([])
  const [fileName, setFileName] = useState("")
  const [isUploading, setIsUploading] = useState(false)

  // Timing states
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [totalDuration, setTotalDuration] = useState(0)

  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const textContainerRef = useRef<HTMLDivElement>(null)
  const startTimeRef = useRef<number>(0)
  const animationFrameRef = useRef<number | null>(null)

  // Memoize the text structure from word timing data
  const textStructure = useMemo(() => {
    if (!wordTimings.length) return []

    // Group words by line number
    const lineGroups: { [lineNumber: number]: WordTiming[] } = {}
    wordTimings.forEach((wordTiming) => {
      if (!lineGroups[wordTiming.line]) {
        lineGroups[wordTiming.line] = []
      }
      lineGroups[wordTiming.line].push(wordTiming)
    })

    // Convert to text structure with segments
    const lines = Object.keys(lineGroups)
      .sort((a, b) => parseInt(a) - parseInt(b))
      .map(lineNumber => lineGroups[parseInt(lineNumber)])

    return lines.map((lineWords, lineIndex) => {
      const segments: TextSegment[] = []

      lineWords.forEach((wordTiming, wordIndex) => {
        // Add the word segment
        segments.push({
          content: wordTiming.word,
          isWord: true,
          wordIndex: wordTimings.indexOf(wordTiming),
          lineIndex,
          segmentIndex: segments.length,
          timing: wordTiming
        })

        // Add space after word (except for last word in line)
        if (wordIndex < lineWords.length - 1) {
          segments.push({
            content: " ",
            isWord: false,
            wordIndex: -1,
            lineIndex,
            segmentIndex: segments.length
          })
        }
      })

      return segments
    })
  }, [wordTimings])

  // Calculate total duration from word timings
  useEffect(() => {
    if (wordTimings.length > 0) {
      const maxEndTime = Math.max(...wordTimings.map(w => w.end))
      setTotalDuration(maxEndTime)
    }
  }, [wordTimings])

  // Animation loop for time-based highlighting
  useEffect(() => {
    if (isPlaying) {
      const animate = () => {
        const elapsed = (Date.now() - startTimeRef.current) / 1000
        setCurrentTime(elapsed)

        if (elapsed < totalDuration) {
          animationFrameRef.current = requestAnimationFrame(animate)
        } else {
          setIsPlaying(false)
          setCurrentTime(totalDuration)
        }
      }

      startTimeRef.current = Date.now() - currentTime * 1000
      animationFrameRef.current = requestAnimationFrame(animate)
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [isPlaying, totalDuration])

  // Auto-scroll to keep highlighted word in view
  useEffect(() => {
    if (isPlaying && textContainerRef.current && scrollAreaRef.current) {
      // Find the currently highlighted word
      const currentWord = wordTimings.find(w =>
        currentTime >= w.start && currentTime <= w.end
      )

      if (currentWord) {
        const wordIndex = wordTimings.indexOf(currentWord)
        const highlightedElement = textContainerRef.current.querySelector(`[data-word-index="${wordIndex}"]`)

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
    }
  }, [currentTime, isPlaying, wordTimings])

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.type !== "text/plain") {
      alert("Please upload a .txt file")
      return
    }

    setIsUploading(true)
    setFileName(file.name)

    try {
      // Create FormData to send the file to the backend
      const formData = new FormData()
      formData.append('file', file)

      // Send the file to the backend API
      const response = await fetch('http://localhost:8000/texts', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`API request failed with status: ${response.status}`)
      }

      // Get the word timing data from the API response
      const wordTimingData: WordTiming[] = await response.json()

      if (!Array.isArray(wordTimingData) || wordTimingData.length === 0) {
        throw new Error('No word timing data received from API')
      }

      setWordTimings(wordTimingData)

      // Simulate a brief delay for better UX
      setTimeout(() => {
        setIsUploading(false)
        setIsModalOpen(false)
      }, 500)
    } catch (error) {
      console.error("Error uploading file to API:", error)
      setIsUploading(false)
      alert(`Error processing file: ${error instanceof Error ? error.message : 'Please try again.'}`)
    }
  }, [])

  const clearStory = useCallback(() => {
    setWordTimings([])
    setFileName("")
    setCurrentTime(0)
    setIsPlaying(false)
    setTotalDuration(0)
  }, [])

  const handlePlay = useCallback(() => {
    setIsPlaying(true)
  }, [])

  const handlePause = useCallback(() => {
    setIsPlaying(false)
  }, [])

  const handleStop = useCallback(() => {
    setIsPlaying(false)
    setCurrentTime(0)
  }, [])

  const handleRestart = useCallback(() => {
    setIsPlaying(false)
    setCurrentTime(0)
    setTimeout(() => {
      setIsPlaying(true)
    }, 100)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Story Reader</h1>
          <p className="text-gray-600">Upload a text file to read your story with guided highlighting</p>
        </div>

        {/* Upload Button */}
        {!wordTimings.length && (
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
        {wordTimings.length > 0 && (
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
              </div>

              <Button onClick={clearStory} variant="outline" size="sm" className="bg-white hover:bg-gray-50">
                <X className="w-4 h-4 mr-2" />
                Clear
              </Button>
            </div>

            {/* Progress indicator */}
            {totalDuration > 0 && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>
                    {Math.round(currentTime * 10) / 10}s / {Math.round(totalDuration * 10) / 10}s
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-amber-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(currentTime / totalDuration) * 100}%` }}
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
                    <TextContent
                      textStructure={textStructure}
                      currentTime={currentTime}
                      isPlaying={isPlaying}
                    />
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
                Choose a .txt file containing your story to display it with timed reading highlights.
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
                <strong>Tip:</strong> The story will be displayed with precise timing-based highlighting from your API.
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
