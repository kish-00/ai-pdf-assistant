import React from 'react'
import { FileText } from 'lucide-react'

export function Header() {
  return (
    <header className="header">
      <div className="header-brand">
        <FileText size={28} />
        <h1>AI PDF Assistant</h1>
      </div>
      <p className="header-subtitle">Upload a PDF, ask questions, get AI-powered answers</p>
    </header>
  )
}
