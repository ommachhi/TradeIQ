import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { predictionAPI, portfolioAPI } from '../services/api'
import Sidebar from '../components/Sidebar'

const TradingViewChartPanel = lazy(() => import('../components/TradingViewChartPanel'))

const VALID_SYMBOL_REGEX = /^(?:[A-Z]{1,10}|[A-Z]{1,10}\.(?:NS|BO))$/

const confidenceToPercent = (confidence, changePercent) => {
  if (confidence === 'HIGH') return 88
  if (confidence === 'MEDIUM') return 68
  const normalized = Math.max(35, 60 - Math.abs(changePercent || 0) * 2)
  return Math.round(normalized)
}

const trendToDirection = (trend) => {
  if (trend === 'Uptrend') return 'UP'
  if (trend === 'Downtrend') return 'DOWN'
  return 'SIDEWAYS'
}

const lineSkeleton = (
  <div className="card p-6 animate-pulse">
    <div className="h-4 w-40 bg-slate-700 rounded mb-4"></div>
    <div className="h-[520px] bg-slate-800/70 rounded"></div>
  </div>
)

const Dashboard = () => {
  const [symbol, setSymbol] = useState('AAPL')
  const [debouncedSymbol, setDebouncedSymbol] = useState('AAPL')
  const [stockData, setStockData] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [timeframe, setTimeframe] = useState('1y')
  const [portfolio, setPortfolio] = useState([])
  const [watchlist, setWatchlist] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('tradeiq-watchlist') || '[]')
    } catch {
      return []
    }
  })
  const [recentSearches, setRecentSearches] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('tradeiq-recent-searches') || '[]')
    } catch {
      return []
    }
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [removingRecent, setRemovingRecent] = useState('')
  const [investmentAmount, setInvestmentAmount] = useState(10000)
  const [buyPrice, setBuyPrice] = useState(0)

  const cacheRef = useRef(new Map())

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSymbol(symbol.trim().toUpperCase())
    }, 450)
    return () => clearTimeout(timer)
  }, [symbol])

  useEffect(() => {
    localStorage.setItem('tradeiq-watchlist', JSON.stringify(watchlist))
  }, [watchlist])

  useEffect(() => {
    localStorage.setItem('tradeiq-recent-searches', JSON.stringify(recentSearches))
  }, [recentSearches])

  const buildForecast = (pred, history) => {
    if (!pred || !history?.length) {
      return pred
    }
    const latest = Number(history[history.length - 1].Close ?? history[history.length - 1].close ?? pred.current_price ?? 0)
    if (!latest || !pred.predicted_price) {
      return pred
    }
    const dayMove = (Number(pred.predicted_price) - latest) / latest
    return {
      ...pred,
      forecast_7d: Number((latest * (1 + dayMove * 7)).toFixed(2)),
      forecast_30d: Number((latest * (1 + dayMove * 30)).toFixed(2)),
    }
  }

  const fetchStock = async (activeSymbol, activeTimeframe) => {
    try {
      const data = await predictionAPI.getHistorical(activeSymbol, activeTimeframe)
      setStockData(data)
      setError('')
      return data
    } catch (err) {
      console.error(err)
      setError(err.message || 'Failed to load stock history')
      setStockData(null)
      return null
    }
  }

  const fetchLive = async (activeSymbol) => {
    try {
      const { price } = await predictionAPI.getLivePrice(activeSymbol)
      setPrediction((p) => ({ ...p, current_price: price }))
      setError('')
    } catch (err) {
      console.error(err)
      setError(err.message || 'Failed to load live price')
    }
  }

  const fetchPrediction = async (activeSymbol, historyData) => {
    try {
      const pred = await predictionAPI.predict({ symbol: activeSymbol })
      setPrediction(buildForecast(pred, historyData?.history))
      setError('')
      return pred
    } catch (err) {
      console.error(err)
      setError(err.message || 'Prediction error')
      setPrediction(null)
      return null
    }
  }

  const fetchPortfolio = async () => {
    try {
      const entries = await portfolioAPI.getEntries()
      setPortfolio(entries)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    if (!debouncedSymbol) return
    if (!VALID_SYMBOL_REGEX.test(debouncedSymbol)) {
      setError('Invalid stock symbol. Please enter a valid symbol like AAPL, RELIANCE.NS, TCS.NS')
      setStockData(null)
      setPrediction(null)
      return
    }

    const cacheKey = `${debouncedSymbol}:${timeframe}`
    const cached = cacheRef.current.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < 120000) {
      setStockData(cached.stockData)
      setPrediction(cached.prediction)
      fetchPortfolio()
      return
    }

    setLoading(true)
    Promise.all([fetchStock(debouncedSymbol, timeframe), fetchPortfolio()])
      .then(async ([historyData]) => {
        const pred = await fetchPrediction(debouncedSymbol, historyData)
        await fetchLive(debouncedSymbol)
        if (historyData && pred) {
          cacheRef.current.set(cacheKey, {
            stockData: historyData,
            prediction: buildForecast(pred, historyData.history),
            timestamp: Date.now(),
          })
          setRecentSearches((prev) => {
            const next = [debouncedSymbol, ...prev.filter((item) => item !== debouncedSymbol)].slice(0, 8)
            return next
          })
        }
      })
      .catch(() => {
        // handled in fetch methods
      })
      .finally(() => setLoading(false))
  }, [debouncedSymbol, timeframe])

  const analytics = useMemo(() => {
    const rows = stockData?.history || []
    if (!rows.length) {
      return null
    }
    const closes = rows.map((row) => Number(row.Close ?? row.close ?? 0)).filter(Boolean)
    if (!closes.length) {
      return null
    }
    const last30 = closes.slice(-30)
    const avg = last30.reduce((sum, value) => sum + value, 0) / last30.length
    const variance = last30.reduce((sum, value) => sum + (value - avg) ** 2, 0) / last30.length
    const volatilityPct = (Math.sqrt(variance) / avg) * 100
    const riskValue = Number(volatilityPct.toFixed(2))
    const riskLevel = riskValue < 1.8 ? 'Low' : riskValue < 3.5 ? 'Medium' : 'High'
    const support = Number(Math.min(...last30).toFixed(2))
    const resistance = Number(Math.max(...last30).toFixed(2))
    const confidencePct = confidenceToPercent(prediction?.confidence, prediction?.change_percent)
    return { riskValue, riskLevel, support, resistance, confidencePct }
  }, [stockData, prediction])

  const pnl = useMemo(() => {
    const predictedPrice = Number(prediction?.predicted_price || 0)
    const amount = Number(investmentAmount || 0)
    const entry = Number(buyPrice || 0)
    if (!predictedPrice || !amount || !entry) {
      return { shares: 0, profit: 0, roi: 0, estimatedValue: 0 }
    }
    const shares = amount / entry
    const estimatedValue = shares * predictedPrice
    const profit = estimatedValue - amount
    const roi = amount ? (profit / amount) * 100 : 0
    return { shares, profit, roi, estimatedValue }
  }, [prediction, investmentAmount, buyPrice])

  const addToWatchlist = () => {
    if (!VALID_SYMBOL_REGEX.test(debouncedSymbol)) {
      return
    }
    setWatchlist((prev) => {
      if (prev.includes(debouncedSymbol)) {
        return prev
      }
      return [debouncedSymbol, ...prev].slice(0, 12)
    })
  }

  const removeRecentSearch = (item) => {
    setRemovingRecent(item)
    window.setTimeout(() => {
      setRecentSearches((prev) => prev.filter((symbolItem) => symbolItem !== item))
      setRemovingRecent('')
    }, 180)
  }

  const clearAllRecentSearches = () => {
    const confirmed = window.confirm('Clear all recent searches?')
    if (!confirmed) {
      return
    }
    setRecentSearches([])
  }

  return (
    <div className="flex">
      <Sidebar />
      <div className="p-6 flex-1 max-w-6xl mx-auto relative">
        {loading && (
          <div className="absolute inset-0 bg-black/25 flex items-center justify-center z-20 rounded-xl">
            <div className="loader"></div>
          </div>
        )}

      <h2 className="text-3xl font-bold mb-4">Investor Dashboard</h2>
      <div className="mb-4 flex flex-wrap gap-3 items-center">
        <label className="text-sm text-gray-300">Symbol:</label>
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          className="input-field w-44"
          placeholder="AAPL or RELIANCE.NS"
          maxLength={20}
        />
        <button type="button" className="btn-primary" onClick={addToWatchlist}>Add Watchlist</button>
      </div>

      {recentSearches.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-300">Recent Searches</span>
            <button
              type="button"
              className="text-xs text-red-300 hover:text-red-200 transition-colors"
              onClick={clearAllRecentSearches}
            >
              Clear All
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((item) => (
              <div
                key={item}
                className={`recent-chip ${removingRecent === item ? 'is-removing' : ''}`}
              >
                <button
                  type="button"
                  className="recent-chip-symbol"
                  onClick={() => setSymbol(item)}
                >
                  {item}
                </button>
                <button
                  type="button"
                  className="recent-chip-remove"
                  onClick={() => removeRecentSearch(item)}
                  aria-label={`Remove ${item} from recent searches`}
                >
                  x
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live cards */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {!loading && !error && !stockData?.history?.length && (
        <div className="card mb-6">
          <p className="text-gray-300">No data available</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-4">
          <h3 className="font-semibold mb-2">Live Price</h3>
          <p className="text-xl">{prediction?.current_price ? `$${prediction.current_price.toFixed(2)}` : 'No data available'}</p>
        </div>
        <div className="card p-4">
          <h3 className="font-semibold mb-2">Prediction</h3>
          <p className="text-xl">{prediction?.predicted_price ? `$${prediction.predicted_price.toFixed(2)}` : 'No data available'}</p>
          <p className="text-sm">Trend: {trendToDirection(prediction?.trend)}</p>
        </div>
        <div className="card p-4">
          <h3 className="font-semibold mb-2">Trend</h3>
          <p className="text-xl capitalize">{prediction?.trend || 'No data available'}</p>
        </div>
      </div>

      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="card p-4">
            <p className="text-sm text-gray-400">Risk Score</p>
            <p className="text-2xl font-semibold">{analytics.riskValue}</p>
            <p className="text-sm text-gray-300">{analytics.riskLevel}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-400">Confidence</p>
            <p className="text-2xl font-semibold">{analytics.confidencePct}%</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-400">Support</p>
            <p className="text-2xl font-semibold">${analytics.support}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-400">Resistance</p>
            <p className="text-2xl font-semibold">${analytics.resistance}</p>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="mt-8 grid gap-6">
        <Suspense fallback={lineSkeleton}>
          <TradingViewChartPanel
            symbol={debouncedSymbol}
            data={stockData?.history}
            prediction={prediction}
            timeframe={timeframe}
            onTimeframeChange={setTimeframe}
          />
        </Suspense>
      </div>

      <div className="mt-8 card p-6">
        <h3 className="font-semibold mb-4">Investment Tools</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-300">Investment Amount</label>
            <input
              type="number"
              min="0"
              className="input-field w-full mt-1"
              value={investmentAmount}
              onChange={(e) => setInvestmentAmount(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm text-gray-300">Buy Price</label>
            <input
              type="number"
              min="0"
              className="input-field w-full mt-1"
              value={buyPrice}
              onChange={(e) => setBuyPrice(e.target.value)}
            />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
            <p className="text-xs text-gray-400">Estimated Value</p>
            <p className="text-lg font-semibold">${pnl.estimatedValue.toFixed(2)}</p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
            <p className="text-xs text-gray-400">Profit / Loss</p>
            <p className={`text-lg font-semibold ${pnl.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              ${pnl.profit.toFixed(2)}
            </p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
            <p className="text-xs text-gray-400">ROI</p>
            <p className={`text-lg font-semibold ${pnl.roi >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {pnl.roi.toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

      {/* Portfolio preview */}
      <div className="mt-8 card p-6">
        <h3 className="font-semibold mb-2">Watchlist</h3>
        {watchlist.length === 0 ? (
          <p className="text-sm text-gray-300 mb-4">No data available</p>
        ) : (
          <div className="flex flex-wrap gap-2 mb-4">
            {watchlist.map((item) => (
              <button
                key={item}
                type="button"
                className="px-2 py-1 text-xs rounded border border-slate-600 text-slate-200 hover:border-blue-400"
                onClick={() => setSymbol(item)}
              >
                {item}
              </button>
            ))}
          </div>
        )}

        <h3 className="font-semibold mb-2">Portfolio</h3>
        {portfolio.length === 0 ? (
          <p className="text-sm text-gray-300">No data available</p>
        ) : (
          <ul className="list-disc list-inside">
            {portfolio.map((entry) => (
              <li key={entry.id}>
                {entry.stock_symbol} x{entry.quantity} @ {entry.average_price}
              </li>
            ))}
          </ul>
        )}
      </div>
      </div>
    </div>
  )
}

export default Dashboard
