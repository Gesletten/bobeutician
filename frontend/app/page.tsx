import React from 'react'
import '../styles/globals.css'

export default function AboutPage() {
  return (

    <section className="min-h-screen w-full bg-[url('../public/images/main_page_bg.png')] bg-cover bg-center bg-no-repeat flex flex-col items-center justify-center text-[#260000] m-0 p-0">
      <div className="w-[80vw] max-w-5xl h-auto min-h-[48vh] bg-[#F6E7E1] bg-opacity-95 p-8 rounded-2xl shadow-xl 
                  flex flex-col items-center justify-center text-center">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-[#F5B7B1] via-[#DE6B74] to-[#0B0B0B]">
          BoBeutician
        </h1>
        <p className="text-xl md:text-3xl mt-4 max-w-3xl leading-relaxed text-[#0B0B0B]/95">
          <span className="block">Personalized skincare, powered by science and simplicity.</span>
          <span className="block text-lg md:text-xl mt-2 opacity-90">Answer a quick questionnaire - get routines, product matches, and ingredient insights made for your skin.</span>
        </p>
        <a href="/form" className="w-full sm:w-auto">
          <button
            className="w-full sm:w-auto px-8 py-3 mt-6 bg-gradient-to-r from-[#DE6B74] to-[#EBD6C8] text-white text-xl rounded-full shadow-lg hover:scale-105 transform transition-all duration-200 ring-1 ring-[#DE6B74]/20">
            Get Started
          </button>
        </a>
      </div>
    </section>
  )
}
