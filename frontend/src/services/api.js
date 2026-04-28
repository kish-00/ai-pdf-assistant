const API_BASE = import.meta.env.VITE_API_URL || '/api'

// Increase timeout for HF API calls (can be slow)
const TIMEOUT_MS = 120000 // 2 minutes

async function handleResponse(response) {
  if (!response.ok) {
    const error = new Error(`API error: ${response.status} ${response.statusText}`)
    error.status = response.status
    throw error
  }
  return response.json()
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    })
    clearTimeout(timeout)
    return handleResponse(response)
  } catch (err) {
    clearTimeout(timeout)
    if (err.name === 'AbortError') {
      throw new Error('Upload timed out. Please try again with a smaller file.')
    }
    throw err
  }
}

export async function askQuestion(docId, question) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE}/chat/${docId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    })
    clearTimeout(timeout)
    return handleResponse(response)
  } catch (err) {
    clearTimeout(timeout)
    if (err.name === 'AbortError') {
      throw new Error('Request timed out. The AI is taking too long. Please try a simpler question.')
    }
    throw err
  }
}

export async function summarizeDocument(docId) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE}/summarize/${docId}`, {
      method: 'POST',
      signal: controller.signal,
    })
    clearTimeout(timeout)
    return handleResponse(response)
  } catch (err) {
    clearTimeout(timeout)
    if (err.name === 'AbortError') {
      throw new Error('Summary generation timed out. Please try again.')
    }
    throw err
  }
}

export async function getDocuments() {
  const response = await fetch(`${API_BASE}/documents`)
  return handleResponse(response)
}

  return response.json()
}

export async function askQuestion(docId, question) {
  const response = await fetch(`${API_BASE}/chat/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId, question }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Query failed' }))
    throw new Error(error.detail || 'Query failed')
  }

  return response.json()
}

export async function summarizeDocument(docId) {
  const response = await fetch(`${API_BASE}/chat/summarize/${docId}`, {
    method: 'POST',
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Summarization failed' }))
    throw new Error(error.detail || 'Summarization failed')
  }

  return response.json()
}

export async function listDocuments() {
  const response = await fetch(`${API_BASE}/pdf/documents`)
  if (!response.ok) throw new Error('Failed to list documents')
  return response.json()
}

export async function deleteDocument(docId) {
  const response = await fetch(`${API_BASE}/pdf/${docId}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete document')
  return response.json()
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`)
  return response.json()
}
