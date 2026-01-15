import { IntakeFormData, ChatSession, ChatMessage } from './models'

// Storage keys
const STORAGE_KEYS = {
  INTAKE_FORM: 'bobeutician_intake_form',
  CHAT_SESSION: 'bobeutician_chat_session',
  USER_PREFERENCES: 'bobeutician_preferences',
} as const

// Enhanced session storage functions with debugging
export function saveSession(key: string, value: any) {
  try {

    if (value === null || value === undefined) {
      sessionStorage.removeItem(key)

    } else {
      const serialized = JSON.stringify(value)
      sessionStorage.setItem(key, serialized)


      // Verify the save worked
      const verification = sessionStorage.getItem(key)
      if (verification) {

      } else {

      }
    }
  } catch (e) {

  }
}

export function loadSession(key: string) {
  try {
    const raw = sessionStorage.getItem(key)


    if (raw === null) {

      return null
    }

    const parsed = JSON.parse(raw)

    return parsed
  } catch (e) {

    return null
  }
}

export function clearSession(key: string) {
  try {
    sessionStorage.removeItem(key)

  } catch (e) {

  }
}

// Enhanced storage with chat-specific clearing (only clears when chat interface closes)
export const skincareStorage = {
  // Intake Form Management with debugging
  saveIntakeForm(data: IntakeFormData) {


    // Validate data before saving
    if (!data.skin_type || !data.sensitive) {

      return false
    }

    // Add timestamp if missing
    const dataToSave = {
      ...data,
      completed_at: data.completed_at || new Date().toISOString()
    }

    saveSession(STORAGE_KEYS.INTAKE_FORM, dataToSave)

    // Verify save worked
    const verification = this.getIntakeForm()
    if (verification) {

      return true
    } else {

      return false
    }
  },

  getIntakeForm(): IntakeFormData | null {

    const result = loadSession(STORAGE_KEYS.INTAKE_FORM)

    return result
  },

  // Debug function to check what's in storage
  debugStorage() {
    // Log current storage contents for debugging purposes
    Object.values(STORAGE_KEYS).forEach(key => {
      const raw = sessionStorage.getItem(key)
      console.log('storage debug', key, raw)
    })

  },

  // Force set data for testing
  testSaveIntakeForm() {
    const testData: IntakeFormData = {
      skin_type: 'oily',
      sensitive: 'no',
      concerns: ['acne', 'aging'],
      completed_at: new Date().toISOString()
    }


    this.saveIntakeForm(testData)

    const loaded = this.getIntakeForm()


    return loaded !== null
  },

  clearIntakeForm() {
    clearSession(STORAGE_KEYS.INTAKE_FORM)
  },

  // Chat Session Management
  saveChatSession(session: ChatSession) {
    const sessionData = {
      ...session,
      messages: session.messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp.toISOString()
      }))
    }
    saveSession(STORAGE_KEYS.CHAT_SESSION, sessionData)
  },

  getChatSession(): ChatSession | null {
    const stored = loadSession(STORAGE_KEYS.CHAT_SESSION)
    if (!stored) return null

    try {
      return {
        ...stored,
        created_at: new Date(stored.created_at),
        updated_at: new Date(stored.updated_at),
        messages: stored.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      }
    } catch {
      return null
    }
  },

  clearChatSession() {
    clearSession(STORAGE_KEYS.CHAT_SESSION)
  },

  // Add message to existing session
  addMessage(message: ChatMessage) {
    const session = this.getChatSession()
    if (session) {
      session.messages.push(message)
      session.updated_at = new Date()
      this.saveChatSession(session)
    }
  },

  // Clear all app data
  clearAll() {
    try {
      Object.values(STORAGE_KEYS).forEach(key => {
        sessionStorage.removeItem(key)
      })
      // Also clear legacy storage
      sessionStorage.removeItem('intake')

    } catch (e) {

    }
  },

  // Force clear on navigation or exit
  clearOnExit() {
    this.clearAll()
    // Also trigger a page reload to ensure clean state
    if (typeof window !== 'undefined') {
      setTimeout(() => {
        window.location.reload()
      }, 100)
    }
  },

  // Start fresh session (clear everything and reset)
  startFreshSession() {

    this.clearAll()
    return {
      intake_cleared: true,
      chat_cleared: true,
      session_id: Date.now().toString()
    }
  },

  // Check if user has completed intake form
  hasCompletedIntakeForm(): boolean {
    const intakeData = this.getIntakeForm()
    return !!(intakeData && intakeData.skin_type && intakeData.sensitive)
  },

  // Get user profile summary for display (returns empty if no data)
  getUserProfileSummary(): string {
    const intakeData = this.getIntakeForm()
    if (!intakeData) return ''

    const parts = []
    if (intakeData.skin_type) parts.push(`${intakeData.skin_type} skin`)
    if (intakeData.sensitive === 'yes') parts.push('sensitive')
    if (intakeData.concerns && intakeData.concerns.length > 0) {
      parts.push(`concerns: ${intakeData.concerns.join(', ')}`)
    }

    return parts.join(' | ')
  },

  // Check if this is a fresh session (no data)
  isFreshSession(): boolean {
    return !this.getIntakeForm() && !this.getChatSession()
  }
}

// Helper function to generate unique IDs
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Helper function to create new chat session
export function createNewChatSession(intakeData?: IntakeFormData): ChatSession {
  return {
    id: generateId(),
    messages: [],
    intake_data: intakeData,
    created_at: new Date(),
    updated_at: new Date()
  }
}
