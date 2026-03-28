import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const StockChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="card p-4">
        <h4 className="font-semibold mb-2">Stock Chart</h4>
        <p className="text-sm">No data available.</p>
      </div>
    )
  }

  const closes = data.map((d) => Number(d.Close ?? d.close ?? 0))
  const chartData = data.map((d, index) => {
    const date = d.Date || d.date
    const close = Number(d.Close ?? d.close ?? 0)
    const ma50Slice = closes.slice(Math.max(0, index - 49), index + 1)
    const ma200Slice = closes.slice(Math.max(0, index - 199), index + 1)
    const ma50 = ma50Slice.reduce((sum, value) => sum + value, 0) / ma50Slice.length
    const ma200 = ma200Slice.reduce((sum, value) => sum + value, 0) / ma200Slice.length
    return { date, close, ma50, ma200 }
  })

  return (
    <div className="card p-4">
      <h4 className="font-semibold mb-2">Stock Chart</h4>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <XAxis dataKey="date"/>
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="close" stroke="#4f46e5" dot={false} />
          <Line type="monotone" dataKey="ma50" stroke="#10b981" dot={false} name="MA50" />
          <Line type="monotone" dataKey="ma200" stroke="#f59e0b" dot={false} name="MA200" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default StockChart
