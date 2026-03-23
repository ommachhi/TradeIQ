import React, { useState, useEffect } from 'react';
import { adminAPI, authHelpers, reportAPI } from '../services/api';
import { 
  FiPieChart, FiLayers, FiShield, FiLogOut, FiMenu, 
  FiX, FiActivity, FiSearch, FiCheckCircle, 
  FiAlertCircle, FiClock, FiGlobe, FiTarget,
  FiArrowUp, FiArrowDown, FiDownload, FiInfo,
  FiTrendingUp, FiBarChart2
} from 'react-icons/fi';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';

const MarketAnalystDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [feedback, setFeedback] = useState({ type: null, msg: '' });
  const [allData, setAllData] = useState({
    predictions: [],
    logs: [],
    stats: null
  });

  const COLORS = ['#3b82f6', '#ef4444', '#f59e0b'];

  useEffect(() => {
    fetchAnalystData();
  }, []);

  const fetchAnalystData = async () => {
    try {
      setLoading(true);
      
      const results = await Promise.allSettled([
        adminAPI.getDashboardStats(),
        adminAPI.getActivityLogs()
      ]);

      const [statsRes, logsRes] = results;

      setAllData({
        stats: statsRes.status === 'fulfilled' ? statsRes.value : null,
        logs: logsRes.status === 'fulfilled' ? logsRes.value : [],
        predictions: await adminAPI.getPredictions()
      });
    } catch (err) {
      showFeedback('error', 'Failed to synchronize Market Desk.');
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
      await fetchAnalystData();
    } catch (err) {
      showFeedback('error', 'Operation failed');
    } finally {
      setProcessing(false);
    }
  };

  const sentimentData = [
    { name: 'BUY', value: allData.predictions.filter(p => p.recommendation === 'BUY').length },
    { name: 'SELL', value: allData.predictions.filter(p => p.recommendation === 'SELL').length },
    { name: 'HOLD', value: allData.predictions.filter(p => p.recommendation === 'HOLD').length },
  ].filter(d => d.value > 0);

  if (loading) return (
    <div className="flex h-screen items-center justify-center bg-[#070b14]">
      <div className="w-12 h-12 border-4 border-slate-800 border-t-amber-500 rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="flex h-screen bg-[#070b14] text-slate-300 overflow-hidden font-inter">
      {/* Analyst Sidebar */}
      <aside className={`${isSidebarCollapsed ? 'w-20' : 'w-64'} bg-[#0e1629] border-r border-slate-800/50 flex flex-col transition-all duration-300 z-50`}>
        <div className="p-6 flex items-center justify-between">
          {!isSidebarCollapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-amber-600 rounded-lg flex items-center justify-center shadow-lg">
                <FiBarChart2 className="text-white" />
              </div>
              <span className="font-black text-white text-lg tracking-tighter uppercase italic">Analyst<span className="text-amber-500">Desk</span></span>
            </div>
          )}
          <button onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)} className="p-2 text-slate-500">
            {isSidebarCollapsed ? <FiMenu size={20} /> : <FiX size={20} />}
          </button>
        </div>

        <nav className="flex-1 px-4 mt-10 space-y-2">
          {[
            { id: 'overview', label: 'Monitor', icon: FiPieChart },
            { id: 'inference', label: 'Market Signals', icon: FiLayers },
            { id: 'compliance', label: 'Protocols', icon: FiShield },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center p-4 rounded-xl transition-all ${
                activeTab === item.id ? 'bg-amber-600/10 text-amber-500 border border-amber-500/20' : 'text-slate-500 hover:bg-slate-800/30'
              }`}
            >
              <item.icon className={`${isSidebarCollapsed ? 'mx-auto' : 'mr-4'} text-xl`} />
              {!isSidebarCollapsed && <span className="font-bold">{item.label}</span>}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-slate-800/50 space-y-4">
           <button onClick={() => window.location.href = '/dashboard'} className="w-full flex items-center p-3 text-slate-400 hover:text-white transition-all text-sm font-bold">
            <FiGlobe className="mr-3" /> {!isSidebarCollapsed && 'Leave Desk'}
          </button>
          <button onClick={() => authHelpers.logout()} className="w-full flex items-center p-3 text-red-500/70 hover:text-red-500 transition-all text-sm font-bold">
            <FiLogOut className="mr-3" /> {!isSidebarCollapsed && 'Term. Session'}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-10 relative">
        <header className="mb-10 flex justify-between items-end border-b border-slate-800/50 pb-8">
           <div>
              <p className="text-amber-500 font-black text-xs uppercase tracking-[3px] mb-1">Market Strategy Specialist</p>
              <h1 className="text-4xl font-black text-white uppercase italic tracking-tighter">
                {activeTab === 'overview' ? 'Market Sentiment' : activeTab.replace(/([A-Z])/g, ' $1').trim()}
              </h1>
           </div>
           <div className="flex flex-col items-end">
              <p className="text-xs font-black text-white">{authHelpers.getUsername()}</p>
              <p className="text-[10px] text-amber-400 font-bold uppercase">Senior Analyst</p>
           </div>
        </header>

        {feedback.msg && (
          <div className={`mb-6 p-4 rounded-xl border ${feedback.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-green-500/10 border-green-500/20 text-green-500'} font-bold`}>
            {feedback.msg}
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="space-y-10 animate-fadeInLow">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
               <div className="glass-card p-8 bg-slate-900/50 border-t-4 border-t-amber-500">
                  <p className="text-xs font-black text-slate-500 uppercase tracking-widest mb-2">Alpha Signals</p>
                  <p className="text-4xl font-black text-white">{allData.predictions.length}</p>
                  <p className="text-xs text-amber-500 font-bold mt-4">+22% vs Prev Day</p>
               </div>
               <div className="glass-card p-8 bg-slate-900/50 border-t-4 border-t-blue-500">
                  <p className="text-xs font-black text-slate-500 uppercase tracking-widest mb-2">Confidence Index</p>
                  <p className="text-4xl font-black text-white">88.4%</p>
                  <p className="text-xs text-blue-500 font-bold mt-4">Optimized Alpha V4</p>
               </div>
               <div className="glass-card p-8 bg-slate-900/50 border-t-4 border-t-green-500">
                  <p className="text-xs font-black text-slate-500 uppercase tracking-widest mb-2">Compliance Rating</p>
                  <p className="text-4xl font-black text-white">AAA</p>
                  <p className="text-xs text-green-500 font-bold mt-4">Security Protocol: Active</p>
               </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
               <div className="glass-card p-8">
                  <h3 className="text-white font-black mb-8 flex items-center italic uppercase"><FiTarget className="mr-3 text-amber-500"/> Signal Breakdown</h3>
                  <div className="h-[300px] w-full">
                     <ResponsiveContainer>
                        <PieChart>
                           <Pie 
                             data={sentimentData} 
                             innerRadius={80} 
                             outerRadius={120} 
                             paddingAngle={5} 
                             dataKey="value"
                            >
                              {sentimentData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                           </Pie>
                           <Tooltip contentStyle={{ background: '#0c1220', border: 'none', borderRadius: '12px' }} />
                        </PieChart>
                     </ResponsiveContainer>
                  </div>
               </div>
               <div className="glass-card p-8 overflow-y-auto max-h-[400px]">
                  <h3 className="text-white font-black mb-6 uppercase tracking-widest text-xs">Priority Vectors</h3>
                  <div className="space-y-4">
                     {allData.predictions.sort((a,b) => b.predicted_price - a.predicted_price).slice(0, 10).map((p, i) => (
                        <div key={i} className="flex justify-between items-center p-4 bg-slate-800/10 rounded-2xl border border-slate-700/20">
                           <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center font-black text-amber-500">
                                 {p.stock_symbol[0]}
                              </div>
                              <span className="text-white font-black tracking-tight">{p.stock_symbol}</span>
                           </div>
                           <span className={`text-xs font-black ${p.recommendation === 'BUY' ? 'text-green-500' : 'text-red-500'}`}>${p.predicted_price}</span>
                        </div>
                     ))}
                  </div>
               </div>
            </div>
          </div>
        )}

        {activeTab === 'inference' && (
          <div className="space-y-8 animate-fadeInLow">
             <div className="flex items-center justify-between">
                <h2 className="text-2xl font-black text-white italic">Algorithmic Inferences</h2>
                <button className="flex items-center space-x-2 text-amber-500 font-black text-xs uppercase hover:underline">
                   <FiDownload /> <span>Export Tactical Report</span>
                </button>
             </div>
             <div className="glass-card overflow-hidden border-amber-500/10">
                <table className="w-full text-left">
                   <thead className="bg-[#0c1629]">
                      <tr className="text-[10px] font-black text-slate-500 uppercase tracking-[2px] border-b border-slate-800">
                         <th className="p-8">Vector ID</th>
                         <th>Predicted Exit</th>
                         <th>Rec Status</th>
                         <th className="text-right pr-8">Report Gen</th>
                      </tr>
                   </thead>
                   <tbody className="divide-y divide-slate-800/30">
                      {allData.predictions.map((p, i) => (
                        <tr key={i} className="hover:bg-slate-800/10 transition-colors">
                           <td className="p-8 text-white font-black tracking-tighter underline underline-offset-4 decoration-slate-700 cursor-pointer">{p.stock_symbol}</td>
                           <td className="text-amber-500 font-black">${parseFloat(p.predicted_price).toFixed(2)}</td>
                           <td>
                              <span className={`px-3 py-1 rounded-xl text-[10px] font-black tracking-widest ${p.recommendation === 'BUY' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                                 {p.recommendation}
                              </span>
                           </td>
                           <td className="text-right pr-8">
                              <button 
                                onClick={() => handleAction(() => reportAPI.generatePDF(p.id), 'Exporting tactical data...')}
                                className="p-2 text-slate-500 hover:text-white"
                               >
                                <FiDownload size={18} />
                              </button>
                           </td>
                        </tr>
                      ))}
                   </tbody>
                </table>
             </div>
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className="space-y-8 animate-fadeInLow">
             <div className="flex items-center justify-between">
                <h2 className="text-2xl font-black text-white italic">Audit Protocols</h2>
                <div className="flex items-center space-x-2 text-slate-500 font-bold text-xs uppercase">
                   <FiShield /> <span>Standard Regulatory Compliance: ACTIVE</span>
                </div>
             </div>
             <div className="glass-card p-6 divide-y divide-slate-800/30">
                {allData.logs.map((log, i) => (
                   <div key={i} className="py-4 flex justify-between items-center group hover:bg-slate-800/10 px-4 rounded-xl transition-all">
                      <div className="flex items-center space-x-4">
                         <div className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></div>
                         <div>
                            <p className="text-white font-bold text-sm tracking-tight">{log.action}</p>
                            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">{log.user}</p>
                         </div>
                      </div>
                      <div className="text-right">
                         <p className="text-[10px] text-slate-400 font-bold">{new Date(log.timestamp).toLocaleString()}</p>
                         <p className="text-[10px] text-amber-500/50 font-black uppercase">{log.role}</p>
                      </div>
                   </div>
                ))}
             </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default MarketAnalystDashboard;
