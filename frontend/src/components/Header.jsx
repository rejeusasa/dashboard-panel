import { LogOut } from 'lucide-react'

function Header({ user, onLogout }) {
  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">🤖 Dashboard Panel</h1>
          <p className="text-gray-400 text-sm">Bot Automation Monitor</p>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className="text-white font-medium">{user?.username}</p>
            <p className="text-gray-400 text-sm capitalize">{user?.role}</p>
          </div>
          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
