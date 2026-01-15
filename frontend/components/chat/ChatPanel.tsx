"use client"

import React from 'react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'

type ChatPanelProps = {
    allMessages: any[]
    loading: boolean
    error: string | null
    chatMode: 'skincare' | 'chat'
    handleSend: (text: string) => void
    sessionId: string
}

export default function ChatPanel({ allMessages, loading, error, chatMode, handleSend, sessionId }: ChatPanelProps) {
    // ChatPanel fills its parent; messages area scrolls internally
    const containerClass = `flex flex-col h-full min-h-0 overflow-hidden rounded-xl border bg-gray-50`

    return (
        <div className={containerClass}>
            {/* no expand controls in this simplified layout */}

            <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
                {allMessages.map((msg, i) => (
                    <MessageBubble key={i} text={msg.text} sender={msg.sender} confidence={msg.confidence} userProfile={msg.userProfile} routineSuggestion={msg.routineSuggestion} citations={msg.citations} />
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-2xl px-6 py-4 max-w-[80%] shadow-sm">
                            <div className="flex items-center space-x-3">
                                <div className="animate-spin rounded-full h-5 w-5 border-2 border-purple-500 border-t-transparent"></div>
                                <span className="text-gray-700 text-sm">{chatMode === 'chat' ? 'BoBeautician is thinking and generating a conversational response...' : 'Analyzing your skin profile and finding recommendations...'}</span>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="flex justify-start">
                        <div className="bg-red-50 border border-red-200 text-red-800 rounded-2xl px-6 py-4 max-w-[80%] shadow-sm">
                            <div className="flex items-start gap-3">
                                <span className="text-red-500">⚠️</span>
                                <div>
                                    <p className="font-medium text-sm">Oops! Something went wrong</p>
                                    <p className="text-sm mt-1">{error}</p>
                                    <button onClick={() => window.location.reload()} className="text-xs bg-red-600 text-white px-3 py-1 rounded-full mt-2 hover:bg-red-700 transition-colors">Try refreshing the page</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="border-t bg-white flex items-center gap-3 px-4 py-3 rounded-b-xl" style={{ zIndex: 70 }}>
                <div className="text-xs text-gray-500 w-28">{sessionId ? `Session #${sessionId.slice(-6)}` : ''}</div>
                <div className="flex-1">
                    <ChatInput
                        onSend={handleSend}
                        disabled={loading}
                        formClassName="flex gap-2 w-full"
                        inputClassName={`flex-1 border border-gray-200 px-4 py-3 rounded-lg`}
                        buttonClassName="bg-[#DEA193] text-white px-4 py-3 rounded-lg"
                    />
                </div>
            </div>
        </div>
    )
}
