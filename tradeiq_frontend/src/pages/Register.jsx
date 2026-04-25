import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI, authHelpers } from '../services/api'

const INITIAL_FORM_STATE = {
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'investor',
}

/**
 * Register Page
 * User registration form
 */
const Register = () => {
  const [formData, setFormData] = useState(INITIAL_FORM_STATE)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [inputsUnlocked, setInputsUnlocked] = useState(false)
  const usernameRef = useRef(null)
  const emailRef = useRef(null)
  const passwordRef = useRef(null)
  const confirmPasswordRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    const clearForm = () => {
      setFormData({ ...INITIAL_FORM_STATE })
      setInputsUnlocked(false)
      ;[usernameRef, emailRef, passwordRef, confirmPasswordRef].forEach((ref) => {
        if (ref.current) {
          ref.current.value = ''
        }
      })
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
                ref={usernameRef}
                name="tradeiq_register_username"
                data-field="username"
                value={formData.username}
                onChange={handleChange}
                onFocus={() => setInputsUnlocked(true)}
                required
                readOnly={!inputsUnlocked}
                className="input-field w-full"
                placeholder="Choose a username"
                autoComplete="off"
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck={false}
                data-lpignore="true"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                ref={emailRef}
                type="email"
                name="tradeiq_register_email"
                data-field="email"
                value={formData.email}
                onChange={handleChange}
                onFocus={() => setInputsUnlocked(true)}
                required
                readOnly={!inputsUnlocked}
                className="input-field w-full"
                placeholder="Enter your email"
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
                ref={passwordRef}
                type="password"
                name="tradeiq_register_password"
                data-field="password"
                value={formData.password}
                onChange={handleChange}
                onFocus={() => setInputsUnlocked(true)}
                required
                minLength="8"
                readOnly={!inputsUnlocked}
                className="input-field w-full"
                placeholder="Create a password (min 8 characters)"
                autoComplete="new-password"
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck={false}
                data-lpignore="true"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <input
                ref={confirmPasswordRef}
                type="password"
                name="tradeiq_register_password_confirm"
                data-field="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                onFocus={() => setInputsUnlocked(true)}
                required
                minLength="8"
                readOnly={!inputsUnlocked}
                className="input-field w-full"
                placeholder="Re-enter your password"
                autoComplete="new-password"
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck={false}
                data-lpignore="true"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Role
              </label>
              <select
                name="tradeiq_register_role"
                data-field="role"
                value={formData.role}
                onChange={handleChange}
                onFocus={() => setInputsUnlocked(true)}
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
