import React from 'react'
import { FileText, Trash2 } from 'lucide-react'
import { deleteDocument } from '../services/api'

export function DocumentList({ documents, activeDoc, onSelectDoc, onDeleteDoc }) {
  if (documents.length === 0) {
    return (
      <div className="doc-list-empty">
        <p>No documents yet</p>
      </div>
    )
  }

  const handleDelete = async (e, docId) => {
    e.stopPropagation()
    try {
      await deleteDocument(docId)
      onDeleteDoc(docId)
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  return (
    <div className="doc-list">
      <h3 className="doc-list-title">Documents</h3>
      <ul>
        {documents.map((doc) => (
          <li
            key={doc.doc_id}
            className={`doc-item ${doc.doc_id === activeDoc ? 'doc-item-active' : ''}`}
            onClick={() => onSelectDoc(doc.doc_id)}
          >
            <FileText size={16} />
            <div className="doc-item-info">
              <span className="doc-item-name">{doc.filename}</span>
              <span className="doc-item-meta">
                {doc.page_count} page{doc.page_count !== 1 ? 's' : ''}
              </span>
            </div>
            <button
              className="doc-item-delete"
              onClick={(e) => handleDelete(e, doc.doc_id)}
              aria-label="Delete document"
            >
              <Trash2 size={14} />
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
