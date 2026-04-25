import React, { useEffect, useMemo, useState } from 'react'
import { adminAPI, authAPI, authHelpers } from '../services/api'
import {
  FiActivity,
  FiAlertCircle,
  FiCheckCircle,
  FiClock,
  FiCpu,
  FiDatabase,
  FiGlobe,
  FiLayers,
  FiLock,
  FiLogOut,
  FiMenu,
  FiPieChart,
  FiSearch,
  FiShield,
  FiTarget,
  FiTrash2,
  FiTrendingUp,
  FiUnlock,
  FiUsers,
  FiX,
} from 'react-icons/fi'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const NAV = [
  ['overview', 'Dashboard', FiPieChart],
  ['users', 'User Management', FiUsers],
  ['datalake', 'Stock Data', FiDatabase],
  ['modelforge', 'ML Control', FiCpu],
  ['inference', 'Prediction Logs', FiLayers],
  ['compliance', 'Activity Logs', FiShield],
]

const TITLES = {
  overview: ['Sovereign Operations', 'Admin Dashboard'],
  users: ['User Management', 'User Management'],
  datalake: ['Stock Data', 'Stock Data Records'],
  modelforge: ['ML Control', 'Model Forge'],
  inference: ['Prediction Logs', 'Prediction Audit Logs'],
  compliance: ['Activity Logs', 'System Compliance Logs'],
}

const fmtDate = (v) => {
  if (!v) return 'Not available'
  try {
    return new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(v))
  } catch {
    return v
  }
}

const fmtNum = (v, d = 2) =>
  v == null || Number.isNaN(Number(v))
    ? '--'
    : Number(v).toLocaleString('en-IN', { minimumFractionDigits: d, maximumFractionDigits: d })
const fmtInt = (v) => (v == null || Number.isNaN(Number(v)) ? '--' : Number(v).toLocaleString('en-IN'))
const fmtScore = (v) => (v == null || Number.isNaN(Number(v)) ? '--' : Number(v).toFixed(3))
const hasMetric = (v) => v != null && !Number.isNaN(Number(v))
const roleLabel = (v) => ({ admin: 'Admin', analyst: 'Analyst', researcher: 'Researcher', investor: 'Investor' }[v] || 'Investor')
const userLabel = (u) => `${u?.first_name || ''} ${u?.last_name || ''}`.trim() || u?.username || 'Unknown User'

const EmptyState = ({ title, text }) => (
  <div className="flex min-h-[220px] items-center justify-center rounded-[1.75rem] border border-dashed border-slate-700/70 bg-slate-900/30 px-8 text-center">
    <div>
      <p className="text-lg font-bold text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{text}</p>
    </div>
  </div>
)

const Metric = ({ label, value, note, Icon, tone }) => {
  const styles = {
    blue: ['border-l-blue-500', 'bg-blue-500/10', 'text-blue-400'],
    purple: ['border-l-purple-500', 'bg-purple-500/10', 'text-purple-400'],
    emerald: ['border-l-emerald-500', 'bg-emerald-500/10', 'text-emerald-400'],
    amber: ['border-l-amber-500', 'bg-amber-500/10', 'text-amber-400'],
  }[tone]

  return (
    <div className={`rounded-[1.75rem] border border-slate-800/80 border-l-4 ${styles[0]} bg-[#0c1220]/80 p-6`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-black uppercase tracking-[0.22em] text-slate-500">{label}</p>
          <p className="text-3xl font-black text-white">{value}</p>
          <p className="mt-3 text-xs text-slate-400">{note}</p>
        </div>
        <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${styles[1]} ${styles[2]}`}>
          <Icon size={22} />
        </div>
      </div>
    </div>
  )
}

const ProfileModal = ({ user, onClose }) =>
  !user ? null : (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/75 px-4 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-[2rem] border border-slate-800 bg-[#0c1220] p-8 shadow-2xl shadow-black/40">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-purple-700 text-2xl font-black text-white">
              {(user.username || 'U').charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-[0.22em] text-slate-500">Profile Details</p>
              <h3 className="mt-2 text-2xl font-black text-white">{userLabel(user)}</h3>
              <p className="text-sm text-slate-400">@{user.username || 'unknown'}</p>
            </div>
          </div>
          <button onClick={onClose} className="rounded-xl border border-slate-700 p-2 text-slate-400 transition-colors hover:border-slate-500 hover:text-white">
            <FiX size={20} />
          </button>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5"><p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Username</p><p className="mt-2 text-lg font-bold text-white">{user.username || '--'}</p></div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5"><p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Email</p><p className="mt-2 break-all text-lg font-bold text-white">{user.email || 'Not added'}</p></div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5"><p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Role</p><p className="mt-2 text-lg font-bold text-white">{roleLabel(user.role)}</p></div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5"><p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Status</p><p className={`mt-2 text-lg font-bold ${user.is_active ? 'text-emerald-400' : 'text-red-400'}`}>{user.is_active ? 'Active' : 'Blocked'}</p></div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 md:col-span-2"><p className="text-xs font-black uppercase tracking-[0.18em] text-slate-500">Joined On</p><p className="mt-2 text-lg font-bold text-white">{fmtDate(user.date_joined)}</p></div>
        </div>
      </div>
    </div>
  )

const TradeIQAdmin = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const [collapsed, setCollapsed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [data, setData] = useState({ stats: null, users: [], datasets: [], models: [], logs: [], predictions: [] })
  const [feedback, setFeedback] = useState({ type: '', msg: '' })
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [stockSearch, setStockSearch] = useState('')
  const [stockPreview, setStockPreview] = useState(null)
  const [latencyMs, setLatencyMs] = useState(null)

  const q = searchTerm.trim().toLowerCase()
  const [title, heading] = TITLES[activeTab] || TITLES.overview

  const showFeedback = (type, msg) => {
    setFeedback({ type, msg })
    window.setTimeout(() => setFeedback({ type: '', msg: '' }), 5000)
  }

  const refresh = async () => {
    try {
      setLoading(true)
      const started = performance.now()
      const [statsRes, usersRes, datasetsRes, modelsRes, logsRes, predictionsRes, profileRes] = await Promise.allSettled([
        adminAPI.getDashboardStats(),
        adminAPI.getUsers(),
        adminAPI.getDatasets(),
        adminAPI.getModelHistory(),
        adminAPI.getActivityLogs(),
        adminAPI.getPredictions(),
        authAPI.getProfile(),
      ])
      setLatencyMs(Math.max(1, Math.round(performance.now() - started)))
      setData({
        stats: statsRes.status === 'fulfilled' ? statsRes.value : null,
        users: usersRes.status === 'fulfilled' ? usersRes.value : [],
        datasets: datasetsRes.status === 'fulfilled' ? datasetsRes.value : [],
        models: modelsRes.status === 'fulfilled' ? modelsRes.value : [],
        logs: logsRes.status === 'fulfilled' ? logsRes.value : [],
        predictions: predictionsRes.status === 'fulfilled' ? predictionsRes.value : [],
      })
      if (profileRes.status === 'fulfilled') {
        setProfile(profileRes.value)
        authHelpers.setAuthData(authHelpers.getToken(), profileRes.value.role || authHelpers.getUserRole(), profileRes.value.username || authHelpers.getUsername())
      }
    } catch (err) {
      console.error(err)
      showFeedback('error', 'Admin data load nahi ho paaya. Thoda refresh karke dobara try karo.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  const runAction = async (fn, successMsg) => {
    try {
      setProcessing(true)
      await fn()
      showFeedback('success', successMsg)
      await refresh()
    } catch (err) {
      showFeedback('error', err.response?.data?.error || err.response?.data?.detail || err.message || 'Operation failed')
    } finally {
      setProcessing(false)
    }
  }

  const retrainModel = async () => {
    try {
      setProcessing(true)
      const res = await adminAPI.retrainModel({ model_name: 'TradeIQ_RF_v2' })
      const m = res?.metrics || {}
      showFeedback('success', `Retrain complete. Test R2 ${fmtScore(m.r_squared)}, RMSE ${fmtNum(m.rmse)}, gap ${fmtScore(m.overfit_gap)}`)
      await refresh()
    } catch (err) {
      showFeedback('error', err.response?.data?.error || err.response?.data?.message || 'Model retraining failed')
    } finally {
      setProcessing(false)
    }
  }

  const users = useMemo(() => (!q ? data.users : data.users.filter((u) => [u.username, u.email, u.first_name, u.last_name, u.role, u.is_active ? 'active' : 'blocked'].filter(Boolean).join(' ').toLowerCase().includes(q))), [data.users, q])
  const models = useMemo(() => (!q ? data.models : data.models.filter((m) => [m.name, m.dataset_name, m.is_active ? 'active' : 'archived'].filter(Boolean).join(' ').toLowerCase().includes(q))), [data.models, q])
  const predictions = useMemo(() => (!q ? data.predictions : data.predictions.filter((p) => [p.stock_symbol, p.username, p.recommendation, p.user_role].filter(Boolean).join(' ').toLowerCase().includes(q))), [data.predictions, q])
  const logs = useMemo(() => (!q ? data.logs : data.logs.filter((l) => [l.username, l.user, l.action, l.role].filter(Boolean).join(' ').toLowerCase().includes(q))), [data.logs, q])
  const datasets = useMemo(() => (!q ? data.datasets : data.datasets.filter((d) => [d.name, d.row_count, d.column_count].filter((v) => v != null).join(' ').toLowerCase().includes(q))), [data.datasets, q])
  const previewRows = useMemo(() => (!stockPreview?.data ? [] : !q ? stockPreview.data : stockPreview.data.filter((r) => [r.date, r.close, r.volume].filter((v) => v != null).join(' ').toLowerCase().includes(q))), [stockPreview, q])

  const trendData = useMemo(() => {
    if (Array.isArray(data.stats?.prediction_trend) && data.stats.prediction_trend.length) return data.stats.prediction_trend.map((p) => ({ label: p.date, count: p.count }))
    const buckets = {}
    const today = new Date()
    for (let i = 6; i >= 0; i -= 1) {
      const d = new Date(today)
      d.setDate(today.getDate() - i)
      buckets[d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })] = 0
    }
    data.predictions.forEach((p) => {
      const d = p.created_at ? new Date(p.created_at) : null
      if (!d || Number.isNaN(d.getTime())) return
      const label = d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
      if (label in buckets) buckets[label] += 1
    })
    return Object.entries(buckets).map(([label, count]) => ({ label, count }))
  }, [data.predictions, data.stats])

  const topOperatives = useMemo(() => {
    if (Array.isArray(data.stats?.top_operators) && data.stats.top_operators.length) return data.stats.top_operators
    const counts = {}
    data.predictions.forEach((p) => {
      const key = p.username || 'Unknown'
      counts[key] = counts[key] || { username: key, role: p.user_role || 'investor', count: 0 }
      counts[key].count += 1
    })
    return Object.values(counts).sort((a, b) => b.count - a.count).slice(0, 5)
  }, [data.predictions, data.stats])

  const searchResults = useMemo(() => {
    if (!q) return []
    const results = []
    users.slice(0, 3).forEach((u) => results.push({ id: `u-${u.id}`, type: 'User', title: u.username, subtitle: `${roleLabel(u.role)} | ${u.email || 'No email'}`, click: () => { setActiveTab('users'); setSelectedUser(u) } }))
    models.slice(0, 2).forEach((m) => results.push({ id: `m-${m.id}`, type: 'Model', title: m.name, subtitle: `R2 ${fmtScore(m.r_squared)} | ${m.is_active ? 'Active' : 'Archived'}`, click: () => setActiveTab('modelforge') }))
    predictions.slice(0, 2).forEach((p) => results.push({ id: `p-${p.id}`, type: 'Prediction', title: p.stock_symbol, subtitle: `${p.username || 'Unknown'} | ${p.recommendation}`, click: () => setActiveTab('inference') }))
    logs.slice(0, 2).forEach((l, i) => results.push({ id: `l-${l.id || i}`, type: 'Activity', title: l.username || l.user || 'System', subtitle: l.action, click: () => setActiveTab('compliance') }))
    datasets.slice(0, 2).forEach((d) => results.push({ id: `d-${d.id}`, type: 'Dataset', title: d.name, subtitle: `${fmtInt(d.row_count)} rows | ${fmtInt(d.column_count)} cols`, click: () => setActiveTab('datalake') }))
    if (profile && [profile.username, profile.email, profile.role].filter(Boolean).join(' ').toLowerCase().includes(q)) results.unshift({ id: 'profile', type: 'Profile', title: profile.username, subtitle: `${roleLabel(profile.role)} | current admin`, click: () => setSelectedUser(profile) })
    return results.slice(0, 8)
  }, [datasets, logs, models, predictions, profile, q, users])

  const activeModel = data.models.find((m) => m.is_active) || null
  const latestModel = data.models[0] || null
  const focusModel = activeModel || latestModel
  const hasTrainMetrics = (m) => hasMetric(m?.train_r_squared) && hasMetric(m?.overfit_gap)
  const healthBadge = (m) => {
    if (!m) return ['Unavailable', 'bg-slate-800 text-slate-400']
    if (!hasTrainMetrics(m)) return ['Legacy Metrics', 'bg-amber-500/10 text-amber-400']
    if (Number(m.overfit_gap) > 0.12) return ['Overfit Risk', 'bg-red-500/10 text-red-400']
    if (Number(m.r_squared) < 0.5) return ['Needs Retrain', 'bg-amber-500/10 text-amber-400']
    return ['Stable', 'bg-emerald-500/10 text-emerald-400']
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#070b14]">
        <div className="relative">
          <div className="h-24 w-24 animate-spin rounded-full border-4 border-slate-800 border-t-blue-500"></div>
          <div className="absolute inset-0 flex items-center justify-center text-xs font-black text-blue-500">TIQ</div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#070b14] text-slate-300 selection:bg-blue-500/30">
      <aside className={`${collapsed ? 'w-24' : 'w-72'} z-50 flex flex-col border-r border-slate-800/50 bg-[#0c1220] transition-all duration-500`}>
        <div className="flex items-center justify-between p-8">
          {!collapsed && (
            <button className="group flex items-center gap-3 text-left" onClick={() => setActiveTab('overview')}>
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-transform group-hover:rotate-12"><FiTrendingUp className="text-xl text-white" /></div>
              <div><span className="text-xl font-black tracking-[-0.05em] text-white">INTEL<span className="text-blue-500 underline decoration-blue-500/30 underline-offset-4">CORE</span></span><p className="text-[10px] font-black uppercase tracking-widest text-blue-500/60">Admin v2.6</p></div>
            </button>
          )}
          <button onClick={() => setCollapsed((v) => !v)} className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-800/50">{collapsed ? <FiMenu size={22} /> : <FiX size={22} />}</button>
        </div>
        <nav className="mt-6 flex-1 space-y-2 overflow-y-auto px-4 no-scrollbar">
          {NAV.map(([id, label, Icon]) => (
            <button key={id} onClick={() => setActiveTab(id)} className={`group flex w-full items-center rounded-2xl p-4 transition-all duration-300 ${activeTab === id ? 'border border-blue-500/20 bg-blue-600/10 text-blue-400 shadow-[0_4px_20px_rgba(59,130,246,0.1)]' : 'text-slate-500 hover:bg-slate-800/30 hover:text-slate-100'}`}>
              <Icon className={`text-xl ${collapsed ? 'mx-auto' : 'mr-4'} ${activeTab === id ? 'animate-pulse' : ''}`} />
              {!collapsed && <span className="font-bold tracking-tight">{label}</span>}
              {activeTab === id && !collapsed && <div className="ml-auto h-1.5 w-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,1)]"></div>}
            </button>
          ))}
        </nav>
        <div className="space-y-4 border-t border-slate-800/50 p-6">
          <button onClick={() => { window.location.href = '/dashboard' }} className="flex w-full items-center rounded-2xl border border-transparent p-4 font-bold text-blue-400/70 transition-all hover:border-blue-500/20 hover:bg-blue-500/10 hover:text-blue-400"><FiGlobe className={`${collapsed ? 'mx-auto' : 'mr-4'} text-xl`} />{!collapsed && <span>Return to Site</span>}</button>
          <button onClick={() => authHelpers.logout()} className="flex w-full items-center rounded-2xl p-4 font-bold text-red-400/70 transition-all hover:bg-red-500/10 hover:text-red-400"><FiLogOut className={`${collapsed ? 'mx-auto' : 'mr-4'} text-xl`} />{!collapsed && <span>Terminate Session</span>}</button>
        </div>
      </aside>

      <main className="relative flex-1 overflow-y-auto p-10 custom-scrollbar">
        <header className="sticky top-0 z-40 mb-10 rounded-[2rem] border border-slate-800/30 bg-[#0c1220]/70 p-6 backdrop-blur-xl">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-4xl font-black uppercase tracking-tight text-white">{title}</h1>
              <div className="mt-3 flex flex-wrap items-center gap-3 text-xs font-bold text-slate-500">
                <span className="flex items-center"><FiGlobe className="mr-1 text-green-500" />API: {data.stats?.system?.api_status || 'unknown'}</span>
                <span className="h-1 w-1 rounded-full bg-slate-700"></span>
                <span className="flex items-center"><FiClock className="mr-1" />Last sync: {fmtDate(data.stats?.system?.timestamp)}</span>
              </div>
            </div>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
              <div className="relative">
                <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input type="text" placeholder="Search users, models, predictions, logs..." className="w-full rounded-2xl border border-slate-700/50 bg-slate-900/80 py-3.5 pl-12 pr-6 text-sm font-medium text-white transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/40 sm:w-96" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                {q && (
                  <div className="absolute left-0 right-0 top-[calc(100%+12px)] rounded-[1.5rem] border border-slate-800 bg-[#0c1220] p-3 shadow-2xl shadow-black/40">
                    {searchResults.length ? searchResults.map((r) => (
                      <button key={r.id} onClick={r.click} className="mb-2 flex w-full items-start justify-between rounded-2xl bg-slate-900/60 px-4 py-3 text-left transition-all hover:bg-blue-500/5 last:mb-0">
                        <div><p className="text-sm font-bold text-white">{r.title}</p><p className="mt-1 text-xs text-slate-400">{r.subtitle}</p></div>
                        <span className="rounded-full bg-slate-800 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-blue-300">{r.type}</span>
                      </button>
                    )) : <div className="rounded-2xl border border-dashed border-slate-700/80 px-4 py-6 text-center"><p className="text-sm font-bold text-white">No matching admin records</p><p className="mt-1 text-xs text-slate-400">Try username, symbol, model name, or log action.</p></div>}
                  </div>
                )}
              </div>
              <button onClick={() => setSelectedUser(profile)} className="hidden items-center rounded-full border border-slate-700/50 bg-slate-900/80 p-2 pr-6 text-left transition-all hover:border-blue-500/30 hover:bg-blue-500/5 lg:flex">
                <div className="mr-4 flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-tr from-blue-600 to-purple-800 text-sm font-black text-white shadow-lg ring-2 ring-blue-500/20">{(profile?.username || authHelpers.getUsername() || 'A').charAt(0).toUpperCase()}</div>
                <div><p className="text-xs font-black uppercase leading-none text-white">{profile?.username || authHelpers.getUsername() || 'Admin'}</p><p className="mt-1 text-[10px] font-black uppercase tracking-widest text-blue-500/80">{roleLabel(profile?.role || authHelpers.getUserRole())}</p></div>
              </button>
            </div>
          </div>
        </header>

        {feedback.msg && (
          <div className={`mb-8 flex items-center justify-between rounded-[1.5rem] border p-5 ${feedback.type === 'error' ? 'border-red-500/20 bg-red-500/10 text-red-400' : 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400'}`}>
            <div className="flex items-center">{feedback.type === 'error' ? <FiAlertCircle size={22} className="mr-3" /> : <FiCheckCircle size={22} className="mr-3" />}<span className="font-bold">{feedback.msg}</span></div>
            <button onClick={() => setFeedback({ type: '', msg: '' })} className="text-sm font-semibold hover:opacity-70">Dismiss</button>
          </div>
        )}

        <div className="mb-8"><h2 className="text-3xl font-black tracking-tight text-white">{heading}</h2><p className="mt-2 text-sm text-slate-400">{activeTab === 'overview' ? 'Operational pulse across accounts, predictions, and model activity.' : activeTab === 'modelforge' ? 'Retrain the active forecasting model and review deployment quality.' : activeTab === 'datalake' ? 'Search live market snapshots and review uploaded datasets.' : activeTab === 'users' ? 'Control access, inspect profiles, and respond to account issues.' : activeTab === 'inference' ? 'Track generated predictions with symbols, users, and recommendations.' : 'Review authenticated actions performed across the platform.'}</p></div>

        {activeTab === 'overview' && (
          <div className="space-y-10 animate-fadeInLow">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
              <Metric label="Recent Activity" value={fmtInt(data.stats?.system?.recent_activity_count || 0)} note="Authenticated actions recorded in the last 24 hours." Icon={FiActivity} tone="blue" />
              <Metric label="Active Clients" value={fmtInt(data.stats?.users?.active || 0)} note="Enabled user accounts that can currently access the system." Icon={FiUsers} tone="purple" />
              <Metric label="Signal Throughput" value={fmtInt(data.stats?.predictions?.total || 0)} note="Total prediction entries stored across the platform." Icon={FiTarget} tone="emerald" />
              <Metric label="API Latency" value={latencyMs != null ? `${latencyMs}ms` : '--'} note="Round-trip admin dashboard fetch time from this browser session." Icon={FiGlobe} tone="amber" />
            </div>
            <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
              <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 p-8 xl:col-span-2">
                <div className="mb-8"><h3 className="text-2xl font-black tracking-tight text-white">Intelligence Velocity</h3><p className="text-sm font-medium text-slate-500">Predictions logged over the latest 7-day window.</p></div>
                {trendData.some((p) => p.count > 0) ? (
                  <div className="h-[350px] w-full">
                    <ResponsiveContainer>
                      <AreaChart data={trendData}>
                        <defs><linearGradient id="velocityGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.45} /><stop offset="95%" stopColor="#3b82f6" stopOpacity={0} /></linearGradient></defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis dataKey="label" stroke="#475569" fontSize={11} tickLine={false} axisLine={false} dy={15} />
                        <YAxis stroke="#475569" fontSize={11} tickLine={false} axisLine={false} dx={-10} allowDecimals={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#0c1220', borderRadius: '16px', border: '1px solid #334155' }} />
                        <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={3} fill="url(#velocityGrad)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                ) : <EmptyState title="No prediction activity yet" text="As soon as users start generating predictions, this chart will show the last 7 days of volume." />}
              </div>
              <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 p-8">
                <h3 className="border-b border-slate-800/70 pb-4 text-xl font-black text-white">Top Operatives</h3>
                {topOperatives.length ? <div className="mt-6 space-y-4">{topOperatives.map((u, i) => <button key={`${u.username}-${i}`} onClick={() => setSelectedUser(data.users.find((x) => x.username === u.username) || { username: u.username, role: u.role, is_active: true })} className="flex w-full items-center gap-4 rounded-2xl border border-slate-700/40 bg-slate-800/20 p-4 text-left transition-all hover:border-blue-500/20 hover:bg-blue-500/5"><div className={`flex h-12 w-12 items-center justify-center rounded-2xl text-lg font-black ${i === 0 ? 'bg-yellow-500/10 text-yellow-400' : 'bg-slate-800 text-slate-400'}`}>{i + 1}</div><div className="flex-1"><p className="font-black tracking-tight text-white">{u.username}</p><p className="mt-1 text-[10px] font-black uppercase tracking-[0.22em] text-slate-500">{roleLabel(u.role)} | {fmtInt(u.count)} predictions</p></div></button>)}</div> : <div className="mt-6"><EmptyState title="Top operatives will appear here" text="Once prediction history builds up, the most active users will be ranked automatically." /></div>}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 overflow-hidden animate-fadeInLow">
            <table className="w-full text-left">
              <thead className="bg-[#0c1220]/90"><tr className="border-b border-slate-800 text-[10px] font-black uppercase tracking-[0.22em] text-slate-500"><th className="p-8">Username / ID</th><th>Role</th><th>Status</th><th className="pr-8 text-right">Control</th></tr></thead>
              <tbody className="divide-y divide-slate-800/60">
                {users.length ? users.map((u) => (
                  <tr key={u.id} className="transition-colors hover:bg-slate-800/20">
                    <td className="p-8"><button onClick={() => setSelectedUser(u)} className="flex items-center gap-5 text-left"><div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-700 bg-slate-800 font-black text-white">{u.username[0].toUpperCase()}</div><div><p className="font-black text-white">{u.username}</p><p className="text-xs text-slate-500">{u.email || 'N/A'}</p></div></button></td>
                    <td><span className={`rounded-xl px-3 py-1 text-[10px] font-black uppercase tracking-widest ${u.role === 'admin' ? 'bg-red-500/10 text-red-400' : 'bg-blue-500/10 text-blue-400'}`}>{roleLabel(u.role)}</span></td>
                    <td><div className="flex items-center gap-2"><div className={`h-2 w-2 rounded-full ${u.is_active ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]' : 'bg-red-500'}`}></div><span className={`text-xs font-bold ${u.is_active ? 'text-emerald-400' : 'text-red-400'}`}>{u.is_active ? 'Active' : 'Blocked'}</span></div></td>
                    <td className="pr-8 text-right"><div className="flex justify-end gap-3"><button disabled={processing} onClick={() => runAction(() => adminAPI.updateUser(u.id, { is_active: !u.is_active }), `User ${u.username} is now ${!u.is_active ? 'Active' : 'Blocked'}`)} className={`rounded-xl p-3 transition-all disabled:cursor-not-allowed disabled:opacity-50 ${u.is_active ? 'bg-red-500/10 text-red-400 hover:bg-red-600 hover:text-white' : 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-600 hover:text-white'}`}>{u.is_active ? <FiLock size={18} /> : <FiUnlock size={18} />}</button><button disabled={processing} onClick={() => { if (window.confirm(`Delete user "${u.username}" permanently? This action cannot be undone.`)) runAction(() => adminAPI.deleteUser(u.id), `User ${u.username} deleted permanently`) }} className="rounded-xl bg-red-500/10 p-3 text-red-400 transition-all hover:bg-red-600 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"><FiTrash2 size={18} /></button></div></td>
                  </tr>
                )) : <tr><td colSpan={4} className="p-8"><EmptyState title="No user matches found" text="Try searching by username, email, role, or account status." /></td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'datalake' && (
          <div className="space-y-8 animate-fadeInLow">
            <div className="grid grid-cols-1 gap-8 xl:grid-cols-4">
              <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 p-6 xl:col-span-1">
                <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white">Fetch Live Data</h3>
                <p className="mt-2 text-sm text-slate-500">Search any supported ticker and preview recent market candles.</p>
                <div className="mt-6 space-y-4">
                  <input type="text" placeholder="Ticker e.g. AAPL" className="w-full rounded-xl border border-slate-700 bg-slate-900 p-4 font-bold text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40" value={stockSearch} onChange={(e) => setStockSearch(e.target.value.toUpperCase())} />
                  <button disabled={!stockSearch || processing} onClick={async () => { try { setProcessing(true); const d = await adminAPI.fetchStockData(stockSearch); setStockPreview(d); showFeedback('success', `Live market data synced for ${d.symbol}`) } catch (err) { showFeedback('error', err.response?.data?.error || 'Stock data fetch failed') } finally { setProcessing(false) } }} className="w-full rounded-xl bg-blue-600 py-4 text-xs font-black uppercase tracking-widest text-white transition-all disabled:cursor-not-allowed disabled:opacity-50">Sync Stock Data</button>
                </div>
              </div>
              <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 overflow-hidden xl:col-span-3">
                <div className="border-b border-slate-800 bg-slate-900/50 p-6"><h3 className="text-xl font-black text-white">Data Preview: {stockPreview?.symbol || 'No symbol selected'}</h3></div>
                <div className="max-h-[480px] overflow-y-auto no-scrollbar">
                  {previewRows.length ? (
                    <table className="w-full text-left text-sm">
                      <thead className="sticky top-0 bg-slate-900"><tr className="border-b border-slate-800 text-[10px] font-black uppercase tracking-[0.22em] text-slate-500"><th className="p-4">Date</th><th>Close</th><th>Volume</th></tr></thead>
                      <tbody>{previewRows.map((r, i) => <tr key={`${r.date}-${i}`} className="border-b border-slate-800/20"><td className="p-4 font-mono text-slate-400">{r.date}</td><td className="font-bold text-blue-400">${fmtNum(r.close)}</td><td className="text-slate-400">{fmtInt(r.volume)}</td></tr>)}</tbody>
                    </table>
                  ) : <div className="p-8"><EmptyState title="No stock preview available" text="Use the ticker search on the left. Search text also filters preview rows if data is already loaded." /></div>}
                </div>
              </div>
            </div>
            <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 overflow-hidden">
              <div className="border-b border-slate-800 p-6"><h3 className="text-xl font-black text-white">Dataset Registry</h3><p className="mt-1 text-sm text-slate-500">Uploaded training datasets available to the backend.</p></div>
              {datasets.length ? (
                <table className="w-full text-left">
                  <thead className="bg-slate-900"><tr className="border-b border-slate-800 text-[10px] font-black uppercase tracking-[0.22em] text-slate-500"><th className="p-6">Dataset</th><th>Rows</th><th>Columns</th><th className="pr-6 text-right">Uploaded</th></tr></thead>
                  <tbody className="divide-y divide-slate-800/40">{datasets.map((d) => <tr key={d.id} className="hover:bg-slate-800/20"><td className="p-6 font-bold text-white">{d.name}</td><td className="text-slate-300">{fmtInt(d.row_count)}</td><td className="text-slate-300">{fmtInt(d.column_count)}</td><td className="pr-6 text-right text-slate-500">{fmtDate(d.uploaded_at)}</td></tr>)}</tbody>
                </table>
              ) : <div className="p-8"><EmptyState title="No dataset matches found" text="When datasets are uploaded, they will appear here and can also be searched from the header." /></div>}
            </div>
          </div>
        )}

        {activeTab === 'modelforge' && (
          <div className="space-y-8 animate-fadeInLow">
            <div className="grid grid-cols-1 gap-8 xl:grid-cols-2">
              <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 p-10">
                <div className="flex items-center gap-4"><div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-400"><FiCpu size={26} /></div><div><h3 className="text-2xl font-black text-white">Retrain Active Model</h3><p className="mt-1 text-sm text-slate-500">Chronological split + regularized random forest training pipeline.</p></div></div>
                <p className="mt-8 text-sm italic leading-7 text-slate-400">Retraining now updates the active model bundle, stores train and test metrics, and flags overfit risk using the train-test score gap instead of fake accuracy.</p>
                {focusModel && (
                  <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900/50 p-5">
                    <p className="text-xs font-black uppercase tracking-[0.2em] text-slate-500">{activeModel ? 'Current Active Model' : 'Latest Recorded Model'}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-3">
                      <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-black uppercase tracking-widest text-blue-400">{focusModel.name}</span>
                      <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-black uppercase tracking-widest text-slate-400">Test R2 {fmtScore(focusModel.r_squared)}</span>
                      <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-black uppercase tracking-widest text-slate-400">RMSE {fmtNum(focusModel.rmse)}</span>
                      <span className={`rounded-full px-3 py-1 text-xs font-black uppercase tracking-widest ${healthBadge(focusModel)[1]}`}>{healthBadge(focusModel)[0]}</span>
                    </div>
                    {!activeModel && <p className="mt-4 text-xs text-amber-300">No model was flagged active in history, so the latest deployment has been surfaced instead.</p>}
                    {!hasTrainMetrics(focusModel) && <p className="mt-2 text-xs text-slate-400">This is a legacy deployment entry, so train-side metrics were not captured yet. Run retrain once on the updated backend to fill them.</p>}
                  </div>
                )}
                <button onClick={retrainModel} disabled={processing} className="mt-8 w-full rounded-xl bg-indigo-600 py-4 text-xs font-black uppercase tracking-widest text-white shadow-lg shadow-indigo-900/20 transition-all disabled:cursor-not-allowed disabled:opacity-50">Retrain And Activate Model</button>
              </div>
              <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 p-10">
                <h3 className="mb-6 text-xl font-black text-white">Deployment History</h3>
                <div className="max-h-[480px] space-y-4 overflow-y-auto pr-2">
                  {models.length ? models.map((m) => {
                    const [health, badge] = healthBadge(m)
                    const legacyMetrics = !hasTrainMetrics(m)
                    return (
                      <div key={m.id} className={`rounded-2xl border p-5 ${m.is_active ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-slate-800 bg-slate-950/40'}`}>
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="font-black text-white">{m.name}</p>
                            <p className="mt-1 text-xs text-slate-500">{m.dataset_name || 'Default dataset'} | {fmtDate(m.training_date)}</p>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {m.is_active && <span className="rounded-full bg-blue-500/10 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-blue-400">Active</span>}
                            <span className={`rounded-full px-3 py-1 text-[10px] font-black uppercase tracking-widest ${badge}`}>{health}</span>
                          </div>
                        </div>
                        <div className="mt-4 grid gap-3 sm:grid-cols-2">
                          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3"><p className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">Test R2</p><p className="mt-2 text-lg font-black text-white">{fmtScore(m.r_squared)}</p></div>
                          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3"><p className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">RMSE</p><p className="mt-2 text-lg font-black text-white">{fmtNum(m.rmse)}</p></div>
                          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3"><p className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">Train R2</p><p className="mt-2 text-lg font-black text-white">{legacyMetrics ? 'Legacy run' : fmtScore(m.train_r_squared)}</p></div>
                          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3"><p className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">Gap</p><p className="mt-2 text-lg font-black text-white">{legacyMetrics ? 'Legacy run' : fmtScore(m.overfit_gap)}</p></div>
                        </div>
                        {legacyMetrics && <p className="mt-4 text-xs text-slate-400">Captured before train-gap tracking was enabled. Retrain on the current backend to store full deployment quality metrics.</p>}
                      </div>
                    )
                  }) : <EmptyState title="No deployment history" text="Model versions will appear here after retraining or when historical records are available." />}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inference' && (
          <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 overflow-hidden animate-fadeInLow">
            {predictions.length ? (
              <table className="w-full text-left">
                <thead className="bg-slate-900"><tr className="border-b border-slate-800 text-[10px] font-black uppercase tracking-[0.22em] text-slate-500"><th className="p-8">Symbol</th><th>User</th><th>Prediction</th><th>Recommendation</th><th className="pr-8 text-right">Created</th></tr></thead>
                <tbody className="divide-y divide-slate-800/40">{predictions.map((p) => <tr key={p.id} className="hover:bg-slate-800/10"><td className="p-8 font-bold text-white">{p.stock_symbol}</td><td className="text-slate-300">{p.username || 'Unknown'}</td><td className="font-bold text-blue-400">${fmtNum(p.predicted_price)}</td><td><span className={`rounded-lg px-2 py-1 text-[10px] font-black uppercase ${p.recommendation === 'BUY' ? 'bg-emerald-500/10 text-emerald-400' : p.recommendation === 'SELL' ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'}`}>{p.recommendation}</span></td><td className="pr-8 text-right text-slate-500">{fmtDate(p.created_at)}</td></tr>)}</tbody>
              </table>
            ) : <div className="p-8"><EmptyState title="No prediction logs found" text="Try a different search term, or wait for new predictions to be created." /></div>}
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className="rounded-[2rem] border border-slate-800/70 bg-[#0c1220]/70 overflow-hidden animate-fadeInLow">
            {logs.length ? (
              <table className="w-full text-left">
                <thead className="bg-slate-900"><tr className="border-b border-slate-800 text-[10px] font-black uppercase tracking-[0.22em] text-slate-500"><th className="p-8">Timestamp</th><th>User</th><th>Action</th><th className="pr-8 text-right">Role</th></tr></thead>
                <tbody className="divide-y divide-slate-800/40">{logs.map((l, i) => <tr key={l.id || `${l.timestamp}-${i}`} className="hover:bg-slate-800/10"><td className="p-8 font-mono text-xs text-slate-500">{fmtDate(l.timestamp)}</td><td className="font-bold text-white">{l.user || l.username}</td><td className="text-slate-300">{l.action}</td><td className="pr-8 text-right"><span className="rounded-lg bg-blue-600/10 px-2 py-1 text-[10px] font-black uppercase tracking-widest text-blue-400">{roleLabel(l.role)}</span></td></tr>)}</tbody>
              </table>
            ) : <div className="p-8"><EmptyState title="No activity logs found" text="Search by username or action, or wait for new logged events to appear." /></div>}
          </div>
        )}
      </main>

      <ProfileModal user={selectedUser} onClose={() => setSelectedUser(null)} />
    </div>
  )
}

export default TradeIQAdmin

