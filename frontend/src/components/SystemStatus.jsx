import { useEffect, useState } from 'react'
import { Activity, Users, AlertCircle } from 'lucide-react'
import { dashboardAPI } from '../services/api'

function SystemStatus({ status, loading }) {
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    fetchSummary()
  }, [])

  const fetchSummary = async () => {
    try {
      const response = await dashboardAPI.getSummary()
      setSummary(response.data)
    } catch (error) {
      console.error('Error fetching summary:', error)
    }
  }

  if (!status) return <div className="text-gray-400">Loading...</div>

  return (
    <div>
      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {/* State */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">System State</p>
              <p className="text-2xl font-bold text-white">{status.state}</p>
            </div>
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              status.state === 'IDLE' ? 'bg-green-900' : 'bg-yellow-900'
            }`}>
              <Activity size={24} className={status.state === 'IDLE' ? 'text-green-400' : 'text-yellow-400'} />
            </div>
          </div>
        </div>

        {/* Active Workers */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Workers</p>
              <p className="text-2xl font-bold text-white">{summary?.active_workers || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-blue-900 flex items-center justify-center">
              <Users size={24} className="text-blue-400" />
            </div>
          </div>
        </div>

        {/* Queue Items */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Queue Items</p>
              <p className="text-2xl font-bold text-white">{status.queue?.links || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-purple-900 flex items-center justify-center">
              <AlertCircle size={24} className="text-purple-400" />
            </div>
          </div>
        </div>

        {/* Success Rate */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-white">{summary?.success_rate || '0%'}</p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-green-900 flex items-center justify-center">
              <span className="text-green-400 font-bold text-xl">✓</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Metrics */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">System Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-gray-400 text-sm mb-1">CPU Usage</p>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${status.system?.cpu_percent || 0}%` }}
              ></div>
            </div>
            <p className="text-white text-sm font-medium mt-1">{status.system?.cpu_percent.toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Memory Usage</p>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full"
                style={{ width: `${status.system?.memory_percent || 0}%` }}
              ></div>
            </div>
            <p className="text-white text-sm font-medium mt-1">{status.system?.memory_percent.toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Used Memory</p>
            <p className="text-white text-xl font-bold">{status.system?.memory_mb} MB</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Available</p>
            <p className="text-white text-xl font-bold">{status.system?.available_mb} MB</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SystemStatus
