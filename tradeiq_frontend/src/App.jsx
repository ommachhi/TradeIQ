import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Predict from './pages/Predict'
import Analysis from './pages/Analysis'
import Login from './pages/Login'
import Register from './pages/Register'
import Admin from './pages/Admin'
import Researcher from './pages/Researcher'
import Analyst from './pages/Analyst'
import Profile from './pages/Profile'
import ProtectedRoute from './components/ProtectedRoute'
import AdminRoute from './components/AdminRoute'

/**
 * App Content Component
 * Handles conditional layout based on current route
 */
function AppContent() {
  const location = useLocation();
  // Hide main Navbar when on any admin-related path
  const isAdminPath = location.pathname.startsWith('/admin') || 
                     location.pathname.startsWith('/researcher') || 
                     location.pathname.startsWith('/analyst');

  return (
    <div className="min-h-screen bg-slate-950 text-gray-100">
      {!isAdminPath && <Navbar />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/predict"
          element={
            <ProtectedRoute>
              <Predict />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis"
          element={
            <ProtectedRoute>
              <Analysis />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <Admin />
            </AdminRoute>
          }
        />
        <Route
          path="/researcher"
          element={
            <ProtectedRoute>
              <Researcher />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analyst"
          element={
            <ProtectedRoute>
              <Analyst />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

/**
 * Main App Component
 * Wraps everything in a Router
 */
function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App
