import { useState, useEffect } from 'react'
import { predictionAPI, portfolioAPI } from '../services/api'
import Sidebar from '../components/Sidebar'
import StockChart from '../components/StockChart'
import PredictionChart from '../components/PredictionChart'
import CandlestickChart from '../components/CandlestickChart'
import StockTable from '../components/StockTable'

const Dashboard = () => {
  const [symbol, setSymbol] = useState('AAPL')
  const [stockData, setStockData] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [portfolio, setPortfolio] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchStock = async () => {
    try {
      const data = await predictionAPI.getHistorical(symbol)
      setStockData(data)
      setError('')
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to load stock history')
      setStockData(null)
    }
  }

  const fetchLive = async () => {
    try {
      const { price } = await predictionAPI.getLivePrice(symbol)
      setPrediction((p) => ({ ...p, current_price: price }))
      setError('')
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to load live price')
    }
  }

  const fetchPrediction = async () => {
    try {
      const pred = await predictionAPI.predict({ symbol })
      setPrediction(pred)
      setError('')
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Prediction error')
      setPrediction(null)
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
    if (!symbol) return
    setLoading(true)
    Promise.all([fetchStock(), fetchPrediction(), fetchPortfolio(), fetchLive()])
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [symbol])

  return (
    <div className="flex">
      <Sidebar />
      <div className="p-6 flex-1 max-w-6xl mx-auto">
        {loading && (
          <div className="absolute inset-0 bg-black/25 flex items-center justify-center z-20">
            <div className="loader"></div>
          </div>
        )}
      <h2 className="text-3xl font-bold mb-4">Dashboard</h2>
      <div className="mb-4">
        <label className="mr-2">Symbol:</label>
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          className="input-field w-32"
        />
      </div>

      {/* Live cards */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-4">
          <h3 className="font-semibold mb-2">Live Price</h3>
          <p className="text-xl">${prediction?.current_price?.toFixed(2) ?? 'N/A'}</p>
        </div>
        <div className="card p-4">
          <h3 className="font-semibold mb-2">Prediction</h3>
          <p className="text-xl">${prediction?.predicted_price?.toFixed(2) ?? 'N/A'}</p>
          <p className="text-sm">Trend: {prediction?.trend || 'N/A'}</p>
        </div>
        <div className="card p-4">
          <h3 className="font-semibold mb-2">Trend</h3>
          <p className="text-xl capitalize">{prediction?.trend || 'N/A'}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="mt-8 grid gap-6">
        <StockChart data={stockData?.history} />
        <PredictionChart historical={stockData?.history} predicted={prediction} />
        <CandlestickChart data={stockData?.history} />
      </div>

      {/* Portfolio preview */}
      <div className="mt-8">
        <h3 className="font-semibold mb-2">Portfolio</h3>
        {portfolio.length === 0 ? (
          <p>No holdings yet.</p>
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
