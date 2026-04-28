import React, { useState } from 'react'
import { UploadZone } from './components/UploadZone'
import { ChatPanel } from './components/ChatPanel'
import { DocumentList } from './components/DocumentList'
import { Header } from './components/Header'
import './styles/global.css'

export default function App() {
  const [documents, setDocuments] = useState([])
  const [activeDoc, setActiveDoc] = useState(null)
  const [messages, setMessages] = useState({})

  const handleUploadComplete = (doc) => {
    setDocuments((prev) => [doc, ...prev])
    setActiveDoc(doc.doc_id)
    setMessages((prev) => ({ ...prev, [doc.doc_id]: [] }))
  }

  const handleSelectDoc = (docId) => {
    setActiveDoc(docId)
  }

  const handleDeleteDoc = (docId) => {
    setDocuments((prev) => prev.filter((d) => d.doc_id !== docId))
    setMessages((prev) => {
      const next = { ...prev }
      delete next[docId]
      return next
    })
    if (activeDoc === docId) {
      const remaining = documents.filter((d) => d.doc_id !== docId)
      setActiveDoc(remaining.length > 0 ? remaining[0].doc_id : null)
    }
  }

  const addMessage = (docId, message) => {
    setMessages((prev) => ({
      ...prev,
      [docId]: [...(prev[docId] || []), message],
    }))
  }

  const currentMessages = activeDoc ? messages[activeDoc] || [] : []

  return (
    <div className="app">
      <Header />
      <main className="main-layout">
        <aside className="sidebar">
          <UploadZone onUploadComplete={handleUploadComplete} />
          <DocumentList
            documents={documents}
            activeDoc={activeDoc}
            onSelectDoc={handleSelectDoc}
            onDeleteDoc={handleDeleteDoc}
          />
        </aside>
        <section className="content">
          {activeDoc ? (
            <ChatPanel
              docId={activeDoc}
              docName={documents.find((d) => d.doc_id === activeDoc)?.filename || 'Document'}
              messages={currentMessages}
              addMessage={addMessage}
            />
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h2>Upload a PDF to get started</h2>
              <p>Ask questions about your document and get AI-powered answers</p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
