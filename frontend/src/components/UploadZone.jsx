import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileUp, Loader2 } from 'lucide-react'
import { uploadPdf } from '../services/api'

export function UploadZone({ onUploadComplete }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  const onDrop = useCallback(
    async (acceptedFiles) => {
      const file = acceptedFiles[0]
      if (!file) return

      setUploading(true)
      setError(null)

      try {
        const result = await uploadPdf(file)
        onUploadComplete(result)
      } catch (err) {
        setError(err.message)
      } finally {
        setUploading(false)
      }
    },
    [onUploadComplete]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: uploading,
  })

  return (
    <div className="upload-zone">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'dropzone-active' : ''} ${uploading ? 'dropzone-disabled' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <>
            <Loader2 size={24} className="spin" />
            <span>Processing PDF...</span>
          </>
        ) : isDragActive ? (
          <>
            <FileUp size={24} />
            <span>Drop the PDF here</span>
          </>
        ) : (
          <>
            <Upload size={24} />
            <span>Drop PDF or click to upload</span>
          </>
        )}
      </div>
      {error && <p className="upload-error">{error}</p>}
    </div>
  )
}
