import React from 'react';
import { Calculator, Table, Shield, AlertCircle, Info, Layers } from 'lucide-react';
import NewClientAnalyzer from '../components/NewClientAnalyzer';
import './AnalyticalEnginePage.css';

// --- OFFICIAL REGULATORY DATA (RPA 99/2003) ---
const RPA_COEFFICIENTS = [
  { zone: 'I', low: '0.12', standard: '0.15', high: '0.20', strategic: '0.25' },
  { zone: 'IIa', low: '0.20', standard: '0.25', high: '0.30', strategic: '0.35' },
  { zone: 'IIb', low: '0.25', standard: '0.30', high: '0.40', strategic: '0.45' },
  { zone: 'III', low: '0.35', standard: '0.40', high: '0.50', strategic: '0.55' },
];

const HEIGHT_CONSTRAINTS = [
  { zone: 'I', max_floors: 5, risk: 'Low' },
  { zone: 'IIa', max_floors: 4, risk: 'Moderate' },
  { zone: 'IIb', max_floors: 4, risk: 'High' },
  { zone: 'III', max_floors: 3, risk: 'Critical' },
];

const AnalyticalEnginePage: React.FC = () => {
  return (
    <div className="page-container animate-fade-in">
      <div className="engine-header">
        <div>
           <h1 className="page-title">GAM Technical Regulatory Engine</h1>
          <p className="page-subtitle">Official RPA 99/2003 Calculation Logic & Technical Tables</p>
        </div>
        <div className="engine-status glass-panel technical-status">
          <Shield size={16} />
          <span className="status-text">Regulatory Compliance Mode</span>
        </div>
      </div>

      <div className="engine-grid">
        
        {/* Table 4.1: Coefficients de zone (A) */}
        <div className="glass-panel engine-card rpa-matrix-card">
          <div className="card-header">
            <h2 className="card-title"><Table size={20} /> RPA Table 4.1: Acceleration (A)</h2>
            <button className="icon-btn"><Info size={16} /></button>
          </div>
          <p className="card-desc">Coefficient d'accélération de zone (A) according to building importance groups.</p>
          
          <div className="table-responsive">
            <table className="regulatory-table">
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Group 3 (Limited)</th>
                  <th>Group 2 (Standard)</th>
                  <th>Group 1B (High)</th>
                  <th>Group 1A (Strategic)</th>
                </tr>
              </thead>
              <tbody>
                {RPA_COEFFICIENTS.map((row) => (
                  <tr key={row.zone}>
                    <td className="zone-cell">Zone {row.zone}</td>
                    <td>{row.low}</td>
                    <td>{row.standard}</td>
                    <td>{row.high}</td>
                    <td className="strategic-cell">{row.strategic}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Global Technical Equation */}
        <div className="glass-panel engine-card equation-card">
          <div className="card-header">
            <h2 className="card-title"><Calculator size={20} /> Risk Assessment Equation</h2>
            <span className="ai-badge">Pure Technical Logic</span>
          </div>
          
          <div className="equation-visualizer">
            <div className="main-formula">
              Risk Score = <span className="term-a">(A × V / 0.65)</span> × <span className="term-y">Yf</span> × <span className="term-f">Fp</span>
            </div>
            
            <div className="formula-legend">
              <div className="legend-item">
                <span className="dot dot-a"></span>
                <strong>A:</strong> Acceleration Coeff (RPA Table 4.1)
              </div>
              <div className="legend-item">
                <span className="dot dot-v"></span>
                <strong>V:</strong> Vulnerability Factor (Residential: 1.0, Industrial: 1.3)
              </div>
              <div className="legend-item">
                <span className="dot dot-y"></span>
                <strong>Yf:</strong> Year Factor (Penalty for structures &gt; 22 years)
              </div>
              <div className="legend-item">
                <span className="dot dot-f"></span>
                <strong>Fp:</strong> Floor Penalty (1.5x Multiplier if height limit exceeded)
              </div>
            </div>
          </div>
        </div>

        {/* Constraint Matrix */}
        <div className="glass-panel engine-card constraint-card">
          <div className="card-header">
            <h2 className="card-title"><Layers size={20} /> Structural Constraints</h2>
          </div>
          
          <div className="constraint-grid">
            {HEIGHT_CONSTRAINTS.map((item) => (
              <div key={item.zone} className="constraint-item">
                <div className="constraint-zone">Zone {item.zone}</div>
                <div className="constraint-val">{item.max_floors} Levels</div>
                <div className={`constraint-risk risk-${item.risk.toLowerCase()}`}>
                  {item.risk} Exposure
                </div>
              </div>
            ))}
          </div>
          <div className="constraint-footer">
            <AlertCircle size={14} />
            <span>Enforcing <strong>RPA Chapter 9</strong> structural limitations.</span>
          </div>
        </div>

        {/* New Client CatBoost Analyzer Form (Calculation Ground) */}
        <div className="glass-panel engine-card analyzer-card">
          <div className="card-header">
             <h2 className="card-title">Regulatory Proving Ground</h2>
             <span className="ai-badge">Verified Formula</span>
          </div>
          <NewClientAnalyzer />
        </div>

      </div>
    </div>
  );
};

export default AnalyticalEnginePage;
