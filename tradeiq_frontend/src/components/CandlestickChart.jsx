import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  ResponsiveContainer,
} from 'recharts'

const CandlestickChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="card p-4">
        <h4 className="font-semibold mb-2">Price & Volume</h4>
        <p className="text-sm">No data available.</p>
      </div>
    )
  }

  const chartData = data.map((d) => ({
    date: d.Date,
    open: d.Open,
    high: d.High,
    low: d.Low,
    close: d.Close,
    volume: d.Volume,
  }))

  return (
    <div className="card p-4">
      <h4 className="font-semibold mb-2">Price & Volume</h4>
      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={chartData}>
          <XAxis dataKey="date" />
          <YAxis yAxisId="price" domain={["auto", "auto"]} />
          <YAxis
            yAxisId="volume"
            orientation="right"
            tickFormatter={(v) => v / 1000 + 'k'}
            domain={["auto", "auto"]}
          />
          <Tooltip />
          <Bar yAxisId="volume" dataKey="volume" barSize={20} fill="#8884d8" />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            stroke="#82ca9d"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

export default CandlestickChart
