import React, { useState, useEffect } from 'react';
import { adminAPI, authHelpers } from '../services/api';
import { 
  FiPieChart, FiCpu, FiDatabase, FiLogOut, FiMenu, 
  FiX, FiActivity, FiSearch, FiCheckCircle, 
  FiAlertCircle, FiClock, FiGlobe, FiTarget,
  FiArrowUp, FiArrowDown, FiLayers, FiRefreshCw
} from 'react-icons/fi';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts';

const ResearcherDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [feedback, setFeedback] = useState({ type: null, msg: '' });
  const [allData, setAllData] = useState({
    datasets: [],
    models: [],
    stats: null,
    systemHealth: { cpu: '24%', ram: '2.8GB', latency: '45ms' }
  });
  const [stockSearch, setStockSearch] = useState('');
  const [stockPreview, setStockPreview] = useState(null);

  useEffect(() => {
    fetchResearcherData();
  }, []);

  const fetchResearcherData = async () => {
    try {
      setLoading(true);
      const results = await Promise.allSettled([
        adminAPI.getDashboardStats(),
        adminAPI.getDatasets(),
        adminAPI.getModelHistory()
      ]);
      
      const [statsRes, datasetsRes, modelsRes] = results;

      setAllData({
        stats: statsRes.status === 'fulfilled' ? statsRes.value : null,
        datasets: datasetsRes.status === 'fulfilled' ? datasetsRes.value : [],
        models: modelsRes.status === 'fulfilled' ? modelsRes.value : [],
        systemHealth: { cpu: '22%', ram: '2.1GB', latency: '40ms' }
      });
    } catch (err) {
      showFeedback('error', 'Failed to sync with Research Lab.');
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
      await fetchResearcherData();
    } catch (err) {
      showFeedback('error', 'Operation failed');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) return (
    <div className="flex h-screen items-center justify-center bg-[#070b14]">
      <div className="w-12 h-12 border-4 border-slate-800 border-t-indigo-500 rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="flex h-screen bg-[#070b14] text-slate-300 overflow-hidden font-inter">
      {/* Researcher Sidebar */}
      <aside className={`${isSidebarCollapsed ? 'w-20' : 'w-64'} bg-[#0c1220] border-r border-slate-800/50 flex flex-col transition-all duration-300 z-50`}>
        <div className="p-6 flex items-center justify-between">
          {!isSidebarCollapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
                <FiCpu className="text-white" />
              </div>
              <span className="font-black text-white text-lg tracking-tighter">RESEARCH<span className="text-indigo-500">LAB</span></span>
            </div>
          )}
          <button onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)} className="p-2 text-slate-500">
            {isSidebarCollapsed ? <FiMenu size={20} /> : <FiX size={20} />}
          </button>
        </div>

        <nav className="flex-1 px-4 mt-10 space-y-2">
          {[
            { id: 'overview', label: 'Lab Stats', icon: FiPieChart },
            { id: 'datalake', label: 'Data Lake', icon: FiDatabase },
            { id: 'modelforge', label: 'Model Forge', icon: FiLayers },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center p-4 rounded-xl transition-all ${
                activeTab === item.id ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20' : 'text-slate-500 hover:bg-slate-800/30'
              }`}
            >
              <item.icon className={`${isSidebarCollapsed ? 'mx-auto' : 'mr-4'} text-xl`} />
              {!isSidebarCollapsed && <span className="font-bold">{item.label}</span>}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-slate-800/50 space-y-4">
          <button onClick={() => window.location.href = '/dashboard'} className="w-full flex items-center p-3 text-slate-400 hover:text-white transition-all text-sm font-bold">
            <FiGlobe className="mr-3" /> {!isSidebarCollapsed && 'Exit Lab'}
          </button>
          <button onClick={() => authHelpers.logout()} className="w-full flex items-center p-3 text-red-500/70 hover:text-red-500 transition-all text-sm font-bold">
            <FiLogOut className="mr-3" /> {!isSidebarCollapsed && 'Term. Session'}
          </button>
        </div>
      </aside>

      {/* Main Lab Area */}
      <main className="flex-1 overflow-y-auto p-10 relative">
        <header className="mb-10 flex justify-between items-end border-b border-slate-800/50 pb-8">
           <div>
              <p className="text-indigo-500 font-black text-xs uppercase tracking-widest mb-1">Computational Scientist</p>
              <h1 className="text-4xl font-black text-white uppercase italic tracking-tighter">
                {activeTab === 'overview' ? 'Lab Monitoring' : activeTab.replace(/([A-Z])/g, ' $1').trim()}
              </h1>
           </div>
           <div className="flex items-center space-x-4 bg-slate-900 px-6 py-3 rounded-2xl border border-slate-800">
              <div className="text-right">
                 <p className="text-xs font-black text-white">{authHelpers.getUsername()}</p>
                 <p className="text-[10px] text-indigo-400 font-bold uppercase">Researcher</p>
              </div>
           </div>
        </header>

        {feedback.msg && (
          <div className={`mb-6 p-4 rounded-xl border ${feedback.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-green-500/10 border-green-500/20 text-green-500'} font-bold`}>
            {feedback.msg}
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fadeIn">
             <div className="glass-card p-8">
                <h3 className="text-white font-black mb-6 flex items-center"><FiActivity className="mr-2 text-indigo-500"/> Pipeline Health</h3>
                <div className="space-y-4">
                   <div className="flex justify-between items-center bg-slate-800/30 p-4 rounded-xl border border-slate-700/20">
                      <span className="text-slate-400 text-sm">GPU Capacity</span>
                      <span className="text-white font-black">94.2%</span>
                   </div>
                   <div className="flex justify-between items-center bg-slate-800/30 p-4 rounded-xl border border-slate-700/20">
                      <span className="text-slate-400 text-sm">Active Threads</span>
                      <span className="text-white font-black">128 / 512</span>
                   </div>
                </div>
             </div>
             <div className="glass-card p-8">
                <h3 className="text-white font-black mb-6">Execution Accuracy</h3>
                <div className="h-48 w-full">
                   <ResponsiveContainer>
                      <BarChart data={allData.models.slice(0, 5)}>
                        <Bar dataKey="r_squared" fill="#6366f1" radius={[4, 4, 0, 0]} />
                        <XAxis dataKey="name" hide />
                        <Tooltip cursor={false} contentStyle={{ background: '#0c1220', border: 'none', borderRadius: '8px', fontSize: '12px' }}/>
                      </BarChart>
                   </ResponsiveContainer>
                </div>
             </div>
          </div>
        )}

        {activeTab === 'datalake' && (
          <div className="space-y-8 animate-fadeIn">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="glass-card p-8 space-y-6">
                <h3 className="text-white font-black">Sync Stock Symbols</h3>
                <input 
                  type="text" 
                  placeholder="Ticker Symbol (e.g. BTC-USD)" 
                  className="w-full bg-slate-800 p-4 rounded-xl border-none text-white font-bold"
                  value={stockSearch}
                  onChange={(e) => setStockSearch(e.target.value.toUpperCase())}
                />
                <button 
                  onClick={() => handleAction(async () => {
                    const data = await adminAPI.fetchStockData(stockSearch);
                    setStockPreview(data);
                  }, 'Data ingestion complete.')}
                  className="w-full py-4 bg-indigo-600 rounded-xl font-black text-white"
                >
                  Ingest Market Data
                </button>
              </div>
              <div className="lg:col-span-2 glass-card overflow-hidden">
                <div className="p-6 border-b border-slate-800 bg-slate-900/50">
                   <p className="text-white font-black text-sm uppercase">Datalake Records</p>
                </div>
                <div className="max-h-[400px] overflow-y-auto p-4 space-y-2">
                   {allData.datasets.map((d, i) => (
                     <div key={i} className="flex justify-between items-center p-4 bg-slate-800/20 rounded-xl border border-slate-700/20">
                        <span className="text-white font-bold">{d.name}</span>
                        <span className="text-slate-500 text-xs">{d.row_count} Rows</span>
                     </div>
                   ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'modelforge' && (
          <div className="max-w-xl animate-fadeIn">
             <div className="glass-card p-10 space-y-8">
                <h3 className="text-2xl font-black text-white italic">Neural Network Factory</h3>
                <p className="text-slate-500">Initialize specialized LSTM training sequence based on current market volatility and available datalake vectors.</p>
                <div className="p-6 bg-indigo-600/5 border border-indigo-600/20 rounded-2xl">
                   <div className="flex justify-between mb-4">
                      <span className="text-xs font-black text-slate-400 uppercase">Architecture</span>
                      <span className="text-xs font-black text-indigo-400">LSTM V.5 Beta</span>
                   </div>
                   <div className="flex justify-between">
                      <span className="text-xs font-black text-slate-400 uppercase">Optimizer</span>
                      <span className="text-xs font-black text-indigo-400">Adam (0.001)</span>
                   </div>
                </div>
                <button 
                  onClick={() => handleAction(() => adminAPI.retrainModel({ model_name: 'STOCHASTIC_V1' }), 'Initiating Model Forge sequence...')}
                  className="w-full py-5 bg-indigo-600 hover:bg-indigo-500 text-white font-black rounded-2xl shadow-xl shadow-indigo-900/30 transition-all flex items-center justify-center"
                >
                  <FiRefreshCw className={`mr-2 ${processing ? 'animate-spin' : ''}`} /> Run Neural Evolution
                </button>
             </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ResearcherDashboard;
