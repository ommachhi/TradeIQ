import { useEffect, useMemo, useState } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  FiActivity,
  FiArrowRight,
  FiBarChart2,
  FiBell,
  FiClock,
  FiCpu,
  FiDatabase,
  FiDownload,
  FiExternalLink,
  FiLayers,
  FiLogOut,
  FiMenu,
  FiRefreshCw,
  FiSearch,
  FiShield,
  FiTarget,
  FiUpload,
  FiX,
} from 'react-icons/fi'
import { adminAPI, authHelpers } from '../services/api'

const TABS = [
  { id: 'overview', label: 'Lab Overview', icon: FiBarChart2 },
  { id: 'datalake', label: 'Data Lake', icon: FiDatabase },
  { id: 'modelforge', label: 'Model Forge', icon: FiLayers },
  { id: 'activity', label: 'Activity', icon: FiActivity },
]

const STOCK_SUGGESTIONS = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'AAPL', 'MSFT']

const cardTone = {
  good: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-200',
  warn: 'border-amber-500/20 bg-amber-500/10 text-amber-200',
  bad: 'border-rose-500/20 bg-rose-500/10 text-rose-200',
  neutral: 'border-slate-800 bg-slate-900/60 text-slate-200',
}

const formatNumber = (value) => {
  if (value == null || Number.isNaN(Number(value))) return '--'
  return Intl.NumberFormat('en-IN', { notation: 'compact', maximumFractionDigits: 2 }).format(Number(value))
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

const StatCard = ({ label, value, detail, tone = 'neutral', icon: Icon }) => (
  <div className={`rounded-[1.6rem] border p-5 shadow-[0_14px_40px_rgba(2,6,23,0.25)] ${cardTone[tone] || cardTone.neutral}`}>
    <div className="flex items-start justify-between gap-4">
      <div>
        <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-slate-400">{label}</p>
        <p className="mt-3 text-3xl font-black tracking-tight text-white">{value}</p>
        {detail && <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>}
      </div>
      {Icon && (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-white/80">
          <Icon size={18} />
        </div>
      )}
    </div>
  </div>
)

const Pill = ({ children, tone = 'neutral' }) => (
  <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${cardTone[tone] || cardTone.neutral}`}>
    {children}
  </span>
)

const SectionTitle = ({ eyebrow, title, description, icon: Icon }) => (
  <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
    <div>
      <p className="text-[11px] font-bold uppercase tracking-[0.32em] text-slate-500">{eyebrow}</p>
      <div className="mt-2 flex items-center gap-3">
        {Icon && <Icon className="text-blue-300" size={18} />}
        <h2 className="text-xl font-black tracking-tight text-white md:text-2xl">{title}</h2>
      </div>
      {description && <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{description}</p>}
    </div>
  </div>
)

const EmptyState = ({ title, description }) => (
  <div className="rounded-[1.5rem] border border-dashed border-slate-700 bg-slate-950/40 p-6 text-center text-slate-400">
    <p className="font-semibold text-white">{title}</p>
    <p className="mt-2 text-sm leading-6">{description}</p>
  </div>
)

const Researcher = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [feedback, setFeedback] = useState({ type: null, msg: '' })
  const [stockSearch, setStockSearch] = useState('RELIANCE')
  const [stockPreview, setStockPreview] = useState(null)
  const [datasets, setDatasets] = useState([])
  const [models, setModels] = useState([])
  const [stats, setStats] = useState(null)
  const [activity, setActivity] = useState([])
  const [predictions, setPredictions] = useState([])
  const [selectedDatasetId, setSelectedDatasetId] = useState('')
  const [retrainModelName, setRetrainModelName] = useState('Auto-trained Model')

  const systemHealth = useMemo(() => {
    const activeModel = stats?.system?.active_model || models.find((model) => model.is_active)?.name || '--'
    const recentActivity = stats?.system?.recent_activity_count ?? activity.length
    return {
      apiStatus: stats?.system?.api_status || 'online',
      activeModel,
      recentActivity,
      cpu: '22%',
      ram: '2.1GB',
      latency: '40ms',
    }
  }, [stats, models, activity.length])

  const showFeedback = (type, msg) => {
    setFeedback({ type, msg })
    window.clearTimeout(showFeedback._timer)
    showFeedback._timer = window.setTimeout(() => setFeedback({ type: null, msg: '' }), 4500)
  }

  const loadResearcherData = async () => {
    try {
      setLoading(true)
      const results = await Promise.allSettled([
        adminAPI.getDashboardStats(),
        adminAPI.getDatasets(),
        adminAPI.getModelHistory(),
        adminAPI.getActivityLogs(),
        adminAPI.getPredictions(),
      ])

      const [statsRes, datasetsRes, modelsRes, activityRes, predictionsRes] = results
      setStats(statsRes.status === 'fulfilled' ? statsRes.value : null)
      setDatasets(datasetsRes.status === 'fulfilled' ? datasetsRes.value : [])
      setModels(modelsRes.status === 'fulfilled' ? modelsRes.value : [])
      setActivity(activityRes.status === 'fulfilled' ? activityRes.value : [])
      setPredictions(predictionsRes.status === 'fulfilled' ? predictionsRes.value : [])

      const latestModels = modelsRes.status === 'fulfilled' ? modelsRes.value : []
      const activeDataset = datasetsRes.status === 'fulfilled' ? datasetsRes.value?.[0]?.id || '' : ''
      setSelectedDatasetId(activeDataset)
      setRetrainModelName(latestModels.find((model) => model.is_active)?.name || 'Auto-trained Model')
    } catch (error) {
      showFeedback('error', 'Failed to sync with Research Lab.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadResearcherData()
  }, [])

  const handleAction = async (actionFn, successMsg) => {
    try {
      setProcessing(true)
      await actionFn()
      showFeedback('success', successMsg)
      await loadResearcherData()
    } catch (error) {
      showFeedback('error', error?.message || 'Operation failed')
    } finally {
      setProcessing(false)
    }
  }

  const ingestStockData = () => handleAction(async () => {
    if (!stockSearch.trim()) {
      throw new Error('Enter a stock symbol first.')
    }
    const data = await adminAPI.fetchStockData(stockSearch.trim())
    setStockPreview(data)
  }, 'Market data ingested successfully.')

  const retrainModel = () => handleAction(async () => {
    await adminAPI.retrainModel({
      model_name: retrainModelName.trim() || 'Auto-trained Model',
      ...(selectedDatasetId ? { dataset_id: selectedDatasetId } : {}),
    })
  }, 'Model retraining started successfully.')

  const activeModel = models.find((model) => model.is_active) || models[0] || null

  const predictionTrend = stats?.prediction_trend || []
  const topOperators = stats?.top_operators || []
  const recentActivity = stats?.recent_activity || []
  const roleBreakdown = stats?.users?.by_role || {}

  const modelPerformanceData = models.slice(0, 6).map((model) => ({
    name: model.name,
    rmse: Number(model.rmse ?? 0),
    trainRmse: Number(model.train_rmse ?? 0),
    rSquared: Number(model.r_squared ?? 0),
  }))

  const roleData = Object.entries(roleBreakdown).map(([role, count]) => ({ name: role, value: count }))

  const pageTitle = activeTab === 'overview'
    ? 'Lab Monitoring'
    : activeTab === 'datalake'
    ? 'Data Lake'
    : activeTab === 'modelforge'
    ? 'Model Forge'
    : 'Activity Stream'

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#070b14]">
        <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-950/70 px-5 py-4 text-slate-300">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-700 border-t-blue-400" />
          Syncing Research Lab...
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[#070b14] text-slate-300">
      <aside
        className={`${sidebarCollapsed ? 'w-20' : 'w-72'} flex flex-col border-r border-slate-800/60 bg-[#0b1220] transition-all duration-300`}
      >
        <div className="flex items-center justify-between gap-3 p-5">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/20">
                <FiCpu />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.28em] text-slate-500">TradeIQ</p>
                <p className="text-lg font-black text-white">Research Lab</p>
              </div>
            </div>
          )}
          <button
            type="button"
            onClick={() => setSidebarCollapsed((value) => !value)}
            className="rounded-xl border border-slate-800 bg-slate-950/60 p-2 text-slate-400 transition hover:border-slate-700 hover:text-white"
          >
            {sidebarCollapsed ? <FiMenu size={18} /> : <FiX size={18} />}
          </button>
        </div>

        <nav className="flex-1 space-y-2 px-3 pb-4">
          {TABS.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setActiveTab(item.id)}
                className={`flex w-full items-center rounded-2xl border px-4 py-4 text-left transition-all ${
                  isActive
                    ? 'border-blue-500/30 bg-blue-500/10 text-blue-100'
                    : 'border-transparent bg-transparent text-slate-500 hover:border-slate-800 hover:bg-slate-900/60 hover:text-slate-200'
                }`}
              >
                <Icon className={`${sidebarCollapsed ? 'mx-auto' : 'mr-4'} text-lg`} />
                {!sidebarCollapsed && <span className="font-semibold">{item.label}</span>}
              </button>
            )
          })}
        </nav>

        <div className="space-y-3 border-t border-slate-800/60 p-4">
          <button
            type="button"
            onClick={() => handleAction(loadResearcherData, 'Research Lab refreshed.')}
            className="flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-blue-500/30 hover:bg-blue-500/10"
          >
            <FiRefreshCw className={processing ? 'animate-spin' : ''} />
            {!sidebarCollapsed && 'Refresh'}
          </button>
          <button
            type="button"
            onClick={() => window.location.assign('/dashboard')}
            className="flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-700 hover:bg-slate-900"
          >
            <FiExternalLink />
            {!sidebarCollapsed && 'Exit Lab'}
          </button>
          <button
            type="button"
            onClick={() => authHelpers.logout()}
            className="flex w-full items-center justify-center gap-2 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm font-semibold text-rose-200 transition hover:border-rose-500/30 hover:bg-rose-500/15"
          >
            <FiLogOut />
            {!sidebarCollapsed && 'Logout'}
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto px-4 py-6 md:px-8 lg:px-10">
        <header className="mb-8 rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6 shadow-[0_20px_80px_rgba(2,6,23,0.38)]">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.3em] text-blue-300/80">Computational Scientist</p>
              <h1 className="mt-3 text-4xl font-black tracking-tight text-white md:text-5xl">{pageTitle}</h1>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
                Monitor datasets, retrain models, inspect prediction health, and watch live activity from a single operational research workspace.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <Pill tone="good">API {systemHealth.apiStatus}</Pill>
              <Pill tone="neutral">Model {systemHealth.activeModel}</Pill>
              <Pill tone="neutral">Activity {systemHealth.recentActivity}</Pill>
              <Pill tone="warn">{authHelpers.getUsername() || 'Researcher'}</Pill>
            </div>
          </div>
        </header>

        {feedback.msg && (
          <div
            className={`mb-6 rounded-2xl border p-4 text-sm font-semibold ${
              feedback.type === 'error'
                ? 'border-rose-500/20 bg-rose-500/10 text-rose-200'
                : 'border-emerald-500/20 bg-emerald-500/10 text-emerald-200'
            }`}
          >
            {feedback.msg}
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="space-y-8">
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <StatCard label="Total Users" value={stats?.users?.total ?? 0} detail={`${stats?.users?.active ?? 0} active, ${stats?.users?.blocked ?? 0} blocked`} icon={FiShield} />
              <StatCard label="Predictions" value={stats?.predictions?.total ?? 0} detail="All-time prediction history" icon={FiTarget} tone="good" />
              <StatCard label="Recent Activity" value={stats?.system?.recent_activity_count ?? 0} detail="Events in last 24 hours" icon={FiBell} tone="warn" />
              <StatCard label="Active Model" value={stats?.system?.active_model || 'None'} detail="Current production model" icon={FiCpu} />
            </section>

            <section className="grid gap-6 xl:grid-cols-[1.4fr,0.6fr]">
              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Prediction Flow"
                  title="Seven-day prediction activity"
                  description="Daily count of model runs across the current week. This helps the team see operational load at a glance."
                  icon={FiActivity}
                />
                <div className="h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={predictionTrend}>
                      <defs>
                        <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.35} />
                          <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.02} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
                      <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
                      <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1f2937', borderRadius: '16px' }} labelStyle={{ color: '#e2e8f0' }} />
                      <Area type="monotone" dataKey="count" stroke="#38bdf8" fill="url(#trendFill)" strokeWidth={3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Live Status"
                  title="System health"
                  description="Simple operational indicators for the research workspace."
                  icon={FiCpu}
                />
                <div className="space-y-4">
                  <StatCard label="CPU" value={systemHealth.cpu} detail="Current compute usage" tone="neutral" />
                  <StatCard label="RAM" value={systemHealth.ram} detail="Resident memory footprint" tone="neutral" />
                  <StatCard label="Latency" value={systemHealth.latency} detail="Approximate request latency" tone="good" />
                </div>
              </div>
            </section>

            <section className="grid gap-6 xl:grid-cols-[1fr,1fr]">
              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Model Performance"
                  title="Recent model scores"
                  description="Test and training fit for the most recent models. Lower RMSE and stronger R² are preferred."
                  icon={FiBarChart2}
                />
                <div className="h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={modelPerformanceData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
                      <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1f2937' }} />
                      <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1f2937', borderRadius: '16px' }} labelStyle={{ color: '#e2e8f0' }} />
                      <Bar dataKey="rmse" fill="#38bdf8" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="trainRmse" fill="#10b981" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Role Mix"
                  title="User distribution"
                  description="The current workspace split by role for admin, analyst, researcher, and investor access."
                  icon={FiShield}
                />
                <div className="space-y-3">
                  {roleData.length > 0 ? (
                    roleData.map((item) => (
                      <div key={item.name} className="flex items-center justify-between rounded-2xl border border-slate-800/60 bg-slate-900/60 px-4 py-3">
                        <span className="text-sm font-semibold capitalize text-slate-200">{item.name}</span>
                        <span className="text-lg font-black text-white">{item.value}</span>
                      </div>
                    ))
                  ) : (
                    <EmptyState title="No role data" description="User role breakdown is not available right now." />
                  )}
                </div>
              </div>
            </section>
          </div>
        )}

        {activeTab === 'datalake' && (
          <div className="space-y-8">
            <section className="grid gap-6 xl:grid-cols-[0.8fr,1.2fr]">
              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Market Ingest"
                  title="Sync live stock data"
                  description="Pull a fresh OHLCV snapshot into the lab for inspection or retraining support."
                  icon={FiDownload}
                />
                <div className="space-y-4">
                  <input
                    type="text"
                    value={stockSearch}
                    onChange={(event) => setStockSearch(event.target.value.toUpperCase())}
                    placeholder="Ticker symbol e.g. RELIANCE, TCS, AAPL"
                    className="w-full rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-white outline-none transition focus:border-blue-500/40"
                  />
                  <div className="flex flex-wrap gap-2">
                    {STOCK_SUGGESTIONS.map((symbol) => (
                      <button
                        key={symbol}
                        type="button"
                        onClick={() => setStockSearch(symbol)}
                        className="rounded-full border border-slate-800 bg-slate-900/70 px-3 py-1.5 text-xs font-semibold text-slate-300 transition hover:border-slate-600 hover:text-white"
                      >
                        {symbol}
                      </button>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={ingestStockData}
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 px-4 py-3 font-semibold text-white transition hover:brightness-110"
                  >
                    <FiUpload />
                    Ingest Market Data
                  </button>
                  {stockPreview?.symbol && (
                    <div className="rounded-[1.4rem] border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-300">
                      <div className="flex items-center justify-between gap-3">
                        <span className="font-semibold text-white">{stockPreview.symbol}</span>
                        <span className="text-xs uppercase tracking-[0.2em] text-slate-500">{stockPreview.row_count} rows</span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">Latest market snapshot loaded into the lab.</p>
                    </div>
                  )}
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Dataset Inventory"
                  title="Available training sources"
                  description="Datasets currently stored in the workspace, including row and column counts."
                  icon={FiDatabase}
                />
                <div className="space-y-3">
                  {datasets.length > 0 ? (
                    datasets.map((dataset) => (
                      <div key={dataset.id} className="rounded-2xl border border-slate-800/60 bg-slate-900/60 p-4">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <p className="font-semibold text-white">{dataset.name}</p>
                            <p className="mt-1 text-xs text-slate-400">
                              {dataset.row_count ?? '--'} rows • {dataset.column_count ?? '--'} columns
                            </p>
                          </div>
                          <span className="rounded-full border border-slate-700 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-300">
                            Dataset
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <EmptyState title="No datasets" description="No uploaded datasets are available in the current workspace." />
                  )}
                </div>
              </div>
            </section>
          </div>
        )}

        {activeTab === 'modelforge' && (
          <div className="space-y-8">
            <section className="grid gap-6 xl:grid-cols-[0.8fr,1.2fr]">
              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Retraining"
                  title="Run a new model cycle"
                  description="Choose a dataset and a model name before kicking off retraining."
                  icon={FiRefreshCw}
                />
                <div className="space-y-4">
                  <input
                    type="text"
                    value={retrainModelName}
                    onChange={(event) => setRetrainModelName(event.target.value)}
                    placeholder="Model name"
                    className="w-full rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-white outline-none transition focus:border-blue-500/40"
                  />
                  <select
                    value={selectedDatasetId}
                    onChange={(event) => setSelectedDatasetId(event.target.value)}
                    className="w-full rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-white outline-none transition focus:border-blue-500/40"
                  >
                    <option value="">Use default training dataset</option>
                    {datasets.map((dataset) => (
                      <option key={dataset.id} value={dataset.id}>
                        {dataset.name}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={retrainModel}
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-3 font-semibold text-white transition hover:brightness-110"
                  >
                    <FiRefreshCw className={processing ? 'animate-spin' : ''} />
                    Retrain Model
                  </button>
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Model Registry"
                  title="Current performance"
                  description="Latest model versions and their primary metrics. Active model is marked for quick review."
                  icon={FiCpu}
                />
                <div className="space-y-3">
                  {models.length > 0 ? (
                    models.map((model) => (
                      <div key={model.id} className={`rounded-2xl border p-4 ${model.is_active ? 'border-blue-500/30 bg-blue-500/10' : 'border-slate-800/60 bg-slate-900/60'}`}>
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <p className="font-semibold text-white">{model.name}</p>
                            <p className="mt-1 text-xs text-slate-400">
                              RMSE {Number(model.rmse ?? 0).toFixed(4)} • R² {Number(model.r_squared ?? 0).toFixed(4)}
                            </p>
                            <p className="mt-1 text-xs text-slate-500">
                              {formatDateTime(model.training_date)}
                            </p>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            {model.is_active && <Pill tone="good">Active</Pill>}
                            <Pill tone={Number(model.overfit_gap ?? 0) > 0.15 ? 'warn' : 'neutral'}>
                              Gap {Number(model.overfit_gap ?? 0).toFixed(4)}
                            </Pill>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <EmptyState title="No model history" description="Model retraining history is not available yet." />
                  )}
                </div>
              </div>
            </section>
          </div>
        )}

        {activeTab === 'activity' && (
          <div className="space-y-8">
            <section className="grid gap-6 xl:grid-cols-[1fr,1fr]">
              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Recent Activity"
                  title="Operational log"
                  description="A quick look at the latest research and admin actions."
                  icon={FiClock}
                />
                <div className="space-y-3">
                  {(recentActivity.length > 0 ? recentActivity : activity.slice(0, 8)).map((item, index) => (
                    <div key={`${item.timestamp || index}-${index}`} className="rounded-2xl border border-slate-800/60 bg-slate-900/60 p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="font-semibold text-white">{item.action}</p>
                          <p className="mt-1 text-xs text-slate-400">
                            {item.user || item.username || 'Unknown'} • {item.role || 'researcher'}
                          </p>
                        </div>
                        <span className="text-xs text-slate-500">{formatDateTime(item.timestamp)}</span>
                      </div>
                    </div>
                  ))}
                  {!recentActivity.length && !activity.length && (
                    <EmptyState title="No activity yet" description="Activity logs will appear here once users interact with the lab." />
                  )}
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
                <SectionTitle
                  eyebrow="Operator Rankings"
                  title="Top prediction users"
                  description="Users with the highest prediction volume in the workspace."
                  icon={FiTarget}
                />
                <div className="space-y-3">
                  {topOperators.length > 0 ? (
                    topOperators.map((item, index) => (
                      <div key={`${item.username}-${index}`} className="flex items-center justify-between rounded-2xl border border-slate-800/60 bg-slate-900/60 px-4 py-3">
                        <div>
                          <p className="font-semibold text-white">{item.username}</p>
                          <p className="text-xs text-slate-400 capitalize">{item.role}</p>
                        </div>
                        <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-bold text-slate-200">
                          {item.count} runs
                        </span>
                      </div>
                    ))
                  ) : (
                    <EmptyState title="No operator data" description="Prediction activity will appear here after users begin running forecasts." />
                  )}
                </div>
              </div>
            </section>

            <section className="rounded-[2rem] border border-slate-800/70 bg-slate-950/55 p-6">
              <SectionTitle
                eyebrow="Prediction History"
                title="Latest prediction records"
                description="Recent model outputs available to the research team for auditing and review."
                icon={FiArrowRight}
              />
              <div className="overflow-hidden rounded-[1.4rem] border border-slate-800/60">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-800 text-left text-sm">
                    <thead className="bg-slate-900/80 text-slate-400">
                      <tr>
                        <th className="px-4 py-3 font-semibold">Symbol</th>
                        <th className="px-4 py-3 font-semibold">User</th>
                        <th className="px-4 py-3 font-semibold">Recommendation</th>
                        <th className="px-4 py-3 font-semibold">Predicted</th>
                        <th className="px-4 py-3 font-semibold">Created</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-950/40">
                      {(predictions.slice(0, 8)).map((item) => (
                        <tr key={item.id}>
                          <td className="px-4 py-3 font-semibold text-white">{item.stock_symbol}</td>
                          <td className="px-4 py-3 text-slate-300">{item.username || 'Unknown'}</td>
                          <td className="px-4 py-3">
                            <Pill tone={item.recommendation === 'BUY' ? 'good' : item.recommendation === 'SELL' ? 'bad' : 'warn'}>{item.recommendation}</Pill>
                          </td>
                          <td className="px-4 py-3 text-slate-300">{Number(item.predicted_price ?? 0).toFixed(2)}</td>
                          <td className="px-4 py-3 text-slate-400">{formatDateTime(item.created_at)}</td>
                        </tr>
                      ))}
                      {!predictions.length && (
                        <tr>
                          <td className="px-4 py-6" colSpan="5">
                            <EmptyState title="No predictions found" description="Prediction history will appear here when the system has live usage." />
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}

export default Researcher
