import { useState } from 'react'
import { predictionAPI } from '../services/api'

/**
 * PredictionForm Component
 * Form for inputting stock features and getting predictions
 */
const PredictionForm = ({ onPredictionComplete }) => {
  const [inputMode, setInputMode] = useState('symbol') // 'symbol' or 'manual'
  const [formData, setFormData] = useState({
    symbol: '',
    open: '',
    high: '',
    low: '',
    volume: '',
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const formatINR = (value) => {
    if (value == null || Number.isNaN(Number(value))) return 'N/A'
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(Number(value))
  }

  const getConfidenceClass = (confidence) => {
    if (confidence === 'HIGH') return 'text-emerald-400'
    if (confidence === 'MEDIUM') return 'text-amber-400'
    return 'text-red-400'
  }

  const getTrendClass = (trend) => {
    if (trend === 'Uptrend') return 'text-emerald-400'
    if (trend === 'Downtrend') return 'text-red-400'
    return 'text-amber-400'
  }

  const handleInputModeChange = (mode) => {
    setInputMode(mode)
    setError(null)
    setResult(null)
    setFormData({
      symbol: '',
      open: '',
      high: '',
      low: '',
      volume: '',
    })
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      let predictionData

      if (inputMode === 'symbol') {
        // Symbol-based prediction
        if (!formData.symbol) {
          throw new Error('Stock symbol is required')
        }
        predictionData = { symbol: formData.symbol.toUpperCase() }
      } else {
        // Manual input prediction
        if (!formData.open || !formData.high || !formData.low || !formData.volume) {
          throw new Error('All fields are required')
        }

        const open = parseFloat(formData.open)
        const high = parseFloat(formData.high)
        const low = parseFloat(formData.low)
        const volume = parseInt(formData.volume)

        if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(volume)) {
          throw new Error('Invalid number format')
        }

        if (high < low) {
          throw new Error('High price must be greater than or equal to low price')
        }

        if (open < low || open > high) {
          throw new Error('Open price must be between low and high prices')
        }

        predictionData = { open, high, low, volume }
      }

      // Call API
      const prediction = await predictionAPI.predict(predictionData)

      setResult(prediction)
      if (onPredictionComplete) {
        onPredictionComplete(prediction)
      }
    } catch (err) {
      const payload = err.response?.data
      let message = payload?.detail || payload?.error || err.message || 'Failed to get prediction'
      if (payload?.details && typeof payload.details === 'object') {
        const details = Object.entries(payload.details)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(' ') : v}`)
          .join(' | ')
        if (details) {
          message = `${message} (${details})`
        }
      }
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card card-hover">
        <h2 className="text-3xl font-bold mb-8 gradient-text">Stock Price Predictor</h2>

        {/* Input Mode Selector */}
        <div className="mb-6">
          <div className="flex space-x-4 mb-4">
            <button
              type="button"
              onClick={() => handleInputModeChange('symbol')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                inputMode === 'symbol'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              Stock Symbol
            </button>
            <button
              type="button"
              onClick={() => handleInputModeChange('manual')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                inputMode === 'manual'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              Manual Input
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {inputMode === 'symbol' ? (
            /* Stock Symbol Input */
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Stock Symbol
              </label>
              <input
                type="text"
                name="symbol"
                value={formData.symbol}
                onChange={handleChange}
                placeholder="e.g., RELIANCE, TCS, INFY"
                className="input-field w-full"
                maxLength="20"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter a stock symbol to fetch live data and get prediction
              </p>
            </div>
          ) : (
            /* Manual Input Fields */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Open Price Input */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Opening Price (INR)
                </label>
                <input
                  type="number"
                  name="open"
                  value={formData.open}
                  onChange={handleChange}
                  placeholder="e.g., 120.5"
                  className="input-field w-full"
                  step="0.01"
                  min="0"
                />
              </div>

              {/* High Price Input */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Highest Price (INR)
                </label>
                <input
                  type="number"
                  name="high"
                  value={formData.high}
                  onChange={handleChange}
                  placeholder="e.g., 125.0"
                  className="input-field w-full"
                  step="0.01"
                  min="0"
                />
              </div>

              {/* Low Price Input */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Lowest Price (INR)
                </label>
                <input
                  type="number"
                  name="low"
                  value={formData.low}
                  onChange={handleChange}
                  placeholder="e.g., 118.2"
                  className="input-field w-full"
                  step="0.01"
                  min="0"
                />
              </div>

              {/* Volume Input */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Trading Volume
                </label>
                <input
                  type="number"
                  name="volume"
                  value={formData.volume}
                  onChange={handleChange}
                  placeholder="e.g., 450000"
                  className="input-field w-full"
                  min="0"
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300">
              <p className="font-medium">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                <span>Predicting...</span>
              </>
            ) : (
              'Get Prediction'
            )}
          </button>
        </form>

        {/* Result Display */}
        {result && (
          <div className="mt-8 pt-8 border-t border-slate-700">
            <h3 className="text-xl font-bold text-white mb-6">Prediction Result</h3>

            {result.warning && (
              <div className="mb-6 p-4 bg-amber-500/10 border border-amber-500/40 rounded-lg text-amber-300">
                <p className="font-semibold">{result.warning}</p>
                <p className="text-xs mt-1">Prediction deviates significantly from current price. Use with caution.</p>
              </div>
            )}

            {/* Stock Symbol Display */}
            {result.symbol && (
              <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <p className="text-blue-300 font-medium">Stock Symbol: {result.symbol}</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Predicted Price */}
              <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
                <p className="text-gray-400 text-sm font-medium mb-2">Predicted Price</p>
                <p className="text-4xl font-bold text-blue-400">
                  {formatINR(result.predicted_price)}
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Based on input parameters
                </p>
              </div>

              {/* Recommendation Badge */}
              <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 flex flex-col items-center justify-center">
                <p className="text-gray-400 text-sm font-medium mb-3">Recommendation</p>
                <span
                  className={`badge ${
                    result.recommendation === 'BUY'
                      ? 'badge-buy'
                      : result.recommendation === 'SELL'
                      ? 'badge-sell'
                      : 'badge-hold'
                  } text-lg px-6 py-3`}
                >
                  {result.recommendation}
                </span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                <p className="text-gray-500 text-xs uppercase">Current Price</p>
                <p className="text-white font-semibold mt-1">{formatINR(result.current_price)}</p>
              </div>
              <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                <p className="text-gray-500 text-xs uppercase">Change</p>
                <p className={`font-semibold mt-1 ${(result.change_percent || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {(result.change_percent || 0) >= 0 ? '+' : ''}{(result.change_percent || 0).toFixed(2)}%
                </p>
              </div>
              <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                <p className="text-gray-500 text-xs uppercase">Trend</p>
                <p className={`font-semibold mt-1 ${getTrendClass(result.trend)}`}>
                  {result.trend === 'Uptrend' ? 'Uptrend 📈' : result.trend === 'Downtrend' ? 'Downtrend 📉' : 'Sideways ➖'}
                </p>
              </div>
              <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                <p className="text-gray-500 text-xs uppercase">Confidence</p>
                <p className={`font-semibold mt-1 ${getConfidenceClass(result.confidence)}`}>
                  {result.confidence || 'LOW'}
                </p>
              </div>
            </div>

            {/* Technical Indicators */}
            {result.technical_indicators && (
              <div className="mt-6 bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                <p className="text-gray-400 text-xs font-medium mb-3">TECHNICAL INDICATORS</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {result.technical_indicators.ma_5 != null && (
                    <div>
                      <p className="text-gray-500">MA(5)</p>
                      <p className="text-white font-semibold">{formatINR(result.technical_indicators.ma_5)}</p>
                    </div>
                  )}
                  {result.technical_indicators.ma_10 != null && (
                    <div>
                      <p className="text-gray-500">MA(10)</p>
                      <p className="text-white font-semibold">{formatINR(result.technical_indicators.ma_10)}</p>
                    </div>
                  )}
                  {result.technical_indicators.ma_20 != null && (
                    <div>
                      <p className="text-gray-500">MA(20)</p>
                      <p className="text-white font-semibold">{formatINR(result.technical_indicators.ma_20)}</p>
                    </div>
                  )}
                  {result.technical_indicators.daily_return != null && (
                    <div>
                      <p className="text-gray-500">Daily Return</p>
                      <p className="text-white font-semibold">{(result.technical_indicators.daily_return * 100).toFixed(2)}%</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Input Summary */}
            {result.input_features && (
              <div className="mt-6 bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                <p className="text-gray-400 text-xs font-medium mb-3">INPUT SUMMARY</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Open</p>
                    <p className="text-white font-semibold">{formatINR(result.input_features.open)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">High</p>
                    <p className="text-white font-semibold">{formatINR(result.input_features.high)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Low</p>
                    <p className="text-white font-semibold">{formatINR(result.input_features.low)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Volume</p>
                    <p className="text-white font-semibold">{result.input_features.volume.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default PredictionForm
