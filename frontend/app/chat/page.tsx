'use client'

import React, { useEffect } from 'react'
import ChatWindow from '../../components/chat/ChatWindow'
import { skincareStorage } from '../../lib/storage'

export default function ChatPage() {
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Clear intake data when leaving the chat page
      skincareStorage.clearAll()
    }

    // Clear intake data when tab is closed or refreshed
    window.addEventListener('beforeunload', handleBeforeUnload)

    // Only remove listeners on unmount. Do NOT clear storage on normal navigation
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [])

  return (
    <section className="h-screen pt-20 bg-no-repeat bg-cover flex flex-col bg-[url('../public/images/form_page_bg.png')]">
      <ChatWindow />
    </section>
  )
}
