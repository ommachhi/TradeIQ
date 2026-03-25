import React, { useState, useEffect, useMemo } from 'react';
import { adminAPI, authHelpers } from '../services/api';
import { 
  FiUsers, FiPieChart, FiTrendingUp, FiCpu, 
  FiDatabase, FiSettings, FiLogOut, FiMenu, 
  FiX, FiActivity, FiSearch, FiCheckCircle, 
  FiAlertCircle, FiClock, FiDownload, FiUpload,
  FiUserPlus, FiShield, FiUserCheck, FiTarget,
  FiBarChart2, FiLayers, FiRefreshCw, FiArrowUp,
  FiArrowDown, FiSmartphone, FiMonitor, FiGlobe,
  FiSave, FiTrash2, FiInfo, FiLock, FiUnlock
} from 'react-icons/fi';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, AreaChart, Area,
  BarChart, Bar, Legend, Cell, PieChart, Pie,
  ComposedChart, Scatter
} from 'recharts';

/**
 * Enterprise-Grade TradeIQ Admin Intelligence Suite
 * Fixed version with resolved navigation and fully functional user management.
 */
const TradeIQAdmin = () => {
  const apiBaseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    (import.meta.env.PROD
      ? 'https://tradeiq-5.onrender.com/api'
      : 'http://localhost:8000/api');

  // Navigation State
  const [activeTab, setActiveTab] = useState('overview');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  
  // Data State
  const [allData, setAllData] = useState({
    stats: null,
    users: [],
    datasets: [],
    models: [],
    logs: [],
    predictions: [],
    systemHealth: { cpu: '12%', ram: '1.4GB', latency: '42ms', uptime: '99.9%' }
  });
  
  // UI State
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [feedback, setFeedback] = useState({ type: null, msg: '' });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [stockSearch, setStockSearch] = useState('');
  const [stockPreview, setStockPreview] = useState(null);

  // Initialize
  useEffect(() => {
    fetchIntelligenceData();
  }, []);

  const fetchIntelligenceData = async () => {
    try {
      setLoading(true);
      
      // Independent fetch to prevent one failure from blocking everything
      const results = await Promise.allSettled([
        adminAPI.getDashboardStats(),
        adminAPI.getUsers(),
        adminAPI.getDatasets(),
        adminAPI.getModelHistory(),
        adminAPI.getActivityLogs()
      ]);

      const [statsRes, usersRes, datasetsRes, modelsRes, logsRes] = results;

      // Native fetch for predictions
      let predictions = [];
      try {
        const resp = await fetch(`${apiBaseUrl}/admin/predictions/`, {
          headers: { 'Authorization': `Bearer ${authHelpers.getToken()}` }
        });
        if (resp.ok) predictions = await resp.json();
      } catch (e) {
        console.error("Prediction fetch failed", e);
      }

      setAllData({
        stats: statsRes.status === 'fulfilled' ? statsRes.value : null,
        users: usersRes.status === 'fulfilled' ? usersRes.value : [],
        datasets: datasetsRes.status === 'fulfilled' ? datasetsRes.value : [],
        models: modelsRes.status === 'fulfilled' ? modelsRes.value : [],
        logs: logsRes.status === 'fulfilled' ? logsRes.value : [],
        predictions: predictions,
        systemHealth: { cpu: '14%', ram: '1.2GB', latency: '38ms', uptime: '99.99%' }
      });

    } catch (err) {
      showFeedback('error', 'Critical System Failure: Unable to handshake with core API.');
    } finally {
      setLoading(false);
    }
  };

  const showFeedback = (type, msg) => {
    setFeedback({ type, msg });
    setTimeout(() => setFeedback({ type: null, msg: '' }), 5000);
  };

  const handleAction = async (actionFn, successMsg) => {
    try {
      setProcessing(true);
      await actionFn();
      showFeedback('success', successMsg);
      await fetchIntelligenceData(); // Refresh data after action
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || 'Operation failed';
      showFeedback('error', errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  // Derived Analytics
  const userActivityData = useMemo(() => {
    const counts = {};
    (allData.predictions || []).forEach(p => {
      counts[p.username || 'System'] = (counts[p.username || 'System'] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  }, [allData.predictions]);

  // Sub-Components
  const MetricCard = ({ label, value, trend, icon: Icon, color }) => (
    <div className={`group glass-card p-6 border-l-4 border-l-${color}-500 hover:scale-[1.02] transition-all duration-300 relative overflow-hidden`}>
      <div className={`absolute top-0 right-0 w-24 h-24 bg-${color}-500/5 rounded-full -mr-8 -mt-8 group-hover:bg-${color}-500/10 transition-colors`}></div>
      <div className="flex justify-between">
        <div>
          <p className="text-slate-400 text-xs font-black uppercase tracking-[2px] mb-1">{label}</p>
          <p className="text-3xl font-black text-white mb-2">{value ?? '---'}</p>
          <div className="flex items-center text-[10px] font-bold">
            {trend && (
              <span className={trend.startsWith('+') ? 'text-green-500' : 'text-red-500'}>
                {trend.startsWith('+') ? <FiArrowUp className="inline mr-1" /> : <FiArrowDown className="inline mr-1" />}
                {trend}
              </span>
            )}
            <span className="text-slate-500 ml-2 uppercase tracking-tighter">vs baseline</span>
          </div>
        </div>
        <div className={`w-12 h-12 rounded-2xl bg-${color}-500/10 flex items-center justify-center text-${color}-500`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );

  if (loading) return (
    <div className="flex h-screen items-center justify-center bg-[#070b14] overflow-hidden">
      <div className="relative">
        <div className="w-24 h-24 rounded-full border-4 border-slate-800 border-t-blue-500 animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center font-black text-blue-500 text-xs">TIQ</div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-[#070b14] text-slate-300 overflow-hidden font-inter selection:bg-blue-500/30">
      {/* Sidebar Navigation */}
      <aside className={`${isSidebarCollapsed ? 'w-24' : 'w-72'} bg-[#0c1220] border-r border-slate-800/50 flex flex-col transition-all duration-500 ease-elastic z-50`}>
        <div className="p-8 flex items-center justify-between">
          {!isSidebarCollapsed && (
            <div className="flex items-center space-x-3 group cursor-pointer" onClick={() => setActiveTab('overview')}>
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.4)] group-hover:rotate-12 transition-transform">
                <FiTrendingUp className="text-white text-xl" />
              </div>
              <div>
                <span className="text-xl font-black text-white tracking-[-0.05em]">INTEL<span className="text-blue-500 underline decoration-blue-500/30 underline-offset-4">CORE</span></span>
                <p className="text-[10px] text-blue-500/60 font-black tracking-widest uppercase">Admin v2.5</p>
              </div>
            </div>
          )}
          <button onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)} className="p-2 hover:bg-slate-800/50 rounded-lg text-slate-500 transition-colors">
            {isSidebarCollapsed ? <FiMenu size={24} /> : <FiX size={24} />}
          </button>
        </div>

        <nav className="flex-1 px-4 mt-6 space-y-2 overflow-y-auto no-scrollbar">
          {[
            { id: 'overview', label: 'Dashboard', icon: FiPieChart },
            { id: 'users', label: 'User Management', icon: FiUsers },
            { id: 'datalake', label: 'Stock Data', icon: FiDatabase },
            { id: 'modelforge', label: 'ML Control', icon: FiCpu },
            { id: 'inference', label: 'Prediction Logs', icon: FiLayers },
            { id: 'compliance', label: 'Activity Logs', icon: FiShield },
            { id: 'config', label: 'Settings', icon: FiSettings },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center p-4 rounded-2xl transition-all duration-300 group ${
                activeTab === item.id 
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20 shadow-[0_4px_20px_rgba(59,130,246,0.1)]' 
                  : 'text-slate-500 hover:bg-slate-800/30 hover:text-slate-100'
              }`}
            >
              <item.icon className={`text-xl ${isSidebarCollapsed ? 'mx-auto' : 'mr-4'} ${activeTab === item.id ? 'animate-pulse' : ''}`} />
              {!isSidebarCollapsed && <span className="font-bold tracking-tight">{item.label}</span>}
              {activeTab === item.id && !isSidebarCollapsed && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,1)]"></div>}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-slate-800/50 space-y-4">
          <button 
            onClick={() => window.location.href = '/dashboard'}
            className="w-full flex items-center p-4 text-blue-400/70 hover:bg-blue-500/10 hover:text-blue-400 rounded-2xl transition-all font-bold border border-transparent hover:border-blue-500/20"
          >
            <FiGlobe className={`${isSidebarCollapsed ? 'mx-auto' : 'mr-4'} text-xl`} />
            {!isSidebarCollapsed && <span>Return to Site</span>}
          </button>
          
          <button 
            onClick={() => authHelpers.logout()}
            className="w-full flex items-center p-4 text-red-400/70 hover:bg-red-500/10 hover:text-red-400 rounded-2xl transition-all font-bold"
          >
            <FiLogOut className={`${isSidebarCollapsed ? 'mx-auto' : 'mr-4'} text-xl`} />
            {!isSidebarCollapsed && <span>Terminate Session</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-10 relative custom-scrollbar">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between mb-12 gap-6 bg-[#0c1220]/50 p-6 rounded-[2rem] border border-slate-800/30 backdrop-blur-xl sticky top-0 z-40">
          <div>
            <h1 className="text-4xl font-black text-white tracking-tight uppercase">
              {activeTab === 'overview' ? 'Sovereign Operations' : activeTab.replace(/([A-Z])/g, ' $1').trim()}
            </h1>
            <div className="flex items-center mt-2 space-x-3 text-xs font-bold text-slate-500">
              <span className="flex items-center"><FiGlobe className="mr-1 text-green-500" /> System: Global Stable</span>
              <span className="w-1 h-1 rounded-full bg-slate-700"></span>
              <span className="flex items-center"><FiClock className="mr-1" /> Uptime: 99.98%</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="relative">
              <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
              <input 
                type="text" 
                placeholder="Secure resource lookup..."
                className="pl-12 pr-6 py-3.5 bg-slate-900/80 border border-slate-700/50 rounded-2xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40 w-80 text-sm font-medium transition-all"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="hidden lg:flex items-center p-2 pr-6 bg-slate-900/80 border border-slate-700/50 rounded-full">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-purple-800 flex items-center justify-center font-black text-white shadow-lg ring-2 ring-blue-500/20 mr-4">
                {authHelpers.getUsername()?.[0].toUpperCase()}
              </div>
              <div className="text-left">
                <p className="text-xs font-black text-white leading-none uppercase">{authHelpers.getUsername()}</p>
                <p className="text-[10px] text-blue-500/80 font-black tracking-widest mt-1">SUPER ADMIN</p>
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Alerts */}
        {feedback.msg && (
          <div className={`mb-10 p-6 rounded-[1.5rem] border animate-slideIn ${
            feedback.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-green-500/10 border-green-500/20 text-green-500'
          } flex items-center justify-between`}>
            <div className="flex items-center">
              {feedback.type === 'error' ? <FiAlertCircle size={24} className="mr-4" /> : <FiCheckCircle size={24} className="mr-4" />}
              <span className="font-bold tracking-tight">{feedback.msg}</span>
            </div>
            <button onClick={() => setFeedback({ type: null, msg: '' })} className="hover:opacity-50">Dismiss</button>
          </div>
        )}

        {/* PROPER CONDITIONAL RENDERING */}
        
        {/* VIEW: OVERVIEW / DASHBOARD */}
        {activeTab === 'overview' && (
          <div className="space-y-10 animate-fadeInLow">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <MetricCard label="Compute Load" value={allData.systemHealth.cpu} trend="+1.2%" icon={FiCpu} color="blue" />
              <MetricCard label="Active Clients" value={allData.stats?.users?.active || 0} trend="+14% w/w" icon={FiUsers} color="purple" />
              <MetricCard label="Signal Throughput" value={allData.stats?.predictions?.total || 0} trend="+8% d/d" icon={FiTarget} color="green" />
              <MetricCard label="API Latency" value={allData.systemHealth.latency} trend="-4ms" icon={FiGlobe} color="amber" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 glass-card p-8">
                <div className="flex justify-between items-center mb-8">
                  <div>
                    <h3 className="text-2xl font-black text-white tracking-tight">Intelligence Velocity</h3>
                    <p className="text-sm text-slate-500 font-bold">Aggregate inference patterns for last 7 cycles</p>
                  </div>
                </div>
                <div className="h-[350px] w-full text-blue-500">
                  <ResponsiveContainer>
                    <AreaChart data={allData.stats?.prediction_trend || []}>
                      <defs>
                        <linearGradient id="velocityGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                      <XAxis dataKey="date" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} dy={15} />
                      <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} dx={-15} />
                      <Tooltip contentStyle={{ backgroundColor: '#0c1220', borderRadius: '16px', border: '1px solid #334155' }} />
                      <Area type="monotone" dataKey="count" fill="url(#velocityGrad)" stroke="#3b82f6" strokeWidth={4} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="glass-card p-8 bg-slate-900/50">
                <h3 className="text-xl font-black text-white mb-8 border-b border-slate-800/50 pb-4">Top Operatives</h3>
                <div className="space-y-6">
                  {userActivityData.map((user, i) => (
                    <div key={i} className="flex items-center space-x-4 p-4 rounded-2xl bg-slate-800/20 border border-slate-700/30">
                      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-black text-lg ${i === 0 ? 'bg-yellow-500/10 text-yellow-500' : 'bg-slate-800 text-slate-500'}`}>
                        {i + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-black tracking-tight">{user.name}</p>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{user.count} Inferences</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: USER MANAGEMENT */}
        {activeTab === 'users' && (
          <div className="space-y-8 animate-fadeInLow">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-3xl font-black text-white tracking-tight">User Management</h2>
                <p className="text-slate-500 text-sm mt-1">Control access for {allData.users.length} registered accounts</p>
              </div>
            </div>

            <div className="glass-card overflow-hidden">
              <table className="w-full text-left">
                <thead className="bg-[#0c1220]/80">
                  <tr className="text-[10px] font-black text-slate-500 uppercase tracking-[3px] border-b border-slate-800">
                    <th className="p-8">Username / ID</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Last Seen</th>
                    <th className="text-right pr-8">Control</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {allData.users.filter(u => u.username.toLowerCase().includes(searchTerm.toLowerCase())).map((user) => (
                    <tr key={user.id} className="hover:bg-slate-800/20 transition-colors group">
                      <td className="p-8">
                        <div className="flex items-center space-x-5">
                          <div className={`w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center font-black text-white border border-slate-700`}>
                            {user.username[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="text-white font-black">{user.username}</p>
                            <p className="text-xs text-slate-500">{user.email || 'N/A'}</p>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`px-3 py-1 rounded-xl text-[10px] font-black uppercase tracking-widest ${user.role === 'admin' ? 'bg-red-500/10 text-red-400' : 'bg-blue-500/10 text-blue-400'}`}>
                          {user.role}
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,1)]' : 'bg-red-500'}`}></div>
                          <span className={`text-xs font-bold ${user.is_active ? 'text-green-500' : 'text-red-500'}`}>
                            {user.is_active ? 'Active' : 'Blocked'}
                          </span>
                        </div>
                      </td>
                      <td className="text-sm text-slate-500">{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                      <td className="text-right pr-8">
                        <button 
                          disabled={processing}
                          onClick={() => handleAction(
                            () => adminAPI.updateUser(user.id, { is_active: !user.is_active }),
                            `User ${user.username} is now ${!user.is_active ? 'Active' : 'Blocked'}`
                          )}
                          className={`p-3 rounded-xl transition-all ${user.is_active ? 'bg-red-500/10 text-red-500 hover:bg-red-600' : 'bg-green-500/10 text-green-500 hover:bg-green-600'} hover:text-white`}
                        >
                           {user.is_active ? <FiLock size={18} /> : <FiUnlock size={18} />}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* VIEW: DATA LAKE / STOCK DATA */}
        {activeTab === 'datalake' && (
          <div className="space-y-10 animate-fadeInLow">
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-black text-white">Stock Data Records</h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              <div className="lg:col-span-1 glass-card p-6 h-fit">
                <h4 className="text-white font-black text-xs uppercase mb-6">Fetch Live Data</h4>
                <div className="space-y-4">
                  <input 
                    type="text" 
                    placeholder="Ticker e.g. AAPL"
                    className="w-full bg-slate-800 border-none rounded-xl p-4 text-white font-bold"
                    value={stockSearch}
                    onChange={(e) => setStockSearch(e.target.value.toUpperCase())}
                  />
                  <button 
                    onClick={async () => {
                      try {
                        setProcessing(true);
                        const data = await adminAPI.fetchStockData(stockSearch);
                        setStockPreview(data);
                        showFeedback('success', 'Relay success: Data fetched.');
                      } catch (e) {
                         showFeedback('error', 'Fetch failed.');
                      } finally { setProcessing(false); }
                    }}
                    className="w-full py-4 bg-blue-600 text-white rounded-xl font-black uppercase text-xs"
                  >
                    Sync Stock Data
                  </button>
                </div>
              </div>
              <div className="lg:col-span-3 glass-card overflow-hidden">
                <div className="p-6 bg-slate-900/50 border-b border-slate-800">
                   <h3 className="text-white font-black">Data Preview: {stockPreview?.symbol || 'None'}</h3>
                </div>
                <div className="max-h-[500px] overflow-y-auto no-scrollbar">
                   <table className="w-full text-left text-xs">
                      <thead className="bg-slate-900 sticky top-0">
                         <tr className="text-slate-500 font-black uppercase border-b border-slate-800">
                            <th className="p-4">Date</th>
                            <th>Close</th>
                            <th>Volume</th>
                         </tr>
                      </thead>
                      <tbody>
                        {stockPreview?.data?.map((row, i) => (
                           <tr key={i} className="border-b border-slate-800/10">
                              <td className="p-4 font-mono text-slate-400">{row.date}</td>
                              <td className="font-bold text-blue-400">${row.close.toFixed(2)}</td>
                              <td className="text-slate-500">{row.volume.toLocaleString()}</td>
                           </tr>
                        ))}
                      </tbody>
                   </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: ML CONTROL / MODEL FORGE */}
        {activeTab === 'modelforge' && (
          <div className="space-y-10 animate-fadeInLow">
            <h2 className="text-3xl font-black text-white">Model Forge</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="glass-card p-10 space-y-8">
                <div className="flex items-center space-x-4">
                  <FiCpu className="text-indigo-500" size={32} />
                  <h3 className="text-xl font-black text-white">Retrain Active Model</h3>
                </div>
                <p className="text-slate-500 text-sm italic">This will update the core weights of the LSTM architecture using the latest staged datasets.</p>
                <button 
                  onClick={() => handleAction(() => adminAPI.retrainModel({ model_name: 'LSTM_V4' }), 'Training started.')}
                  className="w-full py-4 bg-indigo-600 text-white rounded-xl font-black uppercase shadow-lg shadow-indigo-900/20"
                >
                  Confirm Neural Training
                </button>
              </div>
              <div className="glass-card p-10">
                 <h3 className="text-xl font-black text-white mb-6">Deployment History</h3>
                 <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2">
                    {allData.models.map((m, i) => (
                       <div key={i} className={`p-4 rounded-2xl border ${m.is_active ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-slate-800 bg-[#0c1220]'}`}>
                          <div className="flex justify-between">
                             <span className="font-black text-white">{m.name}</span>
                             <span className="text-green-500 font-black">{(m.r_squared * 100).toFixed(1)}% Acc</span>
                          </div>
                       </div>
                    ))}
                 </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: PREDICTION LOGS */}
        {activeTab === 'inference' && (
          <div className="space-y-10 animate-fadeInLow">
             <h2 className="text-3xl font-black text-white">Prediction Audit Logs</h2>
             <div className="glass-card overflow-hidden">
                <table className="w-full text-left">
                   <thead className="bg-slate-900">
                      <tr className="text-[10px] font-black text-slate-500 uppercase tracking-widest border-b border-slate-800">
                         <th className="p-8">Assigned Vector</th>
                         <th>Inferred Price</th>
                         <th>Recommendation</th>
                         <th className="text-right pr-8">Cycle Time</th>
                      </tr>
                   </thead>
                   <tbody className="divide-y divide-slate-800/40">
                      {allData.predictions.map((p, i) => (
                        <tr key={i} className="hover:bg-slate-800/10">
                           <td className="p-8 text-white font-bold">{p.stock_symbol}</td>
                           <td className="text-blue-400 font-bold">${parseFloat(p.predicted_price).toFixed(2)}</td>
                           <td>
                              <span className={`px-2 py-1 rounded-lg text-[10px] font-black uppercase ${p.recommendation === 'BUY' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                                 {p.recommendation}
                              </span>
                           </td>
                           <td className="text-right pr-8 text-slate-500">{new Date(p.created_at).toLocaleTimeString()}</td>
                        </tr>
                      ))}
                   </tbody>
                </table>
             </div>
          </div>
        )}

        {/* VIEW: ACTIVITY LOGS */}
        {activeTab === 'compliance' && (
          <div className="space-y-10 animate-fadeInLow">
             <h2 className="text-3xl font-black text-white">System Compliance Logs</h2>
             <div className="glass-card overflow-hidden">
                <table className="w-full text-left">
                   <thead className="bg-slate-900">
                      <tr className="text-[10px] font-black text-slate-500 uppercase border-b border-slate-800">
                         <th className="p-8">Timestamp</th>
                         <th>User</th>
                         <th>Action Protocol</th>
                         <th className="text-right pr-8">Handshake Method</th>
                      </tr>
                   </thead>
                   <tbody className="divide-y divide-slate-800/40">
                      {allData.logs.map((l, i) => (
                        <tr key={i} className="hover:bg-slate-800/10">
                           <td className="p-8 text-slate-500 font-mono text-xs">{new Date(l.timestamp).toLocaleString()}</td>
                           <td className="text-white font-bold">{l.user || l.username}</td>
                           <td className="text-slate-300">{l.action}</td>
                           <td className="text-right pr-8"><span className="text-[10px] font-black px-2 py-1 bg-blue-600/10 text-blue-400 rounded">REST_v1.2</span></td>
                        </tr>
                      ))}
                   </tbody>
                </table>
             </div>
          </div>
        )}

        {/* VIEW: SETTINGS */}
        {activeTab === 'config' && (
          <div className="space-y-10 animate-fadeInLow max-w-4xl">
             <h2 className="text-3xl font-black text-white">System Core Config</h2>
             <div className="glass-card p-10 space-y-6">
                <div>
                   <label className="text-xs font-black text-slate-500 uppercase tracking-widest mb-2 block">Alpha Signal Threshold</label>
                   <input type="range" className="w-full" defaultValue={85} />
                </div>
                <div className="p-6 bg-red-500/5 rounded-2xl border border-red-500/10">
                   <h4 className="text-red-500 font-black mb-2">Danger Operations</h4>
                   <button className="px-6 py-3 bg-red-600 text-white rounded-xl font-black uppercase text-xs">Purge All Inference Records</button>
                </div>
             </div>
          </div>
        )}

      </main>
    </div>
  );
};

export default TradeIQAdmin;