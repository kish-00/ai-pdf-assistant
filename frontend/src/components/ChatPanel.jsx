import React, { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { Send, BookOpen, Loader2, MessageSquare } from 'lucide-react'
import { askQuestion, summarizeDocument } from '../services/api'

export function ChatPanel({ docId, docName, messages, addMessage }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const question = input.trim()
    if (!question || loading) return

    setInput('')
    addMessage(docId, { role: 'user', content: question })
    setLoading(true)

    try {
      const result = await askQuestion(docId, question)
      addMessage(docId, {
        role: 'assistant',
        content: result.answer,
        sources: result.sources,
      })
    } catch (err) {
      let errorMsg = 'Sorry, something went wrong.'
      if (err.message) {
        if (err.message.includes('timeout') || err.message.includes('timed out')) {
          errorMsg = 'The request timed out. The AI model is taking too long to respond. Please try again or ask a simpler question.'
        } else if (err.message.includes('503') || err.message.includes('Model loading')) {
          errorMsg = 'The AI model is currently loading. Please wait a moment and try again.'
        } else {
          errorMsg = `Error: ${err.message}`
        }
      }
      addMessage(docId, {
        role: 'assistant',
        content: errorMsg,
        sources: [],
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSummarize = async () => {
    if (loading) return
    setLoading(true)

    addMessage(docId, { role: 'user', content: 'Summarize this document' })

    try {
      const result = await summarizeDocument(docId)
      addMessage(docId, {
        role: 'assistant',
        content: result.summary,
        sources: [],
      })
    } catch (err) {
      let errorMsg = 'Sorry, something went wrong while generating the summary.'
      if (err.message) {
        if (err.message.includes('timeout') || err.message.includes('timed out')) {
          errorMsg = 'Summary generation timed out. The document may be too long. Please try again.'
        } else if (err.message.includes('503') || err.message.includes('Model loading')) {
          errorMsg = 'The AI model is currently loading. Please wait and try again.'
        } else {
          errorMsg = `Error: ${err.message}`
        }
      }
      addMessage(docId, {
        role: 'assistant',
        content: errorMsg,
        sources: [],
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <MessageSquare size={18} />
        <span className="chat-header-name">{docName}</span>
        <button className="btn-summarize" onClick={handleSummarize} disabled={loading}>
          <BookOpen size={14} />
          Summarize
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <MessageSquare size={32} />
            <p>Ask a question about this PDF</p>
            <p className="chat-empty-hint">
              Try: "What is this document about?" or "Summarize the key findings"
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message chat-message-${msg.role}`}>
            <div className="chat-message-content">
              {msg.role === 'assistant' ? (
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              ) : (
                <p>{msg.content}</p>
              )}
              {msg.sources && msg.sources.length > 0 && (
                <div className="chat-sources">
                  <span className="sources-label">Sources:</span>
                  {msg.sources.map((src, j) => (
                    <span key={j} className="source-tag">{src}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-message chat-message-assistant">
            <div className="chat-message-content">
              <Loader2 size={18} className="spin" /> Thinking...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your PDF..."
          rows={1}
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()} className="btn-send">
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
