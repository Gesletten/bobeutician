import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MessageBubbleProps {
  text: string
  sender: "user" | "chat"
  confidence?: number
  userProfile?: string
  routineSuggestion?: string
  citations?: Array<{ id: string; source: string; score?: number }>
}

export default function MessageBubble({
  text,
  sender,
  confidence,
  citations
}: MessageBubbleProps) {
  const bubbleColor = sender === "chat" ? "bg-[#EECEC7]" : "bg-[#F2E4E2]"
  const isUser = sender === "user"

  const sanitizeForDisplay = (s: string) => {
    if (!s) return s
    return s.replace(/_/g, ' ').replace(/\r\n/g, '\n').replace(/\s+$/g, '').replace(/\n{3,}/g, '\n\n')
  }

  const formatChatbotText = (rawText: string) => {
    if (sender === "user") return <div className="text-sm">{sanitizeForDisplay(rawText)}</div>

    if (rawText && rawText.toLowerCase().includes("technical difficulties")) {
      return (
        <div className="mb-2 p-3 bg-red-100 border border-red-300 rounded-lg">
          <p className="text-sm text-red-700 font-semibold">⚠️ Sorry, the AI is currently unavailable. Please try again later or contact support if the issue persists.</p>
        </div>
      )
    }

    const normalized = sanitizeForDisplay(rawText)

    const sections = normalized.split(/(?=\n\n|YOUR PROFILE:|🎯|✨|📋|💡|⚠️|🌟|SUGGESTED ROUTINE|MORNING:|EVENING:)/g)

    const Markdown = ({ children }: { children: string }) => (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ _node, ...props }: any) => <a {...props} target="_blank" rel="noreferrer" className="text-blue-600 underline" />,
          code: ({ _node, inline, _className, children, ...props }: any) => (
            <code className={`bg-gray-100 rounded px-1 py-0.5 text-xs ${inline ? '' : 'block p-2 font-mono'}`} {...props}>{children}</code>
          ),
          ul: ({ _node, ...props }: any) => <ul className="list-disc ml-5 space-y-1 text-sm" {...props} />,
          ol: ({ _node, ...props }: any) => <ol className="list-decimal ml-5 space-y-1 text-sm" {...props} />,
          p: ({ _node, ...props }: any) => <p className="text-sm leading-relaxed mb-1" {...props} />
        }}
      >
        {children}
      </ReactMarkdown>
    )

    return sections.map((section, index) => {
      const trimmed = section.trim()
      if (!trimmed) return null

      if (trimmed.startsWith('YOUR PROFILE:')) {
        const content = trimmed.replace('YOUR PROFILE:', '').trim()
        return (
          <div key={index} className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">👤</span>
              <p className="text-sm font-semibold text-blue-800">Your Profile</p>
            </div>
            <div className="text-sm text-blue-700 whitespace-pre-line">
              <Markdown>{content}</Markdown>
            </div>
          </div>
        )
      }

      if (trimmed.startsWith('🎯') || trimmed.startsWith('✨') || trimmed.startsWith('🌟')) {
        return (
          <div key={index} className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-start gap-3">
              <div className="text-2xl leading-none">{trimmed.charAt(0)}</div>
              <div className="text-sm text-green-800">
                <Markdown>{trimmed}</Markdown>
              </div>
            </div>
          </div>
        )
      }

      if (trimmed.includes('SUGGESTED ROUTINE') || trimmed.includes('MORNING:') || trimmed.includes('EVENING:')) {
        return (
          <div key={index} className="mb-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">📋</span>
              <p className="text-sm font-semibold text-purple-800">Suggested Routine</p>
            </div>
            <div className="text-sm text-purple-800 whitespace-pre-line font-mono">
              <Markdown>{trimmed}</Markdown>
            </div>
          </div>
        )
      }

      if (trimmed.match(/^\d+\./) || trimmed.startsWith('•') || trimmed.startsWith('-')) {
        return (
          <div key={index} className="mb-3 pl-2">
            <div className="flex items-start gap-2 mb-1">
              <span className="text-lg">📝</span>
              <div className="text-sm text-[#321711]">
                <Markdown>{trimmed}</Markdown>
              </div>
            </div>
          </div>
        )
      }

      return (
        <div key={index} className="mb-4">
          <div className="flex items-start gap-3 mb-1">
            <div className="text-sm leading-relaxed prose prose-sm max-w-none text-[#321711]">
              <Markdown>{trimmed}</Markdown>
            </div>
          </div>
        </div>
      )
    }).filter(Boolean)
  }

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`px-5 p-4 rounded-2xl ${bubbleColor} max-w-[85%] w-fit text-[#321711]`}>
        {sender === "chat" ? (
          <div className="space-y-2">
            <div className="text-sm">
              {formatChatbotText(text)}
            </div>

            {(!text.toLowerCase().includes("technical difficulties")) && confidence && confidence > 0 && (
              <div className="mt-3 pt-2 border-t border-gray-300">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-600">Confidence:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full ${confidence >= 0.7 ? 'bg-green-500' :
                        confidence >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                      style={{ width: `${confidence * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-gray-600">{Math.round(confidence * 100)}%</span>
                </div>
              </div>
            )}

            {(!text.toLowerCase().includes("technical difficulties")) && citations && citations.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-300">
                <p className="text-xs text-gray-600 mb-1">Sources:</p>
                <div className="flex flex-wrap gap-1">
                  {citations.slice(0, 3).map((citation, idx) => (
                    <span key={idx} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">
                      #{idx + 1}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-sm">{text}</div>
        )}
      </div>
    </div>
  )
}