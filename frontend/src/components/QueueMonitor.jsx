import { useEffect, useState } from 'react'
import { filesAPI } from '../services/api'

function QueueMonitor({ detailed = false }) {
  const [files, setFiles] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchFiles()
    const interval = setInterval(fetchFiles, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchFiles = async () => {
    try {
      const response = await filesAPI.monitor()
      setFiles(response.data)
    } catch (error) {
      console.error('Error fetching files:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="text-gray-400">Loading queue...</div>

  return (
    <div className="space-y-4">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Email Queue</p>
          <p className="text-3xl font-bold text-blue-400 mt-2">{files?.email?.count || 0}</p>
          <p className="text-gray-500 text-xs mt-1">{files?.email?.size_bytes} bytes</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Link Queue</p>
          <p className="text-3xl font-bold text-green-400 mt-2">{files?.link?.count || 0}</p>
          <p className="text-gray-500 text-xs mt-1">{files?.link?.size_bytes} bytes</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Profiles</p>
          <p className="text-3xl font-bold text-purple-400 mt-2">{files?.mapping?.count || 0}</p>
          <p className="text-gray-500 text-xs mt-1">{files?.mapping?.size_bytes} bytes</p>
        </div>
      </div>

      {/* Detailed View */}
      {detailed && (
        <>
          {/* Email List */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-bold text-white mb-4">Email Queue ({files?.email?.count || 0})</h3>
            <div className="max-h-64 overflow-y-auto space-y-2">
              {files?.email?.sample?.map((email, idx) => (
                <div key={idx} className="p-2 bg-gray-700 rounded text-gray-300 text-sm font-mono">
                  {email}
                </div>
              )) || <p className="text-gray-400">No emails</p>}
            </div>
          </div>

          {/* Link List */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-bold text-white mb-4">Link Queue ({files?.link?.count || 0})</h3>
            <div className="max-h-64 overflow-y-auto space-y-2">
              {files?.link?.sample?.map((link, idx) => (
                <div key={idx} className="p-2 bg-gray-700 rounded text-gray-300 text-sm font-mono truncate">
                  {link}
                </div>
              )) || <p className="text-gray-400">No links</p>}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default QueueMonitor
