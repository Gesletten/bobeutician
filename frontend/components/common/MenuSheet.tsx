import React from 'react'

export default function MenuSheet() {
  return (
    <nav>
      <ul className="flex flex-col">
        <li><a 
          href="/" 
          className="h-[10vh]  px-[2vw] text-2xl block px-4 py-2 transition-colors duration-200 hover:bg-[#DEA193] hover:font-bold flex items-center"
        >
          About
        </a></li>
        <li><a 
          href="/form"
          className="h-[10vh] px-[2vw] text-2xl block px-4 py-2 transition-colors duration-200 hover:bg-[#DEA193] hover:font-bold flex items-center"
        >Form
        </a></li>
        <li><a 
          href="/chat"
          className="h-[10vh] px-[2vw] text-2xl block px-4 py-2 transition-colors duration-200 hover:bg-[#DEA193] hover:font-bold flex items-center"
        >Chat
        </a></li>
      </ul>
    </nav>
  )
}

/*

Notes for my teammates:

This component is responsible for rendering the menu sheet with navigation links.
Feel free to add more links or modify the styling as needed.

*/