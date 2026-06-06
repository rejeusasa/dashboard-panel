import { useState, useEffect } from 'react'
import { LogOut } from 'lucide-react'
import Header from '../components/Header'
import SystemStatus from '../components/SystemStatus'
import WorkersList from '../components/WorkersList'
import QueueMonitor from '../components/QueueMonitor'
import ControlPanel from '../components/ControlPanel'
import LogViewer from '../components/LogViewer'
import Analytics from '../components/Analytics'
import { dashboardAPI } from '../services/api'

function Dashboard({ user, token, onLogout }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 2000)
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await dashboardAPI.getStatus()
      setStatus(response.data)
    } catch (error) {
      console.error('Error fetching status:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header user={user} onLogout={onLogout} />

      <div className="container mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-8 border-b border-gray-700 overflow-x-auto">
          {[
            { id: 'overview', label: '📊 Overview' },
            { id: 'workers', label: '👷 Workers' },
            { id: 'queue', label: '📋 Queue' },
            { id: 'control', label: '🎮 Control' },
            { id: 'logs', label: '📝 Logs' },
            { id: 'analytics', label: '📈 Analytics' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <>
              <SystemStatus status={status} loading={loading} />
              <QueueMonitor />
            </>
          )}
          {activeTab === 'workers' && <WorkersList status={status} />}
          {activeTab === 'queue' && <QueueMonitor detailed={true} />}
          {activeTab === 'control' && <ControlPanel onStatusChange={fetchStatus} />}
          {activeTab === 'logs' && <LogViewer />}
          {activeTab === 'analytics' && <Analytics />}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
