import { useState } from 'react'
import { loadSession, saveSession } from '../lib/storage'

export default function useIntake() {
  const [data, setData] = useState(() => loadSession('intake') || {})
  function save(d: any) { setData(d); saveSession('intake', d) }
  return { data, save }
}