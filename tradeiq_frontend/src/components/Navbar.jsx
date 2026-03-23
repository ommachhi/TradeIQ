import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { authAPI, authHelpers } from '../services/api'

/**
 * Navbar Component
 * Navigation bar with role-based links
 */
const Navbar = () => {
  const [authState, setAuthState] = useState({
    isAuthenticated: authHelpers.isAuthenticated(),
    userRole: authHelpers.getUserRole(),
    username: authHelpers.getUsername(),
  })

  useEffect(() => {
    const syncAuthState = () => {
      setAuthState({
        isAuthenticated: authHelpers.isAuthenticated(),
        userRole: authHelpers.getUserRole(),
        username: authHelpers.getUsername(),
      })
    }

    const hydrateProfile = async () => {
      if (!authHelpers.isAuthenticated() || authHelpers.getUsername()) {
        return
      }

      try {
        const profile = await authAPI.getProfile()
        authHelpers.setAuthData(
          authHelpers.getToken(),
          profile.role || authHelpers.getUserRole(),
          profile.username
        )
      } catch {
        // Ignore profile hydration failures and keep the existing UI state.
      }
    }

    syncAuthState()
    hydrateProfile()

    const unsubscribe = authHelpers.subscribe(() => {
      syncAuthState()
      hydrateProfile()
    })

    return unsubscribe
  }, [])

  const { isAuthenticated, userRole, username } = authState
  const profileInitial = (username || 'U').trim().charAt(0).toUpperCase()

  const handleLogout = () => {
    authHelpers.logout()
  }

  return (
    <nav className="bg-gradient-to-r from-slate-900 to-slate-800 border-b border-slate-700 sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-600 rounded-lg flex items-center justify-center font-bold text-white group-hover:shadow-lg group-hover:shadow-blue-500/50 transition-all duration-300">
              T
            </div>
            <span className="text-xl font-bold gradient-text hidden sm:inline">
              TradeIQ
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex space-x-8">
            <Link
              to="/"
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 relative group"
            >
              Home
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-600 group-hover:w-full transition-all duration-300"></span>
            </Link>

            {isAuthenticated && (
              <>
                <Link
                  to="/dashboard"
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 relative group"
                >
                  Dashboard
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-600 group-hover:w-full transition-all duration-300"></span>
                </Link>

                <Link
                  to="/predict"
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 relative group"
                >
                  Predict
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-600 group-hover:w-full transition-all duration-300"></span>
                </Link>

                <Link
                  to="/analysis"
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 relative group"
                >
                  Analysis
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-600 group-hover:w-full transition-all duration-300"></span>
                </Link>

                {userRole === 'admin' && (
                  <Link
                    to="/admin"
                    className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 relative group"
                  >
                    Admin
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-600 group-hover:w-full transition-all duration-300"></span>
                  </Link>
                )}
              </>
            )}
          </div>

          {/* Auth Buttons */}
          <div className="flex items-center space-x-4">
            {!isAuthenticated ? (
              <>
                <Link
                  to="/login"
                  className="text-gray-300 hover:text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-200"
                >
                  Sign Up
                </Link>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <span className="text-gray-300 text-sm">
                  Hi, <span className="text-blue-400 font-semibold">{username || 'User'}</span>
                </span>
                <span className="hidden md:inline text-gray-400 text-sm">
                  {userRole && (
                    <>
                      Role: <span className="text-blue-400 capitalize">{userRole}</span>
                    </>
                  )}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-gray-300 hover:text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                >
                  Logout
                </button>
              </div>
            )}

            {isAuthenticated ? (
              <Link
                to="/profile"
                title="Open profile"
                className="hidden md:flex h-10 w-10 items-center justify-center rounded-full border border-blue-400/40 bg-gradient-to-br from-blue-500/20 to-purple-500/20 text-sm font-bold text-blue-200 shadow-lg shadow-blue-500/10 transition-all duration-200 hover:scale-105 hover:border-blue-300 hover:text-white hover:shadow-blue-500/20"
              >
                {profileInitial}
              </Link>
            ) : (
              <div className="hidden md:block w-1 h-8 bg-gradient-to-b from-blue-400 to-purple-600 rounded-full opacity-50"></div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
