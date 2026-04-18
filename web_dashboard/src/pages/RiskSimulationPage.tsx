import React, { useState, useEffect } from 'react';
import { 
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
    AreaChart, Area, BarChart, Bar, Legend, Cell
} from 'recharts';
import { 
    Activity, Play, Server, Shield, TrendingDown, 
    Calculator, Info, AlertCircle, Globe, MapPin, Percent, Building2,
    Download, RefreshCw, Layers, Zap
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './RiskSimulationPage.css';

const RiskSimulationPage = () => {
    const [hierarchy, setHierarchy] = useState<Record<string, string[]>>({});
    const [selectedWilaya, setSelectedWilaya] = useState('16 - ALGER');
    const [selectedCommune, setSelectedCommune] = useState('ROUIBA');
    const [group, setGroup] = useState('1A');
    const [rpaInfo, setRpaInfo] = useState({ zone: 'III', a_coeff: 0.40, premium: 0 });
    
    const [params, setParams] = useState({
        total_value: 1837788333,
        a_coeff: 0.4,
        retention: 0.30,
        degree: "III",
        iterations: 10000
    });

    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [simProgress, setSimProgress] = useState(0);

    useEffect(() => {
        fetchHierarchy();
    }, []);

    useEffect(() => {
        lookupRPA();
    }, [selectedWilaya, selectedCommune]);

    const fetchHierarchy = async () => {
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/portfolio/hierarchy`);
            const data = await res.json();
            setHierarchy(data);
            if (data['16 - ALGER']) {
                 setSelectedWilaya('16 - ALGER');
                 setSelectedCommune(data['16 - ALGER'][0] || 'ROUIBA');
            }
        } catch (err) { console.error(err); }
    };

    const lookupRPA = async () => {
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/rpa/lookup?wilaya=${encodeURIComponent(selectedWilaya)}&commune=${encodeURIComponent(selectedCommune)}&group=1A`);
            const data = await res.json();
            setRpaInfo(data);
            
            // Set TSI, Group, and Vulnerability automatically from the portfolio's actual profile per the user rules
            const newTsi = data.tsi ? (data.tsi * 0.30) : 0;
            setGroup(data.group || "1B");
            setParams(prev => ({ ...prev, 
                a_coeff: data.a_coeff, 
                total_value: newTsi,
                degree: data.vulnerability || "III"
            }));
        } catch (err) { console.error(err); }
    };

    const handleWilayaChange = (w: string) => {
        setSelectedWilaya(w);
        const list = hierarchy[w] || [];
        if (list.length > 0) {
            setSelectedCommune(list[0]);
        }
    };

    const runSimulation = async () => {
        setLoading(true);
        setSimProgress(0);
        
        // Visual progress simulation
        const interval = setInterval(() => {
            setSimProgress(prev => Math.min(prev + 15, 90));
        }, 300);

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/simulation/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...params, commune: selectedCommune })
            });
            const data = await response.json();
            setSimProgress(100);
            setTimeout(() => setResults(data), 500);
        } catch (error) {
            console.error("Simulation failed:", error);
        } finally {
            clearInterval(interval);
            setTimeout(() => setLoading(false), 800);
        }
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat('en-US', { 
            maximumFractionDigits: 0 
        }).format(val) + ' DZA';
    };

    const wilayas = Object.keys(hierarchy);
    const communes = (selectedWilaya && hierarchy[selectedWilaya]) ? hierarchy[selectedWilaya] : [];

    const histData = results?.distribution?.histogram?.map((val: number, i: number) => ({
        range: `${~~(results.distribution.labels[i] / 1000000)}M`,
        count: val
    })) || [];

    const curveData = results?.ep_curve?.return_periods?.map((rp: number, i: number) => ({
        name: `1/${rp}y`,
        gross: results.ep_curve.gross[i],
        net: results.ep_curve.net[i],
    })) || [];

    const getZoneColor = (zone: string) => {
        if (zone === 'III') return '#ef4444'; 
        if (zone.startsWith('II')) return '#f97316'; 
        if (zone === 'I') return '#eab308'; 
        return '#94a3b8';
    };
    const getRiskStatus = () => {
        if (!results || !rpaInfo.premium) return { label: 'PENDING', color: '#94a3b8', raw: 0 };
        const premiumBuffer = rpaInfo.premium * 0.3; // The 30% benchmark
        const pml = results.kpis.pml_95_gross;
        const ratio = (pml / premiumBuffer) * 100;
        
        // If PML exceeds the 30% prime buffer, it's High Risk
        if (ratio >= 100) return { label: 'HIGH RISK', color: '#ef4444', raw: ratio };
        
        // Otherwise, split the safety margin into zones
        if (ratio > 70) return { label: 'MEDIUM RISK', color: '#f59e0b', raw: ratio };
        if (ratio > 30) return { label: 'LOW RISK', color: '#3b82f6', raw: ratio };
        return { label: 'SAFE', color: '#10b981', raw: ratio };
    };

    const risk = getRiskStatus();

    return (
        <div className="pure-sim-container animate-fade-in">
            <header className="sim-header-v4">
                <div className="hero-text">
                    <motion.h1 
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        Risk Simulation Center
                    </motion.h1>
                    <p>Advanced Monte Carlo Engine for RPA 99/2003 Compliance</p>
                </div>
                <div className="header-actions" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <motion.div 
                        className="rpa-badge" 
                        style={{ borderColor: getZoneColor(rpaInfo.zone), color: getZoneColor(rpaInfo.zone) }}
                        animate={{ scale: [1, 1.05, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <Shield size={18} /> Official Zone: {rpaInfo.zone}
                    </motion.div>
                </div>
            </header>

            <div className="sim-grid">
                <aside className="sim-inputs-card">
                    <div className="card-header">
                        <Calculator size={24} className="text-primary" style={{ color: 'var(--primary)' }} />
                        <h3>Simulation Parameters</h3>
                    </div>
                    
                    <div className="input-group">
                        <label><Globe size={14} /> Regional Wilaya</label>
                        <select value={selectedWilaya} onChange={(e) => handleWilayaChange(e.target.value)}>
                            {wilayas.map(w => <option key={w} value={w}>{w}</option>)}
                        </select>
                    </div>

                    <div className="input-group">
                        <label><MapPin size={14} /> District Commune</label>
                        <select value={selectedCommune} onChange={(e) => setSelectedCommune(e.target.value)}>
                            {communes.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>

                    <div className="input-group">
                        <label><Building2 size={14} /> Commune Seismic Group</label>
                        <select value={rpaInfo.zone} disabled style={{ opacity: 0.8, cursor: 'not-allowed', backgroundColor: 'rgba(255,255,255,0.05)' }}>
                            <option value="0">Zone 0 (Négligeable)</option>
                            <option value="I">Groupe Sismique I</option>
                            <option value="IIa">Groupe Sismique IIa</option>
                            <option value="IIb">Groupe Sismique IIb</option>
                            <option value="III">Groupe Sismique III</option>
                        </select>
                    </div>

                    <div className="highlight-input">
                        <div className="input-group">
                            <label>Design Acceleration (A)</label>
                            <input 
                                type="number" step="0.01" readOnly
                                className="readonly-input"
                                value={params.a_coeff} 
                            />
                            <span className="input-hint" style={{ fontSize: '11px', color: '#64748b', display: 'block', marginTop: '8px', textAlign: 'center' }}>
                                Dynamic lookup based on DTR B C 2-48
                            </span>
                        </div>
                    </div>

                    <div className="input-group" style={{ marginTop: '1.5rem' }}>
                        <label>Total Sum Insured (TSI - 30% Portfolio Base)</label>
                        <input 
                            type="text" 
                            className="readonly-input"
                            readOnly
                            style={{ opacity: 0.8, cursor: 'not-allowed', backgroundColor: 'rgba(255,255,255,0.05)' }}
                            value={formatCurrency(params.total_value)} 
                        />
                    </div>

                    <div className="input-group">
                        <label><Layers size={14} /> Vulnerability Class</label>
                        <select value={params.degree} disabled style={{ opacity: 0.8, cursor: 'not-allowed', backgroundColor: 'rgba(255,255,255,0.05)' }}>
                            <option value="I">Class I (RC Wall System)</option>
                            <option value="II">Class II (Moment Resisting Frame)</option>
                            <option value="III">Class III (Unreinforced Masonry)</option>
                        </select>
                    </div>

                    <div className="input-group">
                        <label><Percent size={14} /> Financial Retention</label>
                        <div className="range-box">
                            <input 
                                type="range" min="0" max="1" step="0.05"
                                value={params.retention} 
                                onChange={(e) => setParams({...params, retention: parseFloat(e.target.value)})}
                            />
                            <span>{(params.retention * 100).toFixed(0)}%</span>
                        </div>
                    </div>

                    <button 
                        className={`sim-run-btn ${loading ? 'loading' : ''}`}
                        onClick={runSimulation}
                        disabled={loading}
                    >
                        {loading ? (
                            <Activity className="spin" size={20} />
                        ) : (
                            <Zap size={20} fill="#fff" />
                        )}
                        {loading ? `Simulating ${simProgress}%` : 'Execute Monte Carlo'}
                    </button>
                    {loading && (
                        <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '10px' }}>
                             <motion.div 
                                style={{ height: '100%', background: 'var(--primary)', borderRadius: '2px' }}
                                initial={{ width: 0 }}
                                animate={{ width: `${simProgress}%` }}
                             />
                        </div>
                    )}
                </aside>

                <main className="sim-outputs">
                    <AnimatePresence mode="wait">
                    {!results ? (
                        <motion.div 
                            key="empty"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="empty-results"
                        >
                            <div className="rpa-scan-animation">
                                <Shield size={80} className="pulse-icon" />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#fff' }}>Simulation Node Ready</h3>
                            <p style={{ maxWidth: '400px' }}>
                                Parameters loaded from the official 58 wilayas registry. 
                                Execute calculation to generate AAL and PML metrics.
                            </p>
                        </motion.div>
                    ) : (
                        <motion.div 
                            key="results"
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="results-wrapper"
                        >
                            <div className="kpi-grid">
                                <div className="kpi-card highlight">
                                    <span className="label">Average Annual Loss (AAL)</span>
                                    <h2>{formatCurrency(results.kpis.aal_gross)}</h2>
                                    <div className="net-sub" style={{ color: 'var(--primary)', fontWeight: 600 }}>
                                        Net: {formatCurrency(results.kpis.aal_net)}
                                    </div>
                                </div>
                                <div className="kpi-card highlight">
                                    <span className="label">PML (95% Confidence)</span>
                                    <h2>{formatCurrency(results.kpis.pml_95_gross)}</h2>
                                    <div className="perc-sub" style={{ color: '#94a3b8' }}>Probable Maximum Loss</div>
                                </div>
                                <div className="kpi-card success">
                                    <span className="label">Max Scenario Impact</span>
                                    <h2 style={{ color: 'var(--accent)' }}>{formatCurrency(results.kpis.max)}</h2>
                                    <div className="std-sub" style={{ color: '#475569' }}>
                                        Std Dev: {formatCurrency(results.kpis.std)}
                                    </div>
                                </div>
                                <div className="kpi-card" style={{ borderLeft: `4px solid ${risk.color}`, background: 'rgba(0,0,0,0.2)' }}>
                                    <span className="label">Commune Risk Alert (30% Prime)</span>
                                    <h2 style={{ color: risk.color }}>{risk.label}</h2>
                                    <div className="risk-perc" style={{ fontSize: '12px', marginTop: '4px' }}>
                                        Exposure: <span style={{ fontWeight: 700 }}>{risk.raw.toFixed(1)}%</span> of Buffer
                                    </div>
                                </div>
                            </div>

                            <div className="main-chart-area">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                    <h4>Loss Outcome Distribution (10k Iterations)</h4>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                         <button className="icon-btn"><RefreshCw size={14} /></button>
                                         <button className="icon-btn"><Download size={14} /></button>
                                    </div>
                                </div>
                                <ResponsiveContainer width="100%" height={350}>
                                    <BarChart data={histData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                        <defs>
                                            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="var(--primary)" stopOpacity={1}/>
                                                <stop offset="100%" stopColor="var(--secondary)" stopOpacity={0.6}/>
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                                        <XAxis dataKey="range" fontSize={11} stroke="#64748b" axisLine={false} tickLine={false} />
                                        <YAxis fontSize={11} stroke="#64748b" axisLine={false} tickLine={false} />
                                        <Tooltip 
                                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                            contentStyle={{ 
                                                background: 'rgba(15, 23, 42, 0.9)', 
                                                border: '1px solid rgba(255,255,255,0.1)', 
                                                borderRadius: '16px',
                                                backdropFilter: 'blur(8px)',
                                                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
                                            }}
                                        />
                                        <Bar dataKey="count" fill="url(#barGradient)" radius={[8, 8, 0, 0]}>
                                            {histData.map((entry: any, index: number) => (
                                                <Cell key={`cell-${index}`} fillOpacity={0.8 + (index/histData.length) * 0.2} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>

                            <div className="secondary-grid">
                                <div className="chart-box">
                                    <h4 style={{ marginBottom: '1.5rem', color: '#94a3b8' }}>Exceedance Probability Curve</h4>
                                    <ResponsiveContainer width="100%" height={260}>
                                        <AreaChart data={curveData}>
                                            <defs>
                                                <linearGradient id="colorGross" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
                                                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                                            <XAxis dataKey="name" fontSize={11} stroke="#64748b" axisLine={false} tickLine={false} />
                                            <YAxis fontSize={11} stroke="#64748b" tickFormatter={(v) => `${v/1000000}M`} axisLine={false} tickLine={false} />
                                            <Tooltip />
                                            <Area type="monotone" dataKey="gross" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorGross)" />
                                            <Area type="monotone" dataKey="net" stroke="var(--accent)" strokeWidth={2} fill="transparent" strokeDasharray="5 5" />
                                            <Legend verticalAlign="top" align="right" height={36}/>
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>

                                <div className="stats-box">
                                    <h4 style={{ marginBottom: '1.5rem', color: '#94a3b8' }}>Detailed Loss Metrics</h4>
                                    <div className="stat-row">
                                        <span>P10 (Standard Year)</span>
                                        <strong>{formatCurrency(results.kpis.p10)}</strong>
                                    </div>
                                    <div className="stat-row">
                                        <span>P50 (Median Case)</span>
                                        <strong>{formatCurrency(results.kpis.p50)}</strong>
                                    </div>
                                    <div className="stat-row">
                                        <span>P90 (Systemic Stress)</span>
                                        <strong>{formatCurrency(results.kpis.p90)}</strong>
                                    </div>
                                    <div className="stat-row highlight">
                                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                                            <span style={{ color: 'var(--primary)', fontWeight: 700 }}>95% CVaR</span>
                                            <small style={{ fontSize: '10px', color: '#64748b' }}>Conditional Value at Risk</small>
                                        </div>
                                        <strong>{formatCurrency(results.kpis.pml_95_gross)}</strong>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                    </AnimatePresence>
                </main>
            </div>
        </div>
    );
};

export default RiskSimulationPage;
