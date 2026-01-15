import '../styles/globals.css'
import React from 'react'
import Header from '../components/common/Header'
import { Jost } from 'next/font/google';

const jost = Jost({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-jost',
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={jost.variable}>
      <body className={jost.variable}>
        <Header />
        <main className="p-0">{children}</main>
      </body>
    </html>
  )
}
