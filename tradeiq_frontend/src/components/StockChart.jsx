import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
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

  const chartData = data.map((d) => ({ date: d.Date, close: d.Close }))

  return (
    <div className="card p-4">
      <h4 className="font-semibold mb-2">Stock Chart</h4>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <XAxis dataKey="date"/>
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="close" stroke="#4f46e5" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default StockChart
