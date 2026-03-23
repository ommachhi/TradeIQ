import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const PredictionChart = ({ historical, predicted }) => {
  if (!historical || historical.length === 0) {
    return (
      <div className="card p-4">
        <h4 className="font-semibold mb-2">Prediction Chart</h4>
        <p className="text-sm">No historical data.</p>
      </div>
    )
  }

  const histData = historical.map((d) => ({ date: d.Date, close: d.Close }))
  const predPoint = predicted?.predicted_price
    ? [{ date: 'Next', close: predicted.predicted_price }]
    : []
  const combined = [...histData, ...predPoint]

  return (
    <div className="card p-4">
      <h4 className="font-semibold mb-2">Prediction Chart</h4>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={combined}>
          <XAxis dataKey="date" />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#16a34a"
            dot={false}
            name="Price"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PredictionChart
