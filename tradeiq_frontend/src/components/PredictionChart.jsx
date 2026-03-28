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

  const histData = historical.map((d) => ({
    date: d.Date || d.date,
    historical: Number(d.Close ?? d.close ?? 0),
    forecast7: null,
    forecast30: null,
  }))

  const latestDate = histData[histData.length - 1]?.date
  const latestHistorical = histData[histData.length - 1]?.historical
  const nextPrice = Number(predicted?.predicted_price ?? latestHistorical ?? 0)
  const forecast7 = Number(predicted?.forecast_7d ?? nextPrice)
  const forecast30 = Number(predicted?.forecast_30d ?? nextPrice)

  const predPoint = predicted?.predicted_price
    ? [
        { date: latestDate || 'Now', historical: latestHistorical, forecast7: null, forecast30: null },
        { date: 'Next Day', historical: null, forecast7: nextPrice, forecast30: nextPrice },
        { date: '7 Day', historical: null, forecast7, forecast30: null },
        { date: '30 Day', historical: null, forecast7: null, forecast30 },
      ]
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
            dataKey="historical"
            stroke="#16a34a"
            dot={false}
            name="Historical"
          />
          <Line
            type="monotone"
            dataKey="forecast7"
            stroke="#3b82f6"
            strokeDasharray="6 3"
            name="7-Day Forecast"
          />
          <Line
            type="monotone"
            dataKey="forecast30"
            stroke="#a855f7"
            strokeDasharray="4 4"
            name="30-Day Forecast"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PredictionChart
