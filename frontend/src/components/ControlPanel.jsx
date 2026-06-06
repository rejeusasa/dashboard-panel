import { useState } from 'react'
import { Play, Square, RotateCcw, Trash2 } from 'lucide-react'
import { commandsAPI } from '../services/api'

function ControlPanel({ onStatusChange }) {
  const [loading, setLoading] = useState(false)

  const executeCommand = async (command) => {
    setLoading(true)
    try {
      let response
      switch (command) {
        case 'login':
          response = await commandsAPI.startLogin()
          break
        case 'loop':
          response = await commandsAPI.startLoop()
          break
        case 'stop':
          response = await commandsAPI.stop()
          break
        case 'restart':
          response = await commandsAPI.restart()
          break
        case 'clean':
          response = await commandsAPI.clean()
          break
        default:
          break
      }
      
      setTimeout(onStatusChange, 1000)
      alert(response?.data?.message || 'Command executed')
    } catch (error) {
      alert(error.response?.data?.error || 'Command failed')
    } finally {
      setLoading(false)
    }
  }

  const buttons = [
    {
      id: 'login',
      label: 'Start Login',
      icon: Play,
      color: 'bg-blue-600 hover:bg-blue-700',
      description: 'Run login.py to initialize profiles'
    },
    {
      id: 'loop',
      label: 'Start Loop',
      icon: Play,
      color: 'bg-green-600 hover:bg-green-700',
      description: 'Run loop.py for automation'
    },
    {
      id: 'restart',
      label: 'Restart Loop',
      icon: RotateCcw,
      color: 'bg-yellow-600 hover:bg-yellow-700',
      description: 'Stop and restart the loop'
    },
    {
      id: 'stop',
      label: 'Stop All',
      icon: Square,
      color: 'bg-red-600 hover:bg-red-700',
      description: 'Stop all processes immediately'
    },
    {
      id: 'clean',
      label: 'Clean RAM',
      icon: Trash2,
      color: 'bg-purple-600 hover:bg-purple-700',
      description: 'Clean system resources and memory'
    },
  ]

  return (
    <div className="space-y-6">
      {/* Warning */}
      <div className="bg-yellow-900 border border-yellow-700 rounded-lg p-4 text-yellow-200">
        ⚠️ Be careful with these commands. They directly control the bot automation process.
      </div>

      {/* Command Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {buttons.map((btn) => {
          const Icon = btn.icon
          return (
            <button
              key={btn.id}
              onClick={() => executeCommand(btn.id)}
              disabled={loading}
              className={`${btn.color} disabled:opacity-50 disabled:cursor-not-allowed p-6 rounded-lg text-white font-medium transition-colors flex flex-col items-center gap-3`}
            >
              <Icon size={24} />
              <div className="text-center">
                <p className="font-bold">{btn.label}</p>
                <p className="text-xs opacity-80">{btn.description}</p>
              </div>
            </button>
          )
        })}
      </div>

      {/* Command History */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-bold text-white mb-4">Last Commands</h3>
        <p className="text-gray-400 text-center py-8">Command history will appear here</p>
      </div>
    </div>
  )
}

export default ControlPanel
