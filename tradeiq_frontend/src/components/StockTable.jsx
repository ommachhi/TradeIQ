const StockTable = ({ rows }) => {
  return (
    <table className="min-w-full bg-slate-800 text-gray-200">
      <thead>
        <tr>
          <th className="px-4 py-2">Symbol</th>
          <th className="px-4 py-2">Price</th>
          <th className="px-4 py-2">Change</th>
        </tr>
      </thead>
      <tbody>
        {rows?.map((r) => (
          <tr key={r.symbol} className="border-b border-slate-700">
            <td className="px-4 py-2">{r.symbol}</td>
            <td className="px-4 py-2">{r.price}</td>
            <td className="px-4 py-2">{r.change}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default StockTable
