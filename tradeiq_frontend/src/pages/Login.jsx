import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI, authHelpers } from '../services/api'

const INITIAL_FORM_STATE = {
  identifier: '',
  password: '',
}

/**
 * Login Page
 * User authentication form
 */
const Login = () => {
  const [formData, setFormData] = useState(INITIAL_FORM_STATE)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [inputsUnlocked, setInputsUnlocked] = useState(false)
  const identifierRef = useRef(null)
  const passwordRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    const clearForm = () => {
      setFormData({ ...INITIAL_FORM_STATE })
      setInputsUnlocked(false)
      if (identifierRef.current) {
        identifierRef.current.value = ''
      }
      if (passwordRef.current) {
        passwordRef.current.value = ''
      }
    }

    clearForm()
    const timers = [0, 150, 600].map((delay) => window.setTimeout(clearForm, delay))
    return () => timers.forEach((timer) => window.clearTimeout(timer))
  }, [])

  const handleChange = (e) => {
    const field = e.target.dataset.field
    setFormData({
      ...formData,
      [field]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authAPI.login({
        username: formData.identifier,
        password: formData.password,
      })

      // new backend returns { access_token, user }
      authHelpers.setAuthData(
        response.access_token,
        response.user.role,
        response.user.username
      )
      
      // Professional Redirect: Multi-Role Handshake
      if (response.user.role === 'admin') {
        navigate('/admin')
      } else if (response.user.role === 'researcher') {
        navigate('/researcher')
      } else if (response.user.role === 'analyst') {
        navigate('/analyst')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      const detail = err.response?.data?.detail || err.response?.data?.error
      setError(detail || 'Login failed. Please check your credentials.')
      setFormData((current) => ({ ...current, password: '' }))
      if (passwordRef.current) {
        passwordRef.current.value = ''
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4">
      {/* Animated Background Elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl opacity-20 -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl opacity-20 translate-x-1/2 translate-y-1/2"></div>

      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 text-white">
            Welcome <span className="gradient-text">Back</span>
          </h1>
          <p className="text-gray-400">
            Sign in to access your TradeIQ dashboard
          </p>
        </div>

        {/* Login Form */}
        <div className="card card-hover">
          <form onSubmit={handleSubmit} autoComplete="off" className="space-y-6" data-form-type="other">
            <div
              className="absolute left-[-9999px] top-auto h-0 w-0 overflow-hidden opacity-0 pointer-events-none"
              aria-hidden="true"
            >
              <input type="text" name="username" autoComplete="username" tabIndex={-1} />
              <input type="password" name="password" autoComplete="current-password" tabIndex={-1} />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Username or Email
              </label>
              <input
                type="text"
                ref={identifierRef}
                name="tradeiq_login_identifier"
                data-field="identifier"
                value={formData.identifier}
                onChange={handleChange}
                onFocus={() => setInputsUnlocked(true)}
                required
                readOnly={!inputsUnlocked}
                className="input-field w-full"
                placeholder="Enter your username or email"
                autoComplete="off"
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck={false}
                data-lpignore="true"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                ref={passwordRef}
                name="tradeiq_login_secret"
                data-field="password"
                value={formData.password}
                onChange={handleChange}
                onFocus={() => setInputsUnlocked(true)}
                required
                readOnly={!inputsUnlocked}
                className="input-field w-full"
                placeholder="Enter your password"
                autoComplete="new-password"
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck={false}
                data-lpignore="true"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-400 hover:text-blue-300 font-medium">
                Sign up here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
