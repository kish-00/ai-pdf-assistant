const API_BASE = import.meta.env.VITE_API_URL || '/api'

export async function uploadPdf(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/pdf/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(error.detail || 'Upload failed')
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
