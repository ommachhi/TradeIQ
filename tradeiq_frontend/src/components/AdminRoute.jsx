import { Navigate } from 'react-router-dom'
import { authHelpers } from '../services/api'

/**
 * AdminRoute Component
 * Allows access only for admin users
 */
const AdminRoute = ({ children }) => {
  if (!authHelpers.isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  if (authHelpers.getUserRole() !== 'admin') {
    return <Navigate to="/analysis" replace />
  }

  return children
}

export default AdminRoute