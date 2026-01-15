'use client'


import React, { useState } from 'react'
import '../../styles/globals.css'
import MenuSheet from './MenuSheet'

export default function Header() {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className='header'>
      <header className="fixed top-0 left-0 w-full flex items-center justify-between bg-[#DEA193] text-white shadow p-4 z-50">
        
          <div className="w-8" />
          
          <h2 className="text-2xl font-normal tracking-tight text-center flex-1">bobeutician</h2>
          
          <div className="relative">
          <button
            aria-label="menu"
            className="w-8 h-8 flex items-center justify-center font-bold text-white bg-[#DEA193] rounded hover:bg-[#c78f80] transition"
            onClick={() => setIsOpen(!isOpen)}
          >
            ☰
          </button>

          {isOpen && (
            <div className="fixed right-0 mt-2 w-[15vw] bg-[#DEA193CF] text-white-bold shadow-lg z-50">
              <MenuSheet />
            </div>
          )}
        </div>
      </header>
    </div>
  )
}

/*

Notes for my teammates:

This component is responsible for rendering the header of the application.
Make sure to keep the design consistent with the overall app theme.

*/