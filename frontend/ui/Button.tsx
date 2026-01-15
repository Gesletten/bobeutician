import React from 'react'

export default function Button({ children }: { children: React.ReactNode }) {
  return <button className="bg-blue-600 text-white px-3 py-1 rounded">{children}</button>
}

/*

Notes for my teammates:

This is a reusable Button component that can be used throughout the application.

*/