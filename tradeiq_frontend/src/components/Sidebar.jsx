import { Link } from 'react-router-dom'
import { authHelpers } from '../services/api'

const Sidebar = () => {
  const userRole = authHelpers.getUserRole()

  return (
    <aside className="w-64 bg-slate-800 text-gray-200 min-h-screen p-4 hidden md:block">
      <nav className="space-y-2">
        <Link className="block px-3 py-2 rounded hover:bg-slate-700" to="/dashboard">
          Dashboard
        </Link>
        <Link className="block px-3 py-2 rounded hover:bg-slate-700" to="/predict">
          Predict
        </Link>
        <Link className="block px-3 py-2 rounded hover:bg-slate-700" to="/analysis">
          Analysis
        </Link>
        {userRole === 'admin' && (
          <Link className="block px-3 py-2 rounded hover:bg-slate-700" to="/admin">
            Admin
          </Link>
        )}
      </nav>
    </aside>
  )
}

export default Sidebar
