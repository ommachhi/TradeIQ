import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

/**
 * ChartView Component
 * Displays historical stock data using Recharts
 */
const ChartView = ({ historicalData }) => {
  const [chartData, setChartData] = useState([])

  useEffect(() => {
    if (historicalData && historicalData.length > 0) {
      // Process data for chart
      const processedData = historicalData.slice(-60).map((item) => ({
        date: item.Date,
        open: parseFloat(item.Open),
        high: parseFloat(item.High),
        low: parseFloat(item.Low),
        close: parseFloat(item.Close),
        volume: item.Volume,
      }))
      setChartData(processedData)
    }
  }, [historicalData])

  if (!chartData || chartData.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-400">Loading chart data...</p>
      </div>
    )
  }

  const minPrice = Math.min(...chartData.map((d) => d.low)) - 5
  const maxPrice = Math.max(...chartData.map((d) => d.high)) + 5

  return (
    <div className="card card-hover">
      <h2 className="text-2xl font-bold mb-6 text-white">Historical Stock Price</h2>

      <div className="w-full h-96 bg-slate-800/50 rounded-lg p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="colorOpen" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="date"
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
              interval={Math.floor(chartData.length / 6)}
            />
            <YAxis
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
              domain={[minPrice, maxPrice]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#e2e8f0',
              }}
              cursor={{ stroke: '#64748b' }}
              formatter={(value) => `$${value.toFixed(2)}`}
            />
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              textStyle={{ color: '#cbd5e1' }}
            />

            <Line
              type="monotone"
              dataKey="open"
              stroke="#3b82f6"
              dot={false}
              name="Open Price"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="close"
              stroke="#8b5cf6"
              dot={false}
              name="Close Price"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="high"
              stroke="#10b981"
              dot={false}
              name="High Price"
              strokeWidth={1}
              strokeDasharray="5 5"
              opacity={0.6}
            />
            <Line
              type="monotone"
              dataKey="low"
              stroke="#ef4444"
              dot={false}
              name="Low Price"
              strokeWidth={1}
              strokeDasharray="5 5"
              opacity={0.6}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <p className="text-gray-400 text-xs font-medium">Latest Close</p>
          <p className="text-xl font-bold text-purple-400 mt-1">
            ${chartData[chartData.length - 1].close.toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <p className="text-gray-400 text-xs font-medium">Highest</p>
          <p className="text-xl font-bold text-green-400 mt-1">
            ${Math.max(...chartData.map((d) => d.high)).toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <p className="text-gray-400 text-xs font-medium">Lowest</p>
          <p className="text-xl font-bold text-red-400 mt-1">
            ${Math.min(...chartData.map((d) => d.low)).toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <p className="text-gray-400 text-xs font-medium">Data Points</p>
          <p className="text-xl font-bold text-blue-400 mt-1">{chartData.length}</p>
        </div>
      </div>
    </div>
  )
}

export default ChartView
