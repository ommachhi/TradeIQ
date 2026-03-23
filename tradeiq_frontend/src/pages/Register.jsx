import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI, authHelpers } from '../services/api'

/**
 * Register Page
 * User registration form
 */
const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    role: 'investor'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    // client-side password check first
    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    try {
      // register user
      await authAPI.register(formData)
      setSuccess('Registration successful!')

      // attempt automatic login; failures here should not erase the success message
      try {
        const authResp = await authAPI.login({
          username: formData.username,
          password: formData.password
        })
        authHelpers.setAuthData(
          authResp.access_token,
          authResp.user.role,
          authResp.user.username
        )
        navigate('/dashboard')
      } catch (loginErr) {
        console.error('login after registration failed', loginErr)
        let loginMsg = 'Automatic login failed – please log in manually.'
        if (loginErr.response && loginErr.response.data) {
          const d = loginErr.response.data
          if (d.error) loginMsg = d.error
          else if (d.detail) loginMsg = d.detail
          else if (typeof d === 'object') {
            loginMsg = Object.entries(d)
              .map(([k,v]) => `${k}: ${Array.isArray(v) ? v.join(' ') : v}`)
              .join(' | ')
          }
        } else if (loginErr.message) {
          loginMsg = loginErr.message
        }
        setError(loginMsg)
      }
    } catch (err) {
      console.error('registration error', err)
      let message = 'Registration failed. Please try again.'
      if (err.response && err.response.data) {
        const d = err.response.data
        if (d.error) message = d.error
        else if (d.detail) message = d.detail
        else if (typeof d === 'object') {
          // flatten field errors
          message = Object.entries(d)
            .map(([k,v]) => `${k}: ${Array.isArray(v) ? v.join(' ') : v}`)
            .join(' | ')
        }
      } else if (err.message) {
        message = err.message
      }
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const roleOptions = [
    { value: 'investor', label: 'Investor' },
    { value: 'analyst', label: 'Market Analyst' },
    { value: 'researcher', label: 'Researcher' },
    { value: 'admin', label: 'Admin' }
  ]

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4">
      {/* Animated Background Elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl opacity-20 -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl opacity-20 translate-x-1/2 translate-y-1/2"></div>

      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 text-white">
            Join <span className="gradient-text">TradeIQ</span>
          </h1>
          <p className="text-gray-400">
            Create your account to start analyzing markets
          </p>
        </div>

        {/* Register Form */}
        <div className="card card-hover">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {success && (
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <p className="text-green-400 text-sm">{success}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                className="input-field w-full"
                placeholder="Choose a username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="input-field w-full"
                placeholder="Enter your email"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength="8"
                className="input-field w-full"
                placeholder="Create a password (min 8 characters)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                required
                minLength="8"
                className="input-field w-full"
                placeholder="Re-enter your password"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Role
              </label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="input-field w-full"
              >
                {roleOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
