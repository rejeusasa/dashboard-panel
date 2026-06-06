import { useEffect, useState } from 'react'
import { workersAPI } from '../services/api'

function WorkersList({ status }) {
  const [workers, setWorkers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchWorkers()
    const interval = setInterval(fetchWorkers, 3000)
    return () => clearInterval(interval)
  }, [])

  const fetchWorkers = async () => {
    try {
      const response = await workersAPI.list()
      setWorkers(response.data.workers || [])
    } catch (error) {
      console.error('Error fetching workers:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="text-gray-400">Loading workers...</div>

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-4">Active Workers</h2>
      
      {workers.length === 0 ? (
        <p className="text-gray-400 text-center py-8">No active workers</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Worker Name</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Time Remaining</th>
              </tr>
            </thead>
            <tbody>
              {workers.map((worker) => (
                <tr key={worker.name} className="border-b border-gray-700 hover:bg-gray-700/50">
                  <td className="py-3 px-4 text-white font-medium">{worker.name}</td>
                  <td className="py-3 px-4">
                    <span className="px-3 py-1 rounded-full text-sm bg-blue-900 text-blue-300">
                      {worker.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-400">
                    {Math.floor(worker.batch_time_remaining / 3600)}h {Math.floor((worker.batch_time_remaining % 3600) / 60)}m
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default WorkersList
