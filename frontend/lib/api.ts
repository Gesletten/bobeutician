// Backend base URL - Fallback to localhost:8000
export const backendBase =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000'

// Keep legacy alias for code that expects `apiBase`
export const apiBase = backendBase

// Legacy QA endpoint
export async function postQA(payload: any) {
  const url = `${backendBase.replace(/\/$/, '')}/api/qa`
  if (backendBase.match(/:\d+$/) && backendBase.includes(':3000')) {
    console.warn('API client: backendBase is set to port 3000 - this may be misconfigured. Prefer port 8000 for backend.')
  }

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return res.json()
}

// New Chat API with intake form integration
export async function submitIntakeForm(intakeData: IntakeFormData) {
  const url = `${backendBase.replace(/\/$/, '')}/api/chat/intake`
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(intakeData),
  })

  if (!res.ok) {
    throw new Error(`Intake form submission failed: ${res.statusText}`)
  }

  return res.json()
}

export async function chatWithAI(chatRequest: ChatRequest): Promise<ChatResponse> {
  const primaryUrl = `${backendBase.replace(/\/$/, '')}/api/qa`

  try {
    const res = await fetch(primaryUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(chatRequest),
    })

    if (!res.ok) {
      const bodyText = await res.text().catch(() => '')
      const shortBody = bodyText.length > 300 ? `${bodyText.slice(0, 300)}...` : bodyText
      // Detect common Next.js 404 HTML to give a helpful hint
      const isNext404 = /<title>404: This page could not be found\.|This page could not be found\./i.test(shortBody)
      const hint = isNext404
        ? 'Received an HTML 404 page from the frontend - this means the request reached the Next.js server rather than the backend. Ensure `NEXT_PUBLIC_BACKEND_URL` points to the backend (port 8000) and not the frontend.'
        : 'Ensure the backend is running and exposes POST /api/qa.'

      throw new Error(`Chat request failed: ${res.status} ${res.statusText}. ${hint} Response body: ${shortBody}`)
    }

    return res.json()
  } catch (err: any) {
    const msg = String(err.message || err)
    if (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('ERR_EMPTY_RESPONSE')) {
      throw new Error(
        `Cannot reach backend at ${primaryUrl}. Network error: ${msg}. Start the backend (uvicorn or docker) and ensure it's listening on port 8000 and that /api/qa exists.`
      )
    }

    throw err
  }
}

export async function chatWithDirectLLM(request: {
  question: string;
  conversation_history?: string;
  conversation_id?: string;
}): Promise<{ answer: string; mode: string; conversation_id?: string }> {
  const res = await fetch(`${apiBase}/api/chat/direct`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!res.ok) {
    throw new Error(`Direct chat failed: ${res.statusText}`)
  }

  return res.json()
}

// Free-form chat like ChatGPT
export async function chatFreeform(request: {
  question: string;
  conversation_history?: string;
  conversation_id?: string;
}): Promise<{ answer: string; conversation_id?: string }> {
  const res = await fetch(`${apiBase}/api/chat/direct`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!res.ok) {
    throw new Error(`Free-form chat failed: ${res.statusText}`)
  }

  const data = await res.json()
  return {
    answer: data.answer,
    conversation_id: data.conversation_id
  }
}

// Health check for API status
export async function checkAPIHealth() {
  const res = await fetch(`${apiBase}/api/chat/health`)
  return res.json()
}

// Types for API requests/responses
export type IntakeFormData = {
  skin_type: string
  sensitive: 'yes' | 'no'
  concerns: string[]
}

export type ChatRequest = {
  question: string
  intake_data?: IntakeFormData
  concern?: string
  conversation_id?: string
}

export type ChatResponse = {
  answer: string
  context_summary: string
  user_profile: string
  citations: Array<{ id: string; source: string; score?: number }>
  recommendation_confidence: number
  routine_suggestion: string
  conversation_id?: string
}