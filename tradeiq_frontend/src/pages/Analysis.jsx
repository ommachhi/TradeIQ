import { useState, useEffect } from 'react'
import ChartView from '../components/ChartView'
import Sidebar from '../components/Sidebar'
import { predictionAPI } from '../services/api'

/**
 * Analysis Page
 * Historical data visualization and analysis
 */
const Analysis = () => {
  const [historicalData, setHistoricalData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL')
  const [selectedPeriod, setSelectedPeriod] = useState('1y')

  const popularSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']

  const fetchData = async (symbol = selectedSymbol, period = selectedPeriod) => {
    try {
      setLoading(true)
      const resp = await predictionAPI.getHistorical(symbol)
      let data = resp.history || []

      // slice according to period
      if (period && data.length > 0) {
        const now = new Date(data[data.length - 1].Date)
        let days = {
          '1d': 1,
          '5d': 5,
          '1mo': 30,
          '3mo': 90,
          '6mo': 180,
          '1y': 365,
          '2y': 730,
          '5y': 1825,
        }[period]
        if (days) {
          data = data.filter((d) => {
            const dt = new Date(d.Date)
            return (now - dt) / (1000 * 60 * 60 * 24) <= days
          })
        }
      }

      setHistoricalData(data)
      setError(null)
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Please log in to view market data.')
      } else {
        setError(`Failed to load data for ${symbol}. Make sure the backend is running.`)
      }
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleSymbolChange = (symbol) => {
    setSelectedSymbol(symbol)
    fetchData(symbol, selectedPeriod)
  }

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period)
    fetchData(selectedSymbol, period)
  }

  return (
    <div className="flex">
      <Sidebar />
      <div className="min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4 flex-1">
      {/* Animated Background Elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl opacity-20 -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl opacity-20 translate-x-1/2 translate-y-1/2"></div>

      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 text-white">
            Market <span className="gradient-text">Analysis</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Explore historical stock price trends and patterns with interactive charts
          </p>
        </div>

        {/* Symbol and Period Selector */}
        <div className="card card-hover mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Symbol Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Stock Symbol
              </label>
              <div className="flex flex-wrap gap-2">
                {popularSymbols.map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => handleSymbolChange(symbol)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      selectedSymbol === symbol
                        ? 'bg-blue-500 text-white'
                        : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                    }`}
                  >
                    {symbol}
                  </button>
                ))}
              </div>
              <input
                type="text"
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
                onKeyPress={(e) => e.key === 'Enter' && handleSymbolChange(selectedSymbol)}
                placeholder="Or enter custom symbol"
                className="input-field w-full mt-3"
                maxLength="20"
              />
            </div>

            {/* Period Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Time Period
              </label>
              <div className="flex flex-wrap gap-2">
                {['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'].map((period) => (
                  <button
                    key={period}
                    onClick={() => handlePeriodChange(period)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      selectedPeriod === period
                        ? 'bg-purple-500 text-white'
                        : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                    }`}
                  >
                    {period}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="card text-center py-16">
            <div className="inline-block">
              <div className="loading-spinner mb-4"></div>
              <p className="text-gray-400">Loading market data...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="card bg-red-500/10 border border-red-500/30 text-center py-8 mb-8">
            <p className="text-red-300 font-medium mb-2">⚠️ Error Loading Data</p>
            <p className="text-red-200 text-sm">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 btn-primary"
            >
              Retry
            </button>
          </div>
        )}

        {/* Chart Section */}
        {historicalData && !loading && (
          <>
            <ChartView historicalData={historicalData} />

            {/* Statistics Section */}
            <div className="mt-12 grid md:grid-cols-3 gap-6">
              {/* Stats Card 1 */}
              <div className="card card-hover">
                <p className="text-gray-400 text-sm font-medium mb-2">Data Coverage</p>
                <p className="text-3xl font-bold text-blue-400">
                  {historicalData.length} Days
                </p>
                <p className="text-gray-500 text-xs mt-2">
                  From {historicalData[0]?.date} to {historicalData[historicalData.length - 1]?.date}
                </p>
              </div>

              {/* Stats Card 2 */}
              <div className="card card-hover">
                <p className="text-gray-400 text-sm font-medium mb-2">Average Volume</p>
                <p className="text-3xl font-bold text-purple-400">
                  {(
                    historicalData.reduce((sum, d) => sum + d.Volume, 0) /
                    historicalData.length /
                    1000000
                  ).toFixed(2)}
                </p>
                <p className="text-gray-500 text-xs mt-2">Million shares</p>
              </div>

              {/* Stats Card 3 */}
              <div className="card card-hover">
                <p className="text-gray-400 text-sm font-medium mb-2">Price Range</p>
                <p className="text-3xl font-bold text-green-400">
                  $
                  {(
                    Math.max(...historicalData.map((d) => d.Close)) -
                    Math.min(...historicalData.map((d) => d.Close))
                  ).toFixed(2)}
                </p>
                <p className="text-gray-500 text-xs mt-2">Min to max range</p>
              </div>
            </div>

            {/* Insights Section */}
            <div className="mt-12 card bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-purple-500/30">
              <h3 className="text-xl font-bold text-white mb-4">📊 Market Insights</h3>
              <ul className="space-y-3 text-gray-300 text-sm">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3">✓</span>
                  <span>
                    Total historical data points: <strong>{historicalData.length}</strong> trading days
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-3">✓</span>
                  <span>
                    Latest closing price: <strong>${historicalData[historicalData.length - 1]?.close.toFixed(2)}</strong>
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-3">✓</span>
                  <span>
                    Average daily volume: <strong>
                      {(
                        historicalData.reduce((sum, d) => sum + d.volume, 0) /
                        historicalData.length /
                        1000000
                      ).toFixed(2)}
                    </strong> million shares
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-yellow-400 mr-3">✓</span>
                  <span>
                    Price volatility: <strong>
                      {(
                        ((Math.max(...historicalData.map((d) => d.close)) -
                          Math.min(...historicalData.map((d) => d.close))) /
                          (historicalData.reduce((sum, d) => sum + d.close, 0) /
                            historicalData.length)) *
                        100
                      ).toFixed(2)}
                      %
                    </strong>
                  </span>
                </li>
              </ul>
            </div>
          </>
        )}
      </div>
      </div>
    </div>
  )
}

export default Analysis
