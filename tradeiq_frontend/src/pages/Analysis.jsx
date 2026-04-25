import { startTransition, useDeferredValue, useEffect, useMemo, useState } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  FiActivity,
  FiAlertCircle,
  FiArrowRight,
  FiBarChart2,
  FiClock,
  FiExternalLink,
  FiFileText,
  FiInfo,
  FiLayers,
  FiMessageSquare,
  FiRefreshCw,
  FiSearch,
  FiShield,
  FiTarget,
  FiTrendingDown,
  FiTrendingUp,
} from 'react-icons/fi'

import Sidebar from '../components/Sidebar'
import { researchAPI } from '../services/api'

const STOCK_DIRECTORY = [
  { symbol: 'RELIANCE', company: 'Reliance Industries', exchange: 'NSE' },
  { symbol: 'TCS', company: 'Tata Consultancy Services', exchange: 'NSE' },
  { symbol: 'INFY', company: 'Infosys', exchange: 'NSE' },
  { symbol: 'HDFCBANK', company: 'HDFC Bank', exchange: 'NSE' },
  { symbol: 'ICICIBANK', company: 'ICICI Bank', exchange: 'NSE' },
  { symbol: 'SBIN', company: 'State Bank of India', exchange: 'NSE' },
  { symbol: 'ITC', company: 'ITC', exchange: 'NSE' },
  { symbol: 'LT', company: 'Larsen & Toubro', exchange: 'NSE' },
  { symbol: 'WIPRO', company: 'Wipro', exchange: 'NSE' },
  { symbol: 'HCLTECH', company: 'HCL Technologies', exchange: 'NSE' },
  { symbol: 'AAPL', company: 'Apple', exchange: 'NASDAQ' },
  { symbol: 'MSFT', company: 'Microsoft', exchange: 'NASDAQ' },
  { symbol: 'NVDA', company: 'NVIDIA', exchange: 'NASDAQ' },
  { symbol: 'GOOGL', company: 'Alphabet', exchange: 'NASDAQ' },
  { symbol: 'AMZN', company: 'Amazon', exchange: 'NASDAQ' },
  { symbol: 'TSLA', company: 'Tesla', exchange: 'NASDAQ' },
]

const TIME_RANGES = [['1d', '1D'], ['1w', '1W'], ['1m', '1M'], ['1y', '1Y']]
const CHART_TABS = [['trend', 'Trend'], ['range', 'Range + Volume']]

const INDICATOR_COPY = {
  ma: 'MA smooths closing prices to reveal the broader direction of the trend.',
  ema: 'EMA reacts faster to recent price changes and helps spot momentum shifts earlier.',
  rsi: 'RSI measures price momentum. Below 30 can signal oversold, above 70 can signal overbought.',
  macd: 'MACD compares fast and slow EMAs to highlight momentum acceleration or slowdown.',
  sr: 'Support and resistance highlight zones where price has recently found buyers or sellers.',
  trend: 'Trend blends EMA structure, RSI, and MACD to classify the current market regime.',
}

const currencySymbol = (currency) => {
  if (currency === 'INR') return 'Rs.'
  if (currency === 'USD') return '$'
  return currency ? `${currency} ` : ''
}

const formatCurrency = (value, currency = 'USD', digits = 2) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return `${currencySymbol(currency)}${Number(value).toLocaleString('en-IN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })}`
}

const formatCompact = (value) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return Intl.NumberFormat('en-IN', { notation: 'compact', maximumFractionDigits: 2 }).format(Number(value))
}

const formatPercent = (value, digits = 2) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return `${Number(value).toFixed(digits)}%`
}

const changeTone = (value) => {
  if (value > 0) return 'text-emerald-400'
  if (value < 0) return 'text-rose-400'
  return 'text-amber-300'
}

const badgeTone = (value) => {
  if (value === 'BUY' || value === 'Positive' || value === 'Uptrend' || value === 'Up' || value === 'Low') {
    return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
  }
  if (value === 'SELL' || value === 'Negative' || value === 'Downtrend' || value === 'Down' || value === 'High') {
    return 'bg-rose-500/10 text-rose-300 border-rose-500/20'
  }
  return 'bg-amber-500/10 text-amber-300 border-amber-500/20'
}

const recommendationTone = (value) => {
  if (value === 'BUY') return 'bg-emerald-500/15 text-emerald-200 border-emerald-500/30'
  if (value === 'SELL') return 'bg-rose-500/15 text-rose-200 border-rose-500/30'
  return 'bg-amber-500/15 text-amber-200 border-amber-500/30'
}

const riskTone = (value) => {
  if (value === 'Low') return 'text-emerald-300'
  if (value === 'High') return 'text-rose-300'
  return 'text-amber-300'
}

const formatDateTime = (value) => {
  if (!value) return '--'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(parsed)
}

const calcMovingAverage = (rows, length) => rows.map((row, index, list) => {
  const start = Math.max(0, index - length + 1)
  const window = list.slice(start, index + 1)
  const sum = window.reduce((total, item) => total + item.close, 0)
  return {
    label: row.label,
    value: sum / window.length,
  }
})

const SectionTitle = ({ eyebrow, title, description, icon: Icon }) => (
  <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
    <div>
      <p className="text-[11px] font-bold uppercase tracking-[0.28em] text-slate-500">{eyebrow}</p>
      <div className="mt-2 flex items-center gap-3">
        {Icon && <Icon className="text-blue-300" size={18} />}
        <h2 className="text-xl font-black tracking-tight text-white md:text-2xl">{title}</h2>
      </div>
      {description && <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{description}</p>}
    </div>
  </div>
)

const MetricCard = ({ label, value, detail, tone = 'text-white', subtext }) => (
  <div className="rounded-[1.5rem] border border-slate-800/70 bg-slate-950/60 p-5 shadow-[0_10px_30px_rgba(2,6,23,0.28)]">
    <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">{label}</p>
    <p className={`mt-3 text-2xl font-black tracking-tight ${tone}`}>{value}</p>
    {detail && <p className="mt-2 text-xs text-slate-400">{detail}</p>}
    {subtext && <p className="mt-3 text-xs leading-5 text-slate-500">{subtext}</p>}
  </div>
)

const InsightChip = ({ label, value, tone = 'bg-slate-800 text-slate-200 border-slate-700' }) => (
  <div className={`rounded-full border px-3 py-1 text-xs font-semibold ${tone}`}>
    <span className="text-slate-400">{label}:</span> <span>{value}</span>
  </div>
)

const NewsCard = ({ item }) => (
  <a
    href={item.url || '#'}
    target={item.url ? '_blank' : '_self'}
    rel="noreferrer"
    className="group block rounded-[1.4rem] border border-slate-800/70 bg-slate-950/60 p-5 transition-all hover:border-blue-500/30 hover:bg-blue-500/5"
  >
    <div className="flex items-start justify-between gap-4">
      <div>
        <p className="text-sm font-semibold text-white group-hover:text-blue-100">{item.headline}</p>
        <p className="mt-2 text-xs text-slate-400">
          {item.source || 'Market Wire'} • {formatDateTime(item.published_at)}
        </p>
      </div>
      <span className={`shrink-0 rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-[0.2em] ${badgeTone(item.sentiment)}`}>
        {item.sentiment || 'Neutral'}
      </span>
    </div>
    {item.url && <p className="mt-4 flex items-center gap-2 text-xs font-semibold text-blue-300 opacity-80 transition-opacity group-hover:opacity-100"><FiExternalLink size={12} /> Open source</p>}
  </a>
)

const searchSymbol = (input) => (input || '').trim().toUpperCase()

const SearchSuggestion = ({ item, onSelect }) => (
  <button type="button" onClick={() => onSelect(item.symbol)} className="flex w-full items-center justify-between rounded-2xl border border-transparent bg-slate-900/70 px-4 py-3 text-left transition-all hover:border-blue-500/20 hover:bg-blue-500/5">
    <div>
      <p className="font-semibold text-white">{item.company}</p>
      <p className="mt-1 text-xs text-slate-400">{item.symbol} • {item.exchange}</p>
    </div>
    <span className="rounded-full bg-slate-800 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.2em] text-blue-300">Pick</span>
  </button>
)

const OverviewCard = ({ label, value, detail, tone = 'text-white' }) => (
  <div className="rounded-[1.5rem] border border-slate-800/70 bg-slate-900/60 p-5 shadow-[0_10px_30px_rgba(2,6,23,0.28)]">
    <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">{label}</p>
    <p className={`mt-3 text-2xl font-black tracking-tight ${tone}`}>{value}</p>
    {detail && <p className="mt-2 text-xs text-slate-400">{detail}</p>}
  </div>
)

const IndicatorCard = ({ label, value, hint, accent = 'text-white' }) => (
  <div className="rounded-[1.5rem] border border-slate-800/70 bg-slate-900/55 p-5">
    <div className="flex items-center justify-between gap-3">
      <p className="text-sm font-bold text-slate-200">{label}</p>
      <span title={hint} className="rounded-full border border-slate-700 p-1 text-slate-500"><FiInfo size={12} /></span>
    </div>
    <p className={`mt-4 text-2xl font-black tracking-tight ${accent}`}>{value}</p>
    <p className="mt-2 text-xs leading-5 text-slate-400">{hint}</p>
  </div>
)

const LoadingShell = () => (
  <div className="space-y-6 animate-pulse">
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {Array.from({ length: 4 }).map((_, index) => <div key={index} className="rounded-[1.5rem] border border-slate-800/70 bg-slate-900/60 p-6"><div className="h-3 w-24 rounded bg-slate-800"></div><div className="mt-5 h-8 w-32 rounded bg-slate-800"></div><div className="mt-4 h-3 w-40 rounded bg-slate-800"></div></div>)}
    </div>
    <div className="grid gap-6 xl:grid-cols-[1.4fr,0.8fr]">
      <div className="h-[420px] rounded-[2rem] border border-slate-800/70 bg-slate-900/60"></div>
      <div className="h-[420px] rounded-[2rem] border border-slate-800/70 bg-slate-900/60"></div>
    </div>
  </div>
)

const Analysis = () => {
  const [searchValue, setSearchValue] = useState('RELIANCE')
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE')
  const [rangeKey, setRangeKey] = useState('1m')
  const [chartMode, setChartMode] = useState('trend')
  const [panel, setPanel] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const deferredSearch = useDeferredValue(searchValue)

  const suggestions = useMemo(() => {
    const query = deferredSearch.trim().toLowerCase()
    if (!query) return STOCK_DIRECTORY.slice(0, 6)
    return STOCK_DIRECTORY.filter((stock) => `${stock.symbol} ${stock.company} ${stock.exchange}`.toLowerCase().includes(query)).slice(0, 6)
  }, [deferredSearch])

  const loadResearch = async (symbol = selectedSymbol, nextRange = rangeKey) => {
    try {
      setLoading(true)
      const data = await researchAPI.getPanel(symbol, nextRange)
      setPanel(data)
      setError('')
    } catch (err) {
      setError(err.message || 'Research panel data load nahi ho paaya.')
      setPanel(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadResearch(selectedSymbol, rangeKey)
  }, [selectedSymbol, rangeKey])

  const applySymbol = (symbol) => {
    const nextSymbol = searchSymbol(symbol)
    if (!nextSymbol) return
    startTransition(() => {
      setSearchValue(nextSymbol)
      setSelectedSymbol(nextSymbol)
    })
  }

  const submitSearch = (event) => {
    event.preventDefault()
    applySymbol(searchValue)
  }

  const chartPoints = panel?.chart?.points || []
  const overview = panel?.overview || {}
  const technical = panel?.technical_analysis || {}
  const movingAverages = technical?.moving_averages || {}
  const prediction = panel?.ai_prediction || {}
  const sentiment = panel?.news_sentiment?.summary || {}
  const newsItems = panel?.news_sentiment?.items || []
  const recommendation = panel?.recommendation || {}
  const directoryEntry = useMemo(
    () => STOCK_DIRECTORY.find((item) => item.symbol === selectedSymbol),
    [selectedSymbol]
  )

  const chartRows = useMemo(
    () =>
      chartPoints
        .map((point) => ({
          label: point.label || point.timestamp?.slice(0, 10) || '--',
          timestamp: point.timestamp || '',
          open: Number(point.open ?? 0),
          high: Number(point.high ?? 0),
          low: Number(point.low ?? 0),
          close: Number(point.close ?? 0),
          volume: Number(point.volume ?? 0),
        }))
        .filter((point) => point.label && Number.isFinite(point.close)),
    [chartPoints]
  )

  const latestBar = chartRows[chartRows.length - 1] || {}

  const chartMAs = useMemo(
    () => ({
      ma20: calcMovingAverage(chartRows, 20),
      ma50: calcMovingAverage(chartRows, 50),
    }),
    [chartRows]
  )

  const chartPayload = useMemo(
    () =>
      chartRows.map((row, index) => ({
        ...row,
        ma20: chartMAs.ma20[index]?.value ?? null,
        ma50: chartMAs.ma50[index]?.value ?? null,
      })),
    [chartRows, chartMAs]
  )

  const performanceState = useMemo(() => {
    if (!chartRows.length) return { tone: 'text-slate-300', label: 'No data' }
    const first = chartRows[0].close
    const last = chartRows[chartRows.length - 1].close
    if (last > first) return { tone: 'text-emerald-300', label: 'Bullish structure' }
    if (last < first) return { tone: 'text-rose-300', label: 'Bearish structure' }
    return { tone: 'text-amber-300', label: 'Sideways structure' }
  }, [chartRows])

  const confidenceLabel =
    prediction.confidence_label ||
    (prediction.confidence_pct >= 75 ? 'High' : prediction.confidence_pct >= 60 ? 'Medium' : 'Low')
  const riskLevel =
    prediction.risk_level ||
    (prediction.risk_score >= 65 ? 'High' : prediction.risk_score >= 35 ? 'Medium' : 'Low')

  const chartContent = chartMode === 'trend' ? (
    <AreaChart data={chartPayload}>
      <defs>
        <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.35} />
          <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.02} />
        </linearGradient>
      </defs>
      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
      <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
      <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} domain={['auto', 'auto']} />
      <Tooltip
        contentStyle={{ background: '#0f172a', border: '1px solid #1f2937', borderRadius: '16px' }}
        labelStyle={{ color: '#e2e8f0' }}
      />
      <ReferenceLine y={technical.support} stroke="#34d399" strokeDasharray="4 4" label={{ value: 'Support', fill: '#34d399', fontSize: 11 }} />
      <ReferenceLine y={technical.resistance} stroke="#fb7185" strokeDasharray="4 4" label={{ value: 'Resistance', fill: '#fb7185', fontSize: 11 }} />
      <Area type="monotone" dataKey="close" stroke="#38bdf8" fill="url(#priceFill)" strokeWidth={3} />
      <Line type="monotone" dataKey="ma20" stroke="#f59e0b" strokeWidth={2} dot={false} />
      <Line type="monotone" dataKey="ma50" stroke="#10b981" strokeWidth={2} dot={false} />
    </AreaChart>
  ) : (
    <ComposedChart data={chartPayload}>
      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
      <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
      <YAxis yAxisId="price" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} domain={['auto', 'auto']} />
      <YAxis yAxisId="volume" orientation="right" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
      <Tooltip
        contentStyle={{ background: '#0f172a', border: '1px solid #1f2937', borderRadius: '16px' }}
        labelStyle={{ color: '#e2e8f0' }}
      />
      <ReferenceLine yAxisId="price" y={technical.support} stroke="#34d399" strokeDasharray="4 4" />
      <ReferenceLine yAxisId="price" y={technical.resistance} stroke="#fb7185" strokeDasharray="4 4" />
      <Bar yAxisId="volume" dataKey="volume" fill="#334155" radius={[8, 8, 0, 0]} />
      <Line yAxisId="price" type="monotone" dataKey="close" stroke="#60a5fa" strokeWidth={3} dot={false} />
    </ComposedChart>
  )

  return (
    <div className="flex">
      <Sidebar />
      <div className="relative min-h-[calc(100vh-64px)] flex-1 overflow-hidden bg-[#07111f] px-4 py-8 md:px-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.18),_transparent_34%),radial-gradient(circle_at_bottom_right,_rgba(16,185,129,0.12),_transparent_28%),linear-gradient(180deg,_rgba(7,17,31,0.96),_rgba(4,10,20,1))]" />
        <div className="absolute left-0 top-10 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-72 w-72 rounded-full bg-emerald-500/10 blur-3xl" />

        <div className="relative z-10 mx-auto max-w-7xl">
          <section className="rounded-[2rem] border border-slate-800/80 bg-slate-950/55 p-6 shadow-[0_20px_80px_rgba(2,6,23,0.45)] md:p-8">
            <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
              <div className="max-w-2xl">
                <p className="text-xs font-bold uppercase tracking-[0.32em] text-blue-300/80">TradeIQ Research Panel</p>
                <h1 className="mt-4 font-[Outfit] text-4xl font-black tracking-tight text-white md:text-5xl">
                  Deep stock research for smarter entries, exits, and conviction.
                </h1>
                <p className="mt-4 text-base leading-7 text-slate-400">
                  Search any supported stock, inspect technical structure, review AI projection, scan market sentiment, and finish with a clear buy, sell, or hold view.
                </p>
              </div>

              <div className="w-full max-w-2xl">
                <form onSubmit={submitSearch} className="relative">
                  <div className="flex flex-col gap-3 rounded-[1.5rem] border border-slate-800 bg-slate-900/80 p-3 shadow-[0_12px_30px_rgba(2,6,23,0.38)] md:flex-row">
                    <div className="relative flex-1">
                      <FiSearch className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                      <input
                        value={searchValue}
                        onChange={(event) => setSearchValue(event.target.value.toUpperCase())}
                        placeholder="Search symbol or company name"
                        className="w-full rounded-2xl border border-slate-800 bg-slate-950/70 py-3 pl-11 pr-4 text-white outline-none transition-all focus:border-blue-500/40"
                        maxLength={20}
                      />
                    </div>
                    <button type="submit" className="rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 px-6 py-3 font-semibold text-white transition-transform hover:-translate-y-0.5">
                      Load Research
                    </button>
                  </div>

                  {suggestions.length > 0 && deferredSearch.trim() && (
                    <div className="absolute left-0 right-0 top-[calc(100%+12px)] z-20 space-y-2 rounded-[1.5rem] border border-slate-800 bg-[#07111f]/95 p-3 shadow-[0_18px_40px_rgba(2,6,23,0.55)] backdrop-blur">
                      {suggestions.map((item) => <SearchSuggestion key={item.symbol} item={item} onSelect={applySymbol} />)}
                    </div>
                  )}
                </form>

                <div className="mt-4 flex flex-wrap gap-2">
                  {directoryEntry && (
                    <div className="rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-200">
                      {directoryEntry.company} • {directoryEntry.exchange}
                    </div>
                  )}
                  {STOCK_DIRECTORY.slice(0, 8).map((item) => (
                    <button
                      key={item.symbol}
                      type="button"
                      onClick={() => applySymbol(item.symbol)}
                      className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition-all ${
                        selectedSymbol === item.symbol
                          ? 'border-blue-400/60 bg-blue-500/10 text-blue-200'
                          : 'border-slate-700 bg-slate-900/70 text-slate-400 hover:border-slate-500 hover:text-white'
                      }`}
                    >
                      {item.symbol}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <div className="mt-8">
            {loading ? (
              <LoadingShell />
            ) : error ? (
              <div className="rounded-[2rem] border border-rose-500/20 bg-rose-500/10 p-8 text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-rose-500/10 text-rose-300">
                  <FiAlertCircle size={28} />
                </div>
                <h2 className="mt-5 text-2xl font-black text-white">Research feed unavailable</h2>
                <p className="mt-3 text-sm text-rose-100/80">{error}</p>
                <button type="button" onClick={() => loadResearch()} className="mt-6 inline-flex items-center gap-2 rounded-2xl border border-rose-400/20 bg-slate-950/40 px-5 py-3 text-sm font-semibold text-white hover:border-rose-300/40">
                  <FiRefreshCw size={16} />
                  Retry
                </button>
              </div>
            ) : (
              <div className="space-y-8">
                <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  <OverviewCard label="Company" value={overview.company_name || panel?.company_name || '--'} detail={overview.symbol ? `${overview.symbol} • ${overview.currency || 'USD'} market feed` : 'Awaiting symbol'} />
                  <OverviewCard label="Current Price" value={formatCurrency(overview.current_price, overview.currency)} detail={`${formatCurrency(overview.price_change, overview.currency)} | ${formatPercent(overview.price_change_pct)}`} tone={changeTone(overview.price_change)} />
                  <OverviewCard label="Market Cap" value={formatCompact(overview.market_cap)} detail="Near real-time company value snapshot" />
                  <OverviewCard label="Volume" value={formatCompact(overview.volume)} detail="Latest traded volume" />
                  <OverviewCard label="52 Week High" value={formatCurrency(overview.fifty_two_week_high, overview.currency)} detail="High over the last one year" />
                  <OverviewCard label="52 Week Low" value={formatCurrency(overview.fifty_two_week_low, overview.currency)} detail="Low over the last one year" />
                </section>

                <section className="grid gap-6 xl:grid-cols-[1.35fr,0.65fr]">
                  <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/60 p-6 shadow-[0_14px_48px_rgba(2,6,23,0.32)]">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                      <SectionTitle
                        eyebrow="Interactive Charts"
                        title="Price action, trend, and volume"
                        description="Switch between a cleaner trend view and a volume-heavy structure view. Support and resistance are drawn from the latest market window."
                        icon={FiBarChart2}
                      />
                      <div className="flex flex-wrap gap-2">
                        {TIME_RANGES.map(([value, label]) => (
                          <button
                            key={value}
                            type="button"
                            onClick={() => setRangeKey(value)}
                            className={`rounded-full border px-4 py-2 text-xs font-bold uppercase tracking-[0.2em] transition-all ${
                              rangeKey === value
                                ? 'border-blue-400/60 bg-blue-500/10 text-blue-200'
                                : 'border-slate-700 bg-slate-900/60 text-slate-400 hover:border-slate-500 hover:text-white'
                            }`}
                          >
                            {label}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="mt-5 flex flex-wrap items-center gap-3">
                      {CHART_TABS.map(([value, label]) => (
                        <button
                          key={value}
                          type="button"
                          onClick={() => setChartMode(value)}
                          className={`rounded-full px-4 py-2 text-sm font-semibold transition-all ${
                            chartMode === value
                              ? 'bg-white text-slate-950'
                              : 'border border-slate-700 bg-slate-900/70 text-slate-400 hover:border-slate-500 hover:text-white'
                          }`}
                        >
                          {label}
                        </button>
                      ))}
                      <div className="rounded-full border border-slate-800 bg-slate-900/60 px-4 py-2 text-xs font-semibold text-slate-400">
                        Updated {formatDateTime(overview.as_of)}
                      </div>
                    </div>

                    <div className="mt-6 h-[420px] rounded-[1.5rem] border border-slate-800/70 bg-[#08101d] p-4">
                      <ResponsiveContainer width="100%" height="100%">
                        {chartContent}
                      </ResponsiveContainer>
                    </div>

                    <div className="mt-5 grid gap-3 md:grid-cols-3">
                      <InsightChip label="Trend" value={technical.trend || performanceState.label} tone={badgeTone(technical.trend || performanceState.label)} />
                      <InsightChip label="Support" value={formatCurrency(technical.support, overview.currency)} tone="bg-emerald-500/10 text-emerald-200 border-emerald-500/20" />
                      <InsightChip label="Resistance" value={formatCurrency(technical.resistance, overview.currency)} tone="bg-rose-500/10 text-rose-200 border-rose-500/20" />
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/60 p-6">
                      <SectionTitle
                        eyebrow="AI Prediction"
                        title="Price outlook and risk"
                        description="Prediction is derived from the market snapshot plus the in-house model output. Confidence and risk are surfaced as decision support, not a guarantee."
                        icon={FiTarget}
                      />
                      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                        <MetricCard label="Predicted Price" value={formatCurrency(prediction.predicted_price, overview.currency)} detail={`Direction: ${prediction.direction || 'Sideways'}`} tone={prediction.direction === 'Down' ? 'text-rose-300' : prediction.direction === 'Up' ? 'text-emerald-300' : 'text-amber-300'} />
                        <MetricCard label="Confidence" value={`${formatPercent(prediction.confidence_pct)} / ${confidenceLabel}`} detail="Model confidence in the next move" tone={confidenceLabel === 'High' ? 'text-emerald-300' : confidenceLabel === 'Low' ? 'text-rose-300' : 'text-amber-300'} />
                        <MetricCard label="Risk Score" value={`${prediction.risk_score || 0}/100`} detail={`Risk level: ${riskLevel}`} tone={riskTone(riskLevel)} />
                        <MetricCard label="Projected Change" value={formatPercent(prediction.change_percent)} detail={prediction.warning || 'Prediction based on latest data and model output'} tone={prediction.change_percent < 0 ? 'text-rose-300' : 'text-emerald-300'} />
                      </div>
                      <div className="mt-5 rounded-[1.4rem] border border-slate-800/70 bg-slate-900/60 p-4">
                        <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">Model note</p>
                        <p className="mt-2 text-sm leading-6 text-slate-300">{prediction.warning || 'Prediction is generated from recent market features and should be used with technical confirmation.'}</p>
                      </div>
                    </div>

                    <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/60 p-6">
                      <SectionTitle
                        eyebrow="Decision Support"
                        title="Final recommendation"
                        description="Recommendation combines AI direction, trend structure, momentum, and sentiment in one view."
                        icon={FiShield}
                      />
                      <div className={`rounded-[1.5rem] border p-5 ${recommendationTone(recommendation.action)}`}>
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <p className="text-xs font-bold uppercase tracking-[0.2em] opacity-80">Action</p>
                            <p className="mt-2 text-3xl font-black tracking-tight">{recommendation.action || 'HOLD'}</p>
                          </div>
                          <div className="rounded-full bg-slate-950/30 px-4 py-2 text-sm font-semibold">
                            Score {recommendation.score ?? 0}
                          </div>
                        </div>
                        <p className="mt-4 text-sm leading-6 text-white/90">{recommendation.reason || 'Signals are mixed, so waiting for stronger confirmation is safer.'}</p>
                        <div className="mt-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] opacity-80">
                          <FiArrowRight size={12} />
                          Decision support summary
                        </div>
                      </div>
                    </div>
                  </div>
                </section>

                <section className="grid gap-6 xl:grid-cols-[0.95fr,1.05fr]">
                  <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/60 p-6">
                    <SectionTitle
                      eyebrow="Technical Analysis"
                      title="Indicator snapshot"
                      description="Each indicator is paired with a short explanation so the panel works for both investors and analysts."
                      icon={FiActivity}
                    />

                    <div className="grid gap-4 md:grid-cols-2">
                      <IndicatorCard label="MA 20" value={formatCurrency(movingAverages.ma_20, overview.currency)} hint={INDICATOR_COPY.ma} />
                      <IndicatorCard label="MA 50" value={formatCurrency(movingAverages.ma_50, overview.currency)} hint={INDICATOR_COPY.ma} />
                      <IndicatorCard label="EMA 20" value={formatCurrency(movingAverages.ema_20, overview.currency)} hint={INDICATOR_COPY.ema} />
                      <IndicatorCard label="EMA 50" value={formatCurrency(movingAverages.ema_50, overview.currency)} hint={INDICATOR_COPY.ema} />
                      <IndicatorCard label="RSI" value={formatPercent(technical.rsi)} accent={technical.rsi >= 70 ? 'text-rose-300' : technical.rsi <= 30 ? 'text-emerald-300' : 'text-amber-300'} hint={INDICATOR_COPY.rsi} />
                      <IndicatorCard label="MACD Histogram" value={Number(technical.macd?.histogram ?? 0).toFixed(4)} accent={technical.macd?.histogram < 0 ? 'text-rose-300' : 'text-emerald-300'} hint={INDICATOR_COPY.macd} />
                      <IndicatorCard label="Support" value={formatCurrency(technical.support, overview.currency)} hint={INDICATOR_COPY.sr} />
                      <IndicatorCard label="Resistance" value={formatCurrency(technical.resistance, overview.currency)} hint={INDICATOR_COPY.sr} />
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-3">
                      <div className="rounded-[1.4rem] border border-slate-800/70 bg-slate-900/60 p-4">
                        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">Trend</p>
                        <p className={`mt-3 text-lg font-black ${performanceState.tone}`}>{technical.trend || performanceState.label}</p>
                        <p className="mt-2 text-xs text-slate-400">EMA structure + momentum + RSI blend</p>
                      </div>
                      <div className="rounded-[1.4rem] border border-slate-800/70 bg-slate-900/60 p-4">
                        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">Volatility</p>
                        <p className="mt-3 text-lg font-black text-white">{formatPercent(technical.volatility_pct)}</p>
                        <p className="mt-2 text-xs text-slate-400">Higher volatility means wider swings</p>
                      </div>
                      <div className="rounded-[1.4rem] border border-slate-800/70 bg-slate-900/60 p-4">
                        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">Last Close</p>
                        <p className="mt-3 text-lg font-black text-white">{formatCurrency(latestBar.close || overview.current_price, overview.currency)}</p>
                        <p className="mt-2 text-xs text-slate-400">Latest sampled point in the selected range</p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/60 p-6">
                    <SectionTitle
                      eyebrow="News & Sentiment"
                      title="Latest headlines and mood"
                      description="The panel shows recent market headlines and a lightweight sentiment read based on headline language."
                      icon={FiMessageSquare}
                    />

                    <div className="grid gap-4 md:grid-cols-3">
                      <MetricCard label="Overall sentiment" value={sentiment.overall || 'Neutral'} tone={badgeTone(sentiment.overall)} detail={sentiment.summary || 'No recent headlines were available from the market feed.'} />
                      <MetricCard label="Positive" value={sentiment.positive ?? 0} tone="text-emerald-300" />
                      <MetricCard label="Negative" value={sentiment.negative ?? 0} tone="text-rose-300" />
                    </div>

                    <div className="mt-4 space-y-3">
                      {newsItems.length > 0 ? (
                        newsItems.map((item, index) => <NewsCard key={`${item.headline}-${index}`} item={item} />)
                      ) : (
                        <div className="rounded-[1.4rem] border border-slate-800/70 bg-slate-900/60 p-5 text-sm text-slate-400">
                          No recent headlines were available for this symbol.
                        </div>
                      )}
                    </div>
                  </div>
                </section>

                <section className="rounded-[2rem] border border-slate-800/70 bg-slate-950/60 p-6">
                  <SectionTitle
                    eyebrow="Quick Summary"
                    title="What the panel is telling you"
                    description="A compact takeaway for users who want the key points without reading every indicator."
                    icon={FiFileText}
                  />
                  <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                    <InsightChip label="Symbol" value={overview.symbol || selectedSymbol} tone="bg-slate-800 text-slate-200 border-slate-700" />
                    <InsightChip label="Range" value={panel?.range_label || rangeKey.toUpperCase()} tone="bg-slate-800 text-slate-200 border-slate-700" />
                    <InsightChip label="Confidence" value={formatPercent(prediction.confidence_pct)} tone={badgeTone(confidenceLabel)} />
                    <InsightChip label="Risk" value={riskLevel} tone={badgeTone(riskLevel)} />
                  </div>
                  <div className="mt-5 flex flex-wrap gap-3">
                    <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-300">
                      <FiTrendingUp className="text-emerald-300" size={16} />
                      Bullish: Green tones and positive labels
                    </div>
                    <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-300">
                      <FiTrendingDown className="text-rose-300" size={16} />
                      Bearish: Red tones and downside pressure
                    </div>
                    <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-300">
                      <FiClock className="text-amber-300" size={16} />
                      Neutral: Wait for better confirmation
                    </div>
                    <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-300">
                      <FiLayers className="text-blue-300" size={16} />
                      Indicators, sentiment, and AI blended together
                    </div>
                  </div>
                  <div className="mt-5 rounded-[1.4rem] border border-blue-500/20 bg-blue-500/5 p-5 text-sm leading-7 text-slate-300">
                    This panel is built to support investor and analyst workflows together. Use the chart for structure, the indicators for timing, and the recommendation only as a decision aid alongside your own research.
                  </div>
                </section>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analysis
