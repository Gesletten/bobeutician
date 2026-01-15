"use client"

import { useEffect, useState, useRef } from 'react'
import InfoPanel from './InfoPanel'
import ChatPanel from './ChatPanel'
import useChat from '../../hooks/useChat'
import { skincareStorage } from '../../lib/storage'
import { IntakeFormData } from '../../lib/models'

export default function ChatWindow() {
  const {
    messages,
    loading,
    error,
    hasIntakeData,
    sendMessage,
    clearChat
  } = useChat()

  const [intakeData, setIntakeData] = useState<IntakeFormData | null>(null)
  const [showProfile, setShowProfile] = useState(true)
  const [chatMode, setChatMode] = useState<'skincare' | 'chat'>('skincare') // New mode state
  const [sessionId, setSessionId] = useState<string>('')
  const containerRef = useRef<HTMLDivElement | null>(null)
  // We'll compute header geometry and use a centered chat container
  const [containerMaxHeight, setContainerMaxHeight] = useState<number | null>(null)


  const prettifyLabel = (s: string | undefined | null) => {
    if (!s) return ''
    return s.replace(/_/g, ' ').replace(/\s+/g, ' ').trim().replace(/(^|\s)\S/g, l => l.toUpperCase())
  }

  // Load intake data on mount and setup chat-specific auto-clearing
  useEffect(() => {
    console.log('ChatWindow mounted - loading intake data')

    const loadIntakeData = () => {
      console.log('About to load intake form data...')

      // First try direct sessionStorage access
      const directData = sessionStorage.getItem('bobeutician_intake_form')
      console.log('Direct sessionStorage data:', directData)
      if (directData) {
        try {
          const parsedData = JSON.parse(directData)
          console.log('Parsed direct data:', parsedData)
          setIntakeData(parsedData)
          return
        } catch (e) {
          console.error('Failed to parse direct data:', e)
        }
      }

      // Fallback to storage system
      const data = skincareStorage.getIntakeForm()
      console.log('Storage system data:', data)
      setIntakeData(data)
    }

    // Load initially
    loadIntakeData()

    // Set session ID
    setSessionId(Date.now().toString())

    // compute header bottom and available space; keep chat as a centered card (not full-screen)
    function computeLayout() {
      const headerEl = document.querySelector('header') as HTMLElement | null
      const headerBottom = headerEl ? Math.round(headerEl.getBoundingClientRect().bottom) : 64
      const padding = 48 // total vertical padding from top and bottom
      const maxH = Math.min(Math.round(window.innerHeight * 0.82), Math.max(520, Math.round(window.innerHeight - headerBottom - padding)))
      setContainerMaxHeight(maxH)

      // Keep info panel inside the chat container; sizing handled by CSS
    }

    computeLayout()
    window.addEventListener('resize', computeLayout)


    // Setup auto-clearing only for chat interface close/reload
    const handleBeforeUnload = () => {
      console.log('Chat interface closing - clearing all data')
      skincareStorage.clearAll()
    }

    // Add event listener for actual page unload (close or reload)
    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      // Clean up event listeners but don't clear data on normal navigation
      window.removeEventListener('beforeunload', handleBeforeUnload)
      window.removeEventListener('resize', () => { })
      console.log('ChatWindow unmounting - data preserved for navigation')
    }
  }, [])

  // Force reload intake data when component mounts or updates
  useEffect(() => {
    const loadAndUpdateIntakeData = () => {
      const data = skincareStorage.getIntakeForm()
      console.log('Intake data force reload:', data)
      setIntakeData(data)

      // Force re-render by updating state
      if (data) {
        console.log('Intake data found - updating chat interface')
      } else {
        console.log('No intake data found')
      }
    }

    loadAndUpdateIntakeData()
  }, [hasIntakeData])

  // Function to manually reload intake data
  const reloadIntakeData = () => {
    console.log('Manual reload triggered')

    // Debug storage first
    console.log('All sessionStorage keys:', Object.keys(sessionStorage))

    const directData = sessionStorage.getItem('bobeutician_intake_form')
    console.log('Direct sessionStorage data:', directData)

    if (directData) {
      try {
        const parsedData = JSON.parse(directData)
        console.log('Manual reload success:', parsedData)
        setIntakeData(parsedData)
      } catch (e) {
        console.error('Manual reload parse error:', e)
        setIntakeData(null)
      }
    } else {
      console.log('No data in sessionStorage')
      setIntakeData(null)
    }
  }

  // Also update when the window gains focus (user returns from form)
  useEffect(() => {
    const handleFocus = () => {
      console.log('Chat window focused - checking for new intake data')
      reloadIntakeData()
    }

    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [])

  // Convert chat messages to display format
  const displayMessages = messages.map(msg => ({
    text: msg.content,
    sender: msg.role === 'user' ? 'user' as const : 'chat' as const,
    confidence: msg.confidence,
    userProfile: msg.user_profile,
    routineSuggestion: msg.routine_suggestion,
    citations: msg.citations
  }))

  // Add welcome message if no messages (dynamically updates based on intakeData state)
  let welcomeText = "Welcome to BoBeutician!\n\nI'm your AI skincare consultant, ready to help you achieve your best skin.\n\nFor the most personalized recommendations, please complete your intake form first.\n\nOr feel free to ask me general skincare questions right away!\n\nHow can I help you today?"
  if (intakeData) {
    const concerns = intakeData.concerns && intakeData.concerns.length > 0 ? (', with concerns: ' + intakeData.concerns.map(c => prettifyLabel(c)).join(', ')) : ''
    welcomeText = 'Welcome to your personalized skincare consultation!\n\nI can see your profile: ' + prettifyLabel(intakeData.skin_type) + ' skin' + (intakeData.sensitive === 'yes' ? ', Sensitive' : '') + concerns + '.\n\nYou can ask me about product recommendations, ingredient advice, routines, or managing your specific concerns.\n\nWhat would you like to know about skincare today?'
  }

  const allMessages = displayMessages.length === 0
    ? [{ text: welcomeText, sender: 'chat' as const }]
    : displayMessages
  // Handle sending messages to backend
  async function handleSend(userText: string) {
    if (!userText.trim()) return

    // Use the chatMode to determine which mode to use
    const mode = chatMode === 'chat' ? 'freeform' : 'skincare'

    sendMessage(userText, undefined, mode).catch(error => {
      console.error('Failed to send message:', error)
    })
  }

  return (
    <div className="w-full h-full flex justify-center items-center p-4 overflow-hidden">
      <div ref={containerRef} className="bg-white rounded-2xl shadow-lg flex flex-col overflow-hidden" style={{ width: '98vw', height: containerMaxHeight ? `${containerMaxHeight}px` : 'calc(100vh - 120px)', maxHeight: containerMaxHeight ? `${containerMaxHeight}px` : 'calc(100vh - 120px)' }}>
        {/* Mode Toggle */}
        <div className="border-b bg-gray-50 p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-700">Mode:</span>
              <div className="flex bg-gray-200 rounded-lg p-1">
                <button
                  onClick={() => setChatMode('skincare')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${chatMode === 'skincare'
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                    }`}
                >
                  🧴 Skincare Mode
                </button>
                <button
                  onClick={() => setChatMode('chat')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${chatMode === 'chat'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                    }`}
                >
                  💬 Chat Mode
                </button>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Fresh session button */}
              <button
                onClick={() => {
                  const fresh = skincareStorage.startFreshSession()
                  setSessionId(fresh.session_id)
                  clearChat()
                  setIntakeData(null)
                  window.location.reload()
                }}
                className="text-xs bg-red-500 text-white px-3 py-1 rounded-full hover:bg-red-600 transition-colors"
                title="Start completely fresh session"
              >
                🔄 Fresh Session
              </button>

              {/* Mode description */}
              <div className="text-xs text-gray-500 text-right max-w-xs">
                {chatMode === 'skincare'
                  ? 'Structured product recommendations from database'
                  : 'Free-form conversational AI like ChatGPT'
                }
              </div>
            </div>
          </div>

          {sessionId && (
            <div className="mt-2 text-xs text-gray-400 text-center">
              <div className="flex items-center justify-center gap-3">
                <span>Session #{sessionId.slice(-6)} | Data persists until you close this chat interface</span>
              </div>
            </div>
          )}
        </div>
        {/* Main content grid: Chat left (2/3), Info right (1/3) */}
        <div className="flex-1 overflow-hidden flex flex-col md:flex-row gap-4 p-4">
          {/* ChatPanel on the left */}
          <div className="md:w-3/4 w-full flex flex-col min-h-0 overflow-hidden">
            <ChatPanel
              allMessages={allMessages}
              loading={loading}
              error={error}
              chatMode={chatMode}
              handleSend={handleSend}
              sessionId={sessionId}
            />
          </div>

          {/* InfoPanel on the right */}
          <div className="md:w-1/4 w-full min-h-0 overflow-auto rounded-xl bg-gradient-to-br from-blue-50 to-purple-50 border p-4">
            <InfoPanel intakeData={intakeData} showProfile={showProfile} setShowProfile={setShowProfile} reloadIntakeData={reloadIntakeData} />
          </div>
        </div>
      </div>
    </div>
  );
}