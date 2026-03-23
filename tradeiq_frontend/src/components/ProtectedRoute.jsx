import { Navigate } from 'react-router-dom'
import { authHelpers } from '../services/api'

/**
 * ProtectedRoute Component
 * Blocks access if user is not logged in
 */
const ProtectedRoute = ({ children }) => {
  if (!authHelpers.isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute