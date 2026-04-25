import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { healthCheck } from '../services/api'

/**
 * Home Page
 * Landing page with project introduction
 */
const Home = () => {
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    let cancelled = false

    const checkAPI = async () => {
      try {
        const result = await healthCheck()
        if (!cancelled) {
          setApiStatus(result.status === 'healthy' ? 'healthy' : 'unhealthy')
        }
      } catch (error) {
        if (!cancelled) {
          setApiStatus('error')
        }
      }
    }

    checkAPI()

    const intervalId = window.setInterval(checkAPI, 10000)
    window.addEventListener('focus', checkAPI)
    window.addEventListener('online', checkAPI)

    return () => {
      cancelled = true
      window.clearInterval(intervalId)
      window.removeEventListener('focus', checkAPI)
      window.removeEventListener('online', checkAPI)
    }
  }, [])

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl opacity-20 -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl opacity-20 translate-x-1/2 translate-y-1/2"></div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        {/* Hero Section */}
        <div className="text-center mb-16 md:mb-24">
          <div className="inline-block mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/50">
              <span className="text-4xl font-bold text-white">T</span>
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-white">
            Trade<span className="gradient-text">IQ</span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-300 mb-4">
            AI-Powered Stock Market Prediction
          </p>

          <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
            Leveraging machine learning to predict stock prices with high accuracy. 
            Make informed investment decisions with our advanced prediction model.
          </p>

          {/* API Status */}
          <div className="flex items-center justify-center space-x-3 mb-12">
            <div
              className={`w-3 h-3 rounded-full ${
                apiStatus === 'healthy' ? 'bg-green-400' : apiStatus === 'error' ? 'bg-red-400' : 'bg-yellow-400'
              } animate-pulse`}
            ></div>
            <p className="text-sm text-gray-400">
              {apiStatus === 'healthy'
                ? 'API: Connected'
                : apiStatus === 'error'
                ? 'API: Disconnected'
                : 'API: Checking...'}
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/predict" className="btn-primary inline-block">
              Start Predicting
            </Link>

            <Link
              to="/analysis"
              className="px-8 py-3 rounded-lg border border-slate-600 text-white hover:border-blue-400 hover:bg-blue-400/10 transition-all duration-200 font-medium inline-block"
            >
              View Analysis
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 my-20">
          {/* Feature 1 */}
          <div className="card card-hover text-center group">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-500/30 transition-colors">
              <svg
                className="w-6 h-6 text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Fast Predictions</h3>
            <p className="text-gray-400 text-sm">
              Get instant stock price predictions using our trained ML model
            </p>
          </div>

          {/* Feature 2 */}
          <div className="card card-hover text-center group">
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-500/30 transition-colors">
              <svg
                className="w-6 h-6 text-purple-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Data Analysis</h3>
            <p className="text-gray-400 text-sm">
              Analyze historical stock data with interactive charts
            </p>
          </div>

          {/* Feature 3 */}
          <div className="card card-hover text-center group">
            <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-green-500/30 transition-colors">
              <svg
                className="w-6 h-6 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Smart Recommendations</h3>
            <p className="text-gray-400 text-sm">
              Get BUY, SELL, or HOLD recommendations based on predictions
            </p>
          </div>
        </div>

        {/* Tech Stack Section */}
        <div className="mt-24 pt-20 border-t border-slate-700">
          <h2 className="text-3xl font-bold text-white mb-12 text-center">Technology Stack</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { name: 'Django', icon: '🐍' },
              { name: 'React.js', icon: '⚛️' },
              { name: 'Tailwind CSS', icon: '🎨' },
              { name: 'Machine Learning', icon: '🤖' },
            ].map((tech) => (
              <div
                key={tech.name}
                className="card text-center p-6 border border-slate-700 bg-slate-800/30"
              >
                <span className="text-4xl mb-3 block">{tech.icon}</span>
                <p className="text-white font-semibold">{tech.name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
