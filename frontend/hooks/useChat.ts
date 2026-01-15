import { useState, useEffect, useCallback } from 'react'
import { chatWithAI, ChatRequest } from '../lib/api'
import { ChatMessage, ChatSession, IntakeFormData } from '../lib/models'
import { skincareStorage, generateId, createNewChatSession } from '../lib/storage'

type ChatState = {
  messages: ChatMessage[]
  loading: boolean
  error: string | null
  session: ChatSession | null
  hasIntakeData: boolean
}

export default function useChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    loading: false,
    error: null,
    session: null,
    hasIntakeData: false
  })

  // Initialize chat session from storage and monitor intake data changes
  useEffect(() => {
    const checkAndUpdateIntakeData = () => {
      const existingSession = skincareStorage.getChatSession()
      const intakeData = skincareStorage.getIntakeForm()

      console.log('useChat checking intake data:', intakeData)

      if (existingSession) {
        setState(prev => ({
          ...prev,
          session: existingSession,
          messages: existingSession.messages,
          hasIntakeData: !!intakeData
        }))
      } else if (intakeData) {
        // Create new session with intake data
        const newSession = createNewChatSession(intakeData)
        skincareStorage.saveChatSession(newSession)
        setState(prev => ({
          ...prev,
          session: newSession,
          hasIntakeData: true
        }))
      } else {
        setState(prev => ({
          ...prev,
          hasIntakeData: false
        }))
      }
    }

    checkAndUpdateIntakeData()

    // Set up an interval to check for intake data changes (for when user comes from form)
    const interval = setInterval(() => {
      // Check direct sessionStorage first
      const directCheck = sessionStorage.getItem('bobeutician_intake_form')
      let currentIntakeData = null

      if (directCheck) {
        try {
          currentIntakeData = JSON.parse(directCheck)
        } catch (e) {
          console.error('useChat parse error:', e)
        }
      }

      // Fallback to storage system
      if (!currentIntakeData) {
        currentIntakeData = skincareStorage.getIntakeForm()
      }

      setState(prev => {
        const hasData = !!currentIntakeData
        if (prev.hasIntakeData !== hasData) {
          console.log('useChat detected intake data change:', hasData, currentIntakeData)
          return { ...prev, hasIntakeData: hasData }
        }
        return prev
      })
    }, 1000) // Check every second for changes

    return () => clearInterval(interval)
  }, [])

  // Send message to AI (supports skincare, direct chat, and free-form chat modes)
  const sendMessage = useCallback(async (question: string, concern?: string, chatMode: 'skincare' | 'freeform' = 'skincare') => {
    if (!question.trim()) return

    setState(prev => ({ ...prev, loading: true, error: null }))

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: question,
      timestamp: new Date()
    }

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage]
    }))

    try {
      const intakeData = skincareStorage.getIntakeForm()
      const currentSession = state.session || createNewChatSession(intakeData)

      let response: any

      if (chatMode === 'freeform') {
        // Free-form ChatGPT-style chat mode
        const { chatFreeform } = await import('../lib/api')

        // Build conversation history from previous messages
        const conversationHistory = state.messages
          .slice(-10) // Last 10 messages for context
          .map(msg => `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`)
          .join('\n')

        response = await chatFreeform({
          question,
          conversation_history: conversationHistory,
          conversation_id: currentSession.id
        })
      } else {
        // Skincare mode - use SQL-backed retrieval pipeline
        const chatRequest: ChatRequest = {
          question,
          intake_data: intakeData || undefined,
          concern,
          conversation_id: currentSession.id
        }
        response = await chatWithAI(chatRequest)
      }

      // Create assistant message
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        user_profile: response.user_profile,
        confidence: response.recommendation_confidence,
        routine_suggestion: response.routine_suggestion,
        citations: response.citations
      }

      // Update state and storage
      const updatedMessages = [...state.messages, userMessage, assistantMessage]
      const updatedSession: ChatSession = {
        ...currentSession,
        messages: updatedMessages,
        updated_at: new Date()
      }

      setState(prev => ({
        ...prev,
        messages: updatedMessages,
        session: updatedSession,
        loading: false
      }))

      skincareStorage.saveChatSession(updatedSession)

    } catch (error) {
      console.error('Chat error:', error)
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to send message'
      }))
    }
  }, [state.session, state.messages])

  // Clear chat and start new session
  const clearChat = useCallback(() => {
    skincareStorage.clearChatSession()
    const intakeData = skincareStorage.getIntakeForm()
    const newSession = createNewChatSession(intakeData)

    setState({
      messages: [],
      loading: false,
      error: null,
      session: newSession,
      hasIntakeData: !!intakeData
    })

    skincareStorage.saveChatSession(newSession)
  }, [])

  // Update intake data in current session
  const updateIntakeData = useCallback((intakeData: IntakeFormData) => {
    skincareStorage.saveIntakeForm(intakeData)

    if (state.session) {
      const updatedSession = {
        ...state.session,
        intake_data: intakeData,
        updated_at: new Date()
      }

      setState(prev => ({
        ...prev,
        session: updatedSession,
        hasIntakeData: true
      }))

      skincareStorage.saveChatSession(updatedSession)
    }
  }, [state.session])

  // Get user profile summary
  const getUserProfile = useCallback(() => {
    return skincareStorage.getUserProfileSummary()
  }, [])

  return {
    messages: state.messages,
    loading: state.loading,
    error: state.error,
    session: state.session,
    hasIntakeData: state.hasIntakeData,
    sendMessage,
    clearChat,
    updateIntakeData,
    getUserProfile
  }
}

// Legacy hook for backward compatibility
export function useLegacyChat() {
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  async function send(question: string) {
    setLoading(true)
    setMessages(m => [...m, { id: Date.now(), text: question, role: 'user' }])

    try {
      // Get form data from session storage
      const intakeData = skincareStorage.getIntakeForm()

      // Include intake data in the request
      const { postQA } = await import('../lib/api')
      const res = await postQA({
        question,
        intake_data: intakeData
      })

      setMessages(m => [...m, {
        id: Date.now() + 1,
        text: res.answer,
        role: 'assistant',
        context_summary: res.context_summary,
        citations: res.citations
      }])
    } catch (error) {
      console.error('Legacy chat error:', error)
      setMessages(m => [...m, {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble responding right now.",
        role: 'assistant'
      }])
    } finally {
      setLoading(false)
    }
  }

  return { messages, send, loading }
}