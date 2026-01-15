// Legacy QA types
export type QAResponse = {
  answer: string
  context_summary?: string
  citations?: Array<{ id: string; text: string }>
}

// New Chat system types
export type IntakeFormData = {
  skin_type: 'oily' | 'dry' | 'normal' | 'combination' | 'sensitive'
  sensitive: 'yes' | 'no'
  concerns: string[]
  completed_at?: string
}

export type ChatMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  user_profile?: string
  confidence?: number
  routine_suggestion?: string
  citations?: Array<{ id: string; source: string; score?: number }>
}

export type ChatSession = {
  id: string
  messages: ChatMessage[]
  intake_data?: IntakeFormData
  created_at: Date
  updated_at: Date
}

export type SkinConcern =
  | 'acne'
  | 'aging'
  | 'pigmentation'
  | 'dryness'
  | 'blackheads'
  | 'sensitivity'
  | 'sun_damage'
  | 'enlarged_pores'
  | 'fine_lines'
  | 'dark_circles'

// Utility type for form validation
export type FormValidationResult = {
  isValid: boolean
  errors: string[]
  warnings?: string[]
}