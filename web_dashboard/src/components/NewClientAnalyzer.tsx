import React, { useState, useEffect } from 'react';
import { Send, CheckCircle, XCircle, Loader2, MapPin, Activity, Calculator, Info, AlertTriangle } from 'lucide-react';
import './NewClientAnalyzer.css';
import algeriaZoning from '../data/algeria_zoning.json';

interface CatBoostResult {
  status: 'ACCEPTED' | 'DECLINED' | 'ERROR';
  reason: string;
  estimate: number | null;
}

// Define types for zoning data
interface CommuneData {
  name: string;
  zone: string;
}

// Official RPA 99/2003 Table 4.1: Coefficients de zone (A)
const RPA_MATRIX: Record<string, Record<string, number>> = {
  '0':   { '1A': 0.08, '1B': 0.06, '2': 0.04, '3': 0.02 }, // Nominal baseline for Zone 0 (Very Low Risk)
  'I':   { '1A': 0.20, '1B': 0.15, '2': 0.12, '3': 0.07 },
  'IIa': { '1A': 0.30, '1B': 0.25, '2': 0.20, '3': 0.14 },
  'IIb': { '1A': 0.40, '1B': 0.30, '2': 0.25, '3': 0.18 },
  'III': { '1A': 0.50, '1B': 0.40, '2': 0.35, '3': 0.25 }
};

const BUILDING_FACTORS: Record<string, number> = {
  'Commercial': 1.1,  // Usage multiplier
  'Residential': 1.0,
  'Industrial': 1.3
};

// RPA Chapter 9: Table 9.1 - Floor Limits
const RPA_FLOOR_LIMITS: Record<string, number> = {
  'I': 5,
  'IIa': 4,
  'IIb': 4,
  'III': 3
};

const NewClientAnalyzer: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CatBoostResult | null>(null);
  const [showFormula, setShowFormula] = useState(false);
  
  // Get list of Wilayas
  const wilayas = Object.keys(algeriaZoning);
  
  const [selectedWilaya, setSelectedWilaya] = useState(wilayas[0]);
  const [selectedCommune, setSelectedCommune] = useState('');
  
  const [formData, setFormData] = useState({
    property_type: 'Residential',
    zone_rpa: 'I',
    importance_group: '2',
    capital_assure: 10000000,
    construction_year: 2010,
    floors: 1
  });

  // Calculate Technical Scores
  const rpaCoeff = RPA_MATRIX[formData.zone_rpa]?.[formData.importance_group] || 0;
  const buildingFactor = BUILDING_FACTORS[formData.property_type] || 1.0;
  const floorLimit = RPA_FLOOR_LIMITS[formData.zone_rpa] || 99;
  
  // Scoring logic rebuild based on Table 4.1
  // Max possible product is 0.50 (Zone III, Grp 1A) * 1.3 (Industrial) = 0.65
  let baseScore = (rpaCoeff * buildingFactor) / 0.65 * 100;
  
  const yearDiff = Math.max(0, 2025 - formData.construction_year);
  const yearPenalty = yearDiff > 45 ? 1.4 : yearDiff > 22 ? 1.2 : 1.0;
  
  const isOverLimit = formData.floors > floorLimit;
  const floorPenalty = isOverLimit ? 1.5 : 1.0;
  
  const riskScore = Math.min(100, Math.round(baseScore * yearPenalty * floorPenalty));

  // Auto-map Importance Group when Property Type changes
  const handleTypeChange = (type: string) => {
    let group = '2';
    if (type === 'Commercial') group = '3';
    if (type === 'Industrial') group = '1B';
    
    setFormData(prev => ({ 
      ...prev, 
      property_type: type,
      importance_group: group 
    }));
  };

  // Update communes and set default when wilaya changes
  useEffect(() => {
    const communes = algeriaZoning[selectedWilaya as keyof typeof algeriaZoning] || [];
    if (communes.length > 0) {
      setSelectedCommune(communes[0].name);
      setFormData(prev => ({ ...prev, zone_rpa: communes[0].zone }));
    }
  }, [selectedWilaya]);

  // Handle commune change
  const handleCommuneChange = (communeName: string) => {
    setSelectedCommune(communeName);
    const communes = algeriaZoning[selectedWilaya as keyof typeof algeriaZoning] || [];
    const found = communes.find((c: CommuneData) => c.name === communeName);
    if (found) {
      setFormData(prev => ({ ...prev, zone_rpa: found.zone }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/evaluate-client`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          property_type: formData.property_type,
          zone_rpa: formData.zone_rpa,
          importance_group: formData.importance_group,
          capital_assure: Number(formData.capital_assure),
          construction_year: formData.construction_year,
          floors: formData.floors
        })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setResult({ status: 'ERROR', reason: 'Failed to connect to AI Backend. Ensure the FastAPI server is running.', estimate: null });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="new-client-analyzer glass-panel">
      <div className="analyzer-header">
        <div className="title-section">
          <h3 className="analyzer-title">New Client Risk Assessment</h3>
          <span className="analyzer-badge">Live Inference</span>
        </div>
        <button 
          className="info-toggle" 
          onClick={() => setShowFormula(!showFormula)}
          title="Show Calculation Logic"
        >
          <Info size={18} />
        </button>
      </div>

      {showFormula && (
        <div className="formula-overlay animate-slideDown">
          <div className="formula-content">
            <h4><Calculator size={16} /> Technical Risk Equation</h4>
            <p>Risk Score = (A × V / 0.65) × Yf × Fp</p>
            <ul>
              <li><strong>A (RPA Matrix):</strong> Based on Importance Group (Grp1A to Grp3)</li>
              <li><strong>Grp-3:</strong> Commercial (Lowest A = 0.07 – 0.25)</li>
            </ul>
            <div className="rpa-limit-info">
              <span>Full compliance logic for <strong>RPA 99/03 Table 4.1</strong> active.</span>
            </div>
          </div>
        </div>
      )}

      <div className="analyzer-body">
        <form className="analyzer-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Property Category</label>
              <select 
                value={formData.property_type} 
                onChange={e => handleTypeChange(e.target.value)}
              >
                <option value="Residential">Residential</option>
                <option value="Commercial">Commercial (Group 3)</option>
                <option value="Industrial">Industrial (Group 1B)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Importance Group</label>
              <select 
                value={formData.importance_group} 
                onChange={e => setFormData({...formData, importance_group: e.target.value})}
              >
                <option value="1A">Group 1A (Strategic)</option>
                <option value="1B">Group 1B (High)</option>
                <option value="2">Group 2 (Standard)</option>
                <option value="3">Group 3 (Limited)</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Wilaya</label>
              <select 
                value={selectedWilaya} 
                onChange={e => setSelectedWilaya(e.target.value)}
              >
                {wilayas.map(w => (
                  <option key={w} value={w}>{w}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Commune</label>
              <select 
                value={selectedCommune} 
                onChange={e => handleCommuneChange(e.target.value)}
              >
                {(algeriaZoning[selectedWilaya as keyof typeof algeriaZoning] || []).map((c: CommuneData) => (
                  <option key={c.name} value={c.name}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Construction Year</label>
              <input 
                type="number" 
                value={formData.construction_year}
                onChange={e => setFormData({...formData, construction_year: Number(e.target.value)})}
                min="1900" max="2025"
              />
            </div>
            <div className="form-group">
              <label>Number of Floors</label>
              <input 
                type="number" 
                value={formData.floors}
                onChange={e => setFormData({...formData, floors: Number(e.target.value)})}
                min="1"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Capital Assured (DZA)</label>
            <input 
              type="number" 
              value={formData.capital_assure}
              onChange={e => setFormData({...formData, capital_assure: Number(e.target.value)})}
              min="0"
            />
          </div>

          <div className="zone-indicator">
            <div className="zone-info">
              <MapPin size={16} className="pin-icon" />
              <span>Zone {formData.zone_rpa} [A = <strong>{rpaCoeff.toFixed(2)}</strong>]</span>
            </div>
            <div className={`zone-tag zone-${formData.zone_rpa}`}>
              RPA {formData.zone_rpa}
            </div>
          </div>

          <button type="submit" className="analyze-btn" disabled={loading}>
            {loading ? <Loader2 className="spinner" size={20} /> : <Send size={20} />}
            <span>{loading ? 'Analyzing...' : 'Run Analysis'}</span>
          </button>
        </form>

        <div className="analyzer-result-container">
          {!result && !loading && (
            <div className="empty-result">
              <div className="eval-preview">
                <Activity size={40} className="pulse-icon" />
                <p>Select location to calculate vulnerability score.</p>
                <div className="preview-score">
                  <span>Risk Score: <strong>{riskScore}</strong> pts</span>
                </div>
              </div>
            </div>
          )}

          {loading && (
            <div className="loading-result">
              <div className="scan-line"></div>
              <p>Evaluating Risk Profile...</p>
            </div>
          )}

          {result && !loading && (
            <div className="result-stack">
              <div className={`result-card result-${result.status.toLowerCase()}`}>
                <div className="result-header">
                  {result.status === 'ACCEPTED' && <CheckCircle size={28} className="icon-accepted" />}
                  {result.status === 'DECLINED' && <XCircle size={28} className="icon-declined" />}
                  {result.status === 'ERROR' && <XCircle size={28} className="icon-error" />}
                  <h4>{result.status === 'ACCEPTED' ? 'Policy Approved' : result.status === 'DECLINED' ? 'Policy Declined' : 'Connection Error'}</h4>
                </div>
                
                <div className="result-details">
                  <p className="result-reason">{result.reason}</p>
                  
                  {isOverLimit && (
                    <div className="warning-banner animate-pulse">
                      <AlertTriangle size={16} />
                      <span>RPA Warning: Building exceeds max floor limit ({floorLimit}) for Zone {formData.zone_rpa}.</span>
                    </div>
                  )}

                  {result.estimate !== null && (
                    <div className="estimate-box">
                      <span className="estimate-label">Total Net Premium (Estimate)</span>
                      <span className="estimate-val">{result.estimate.toLocaleString('en-US')} DZA</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="technical-card animate-fadeIn">
                <h5>Technical Evaluation</h5>
                <div className="tech-grid">
                  <div className="tech-item">
                    <span>Acceleration (A)</span>
                    <strong>{rpaCoeff}</strong>
                  </div>
                  <div className="tech-item">
                    <span>Group Factor</span>
                    <strong>Grp-{formData.importance_group}</strong>
                  </div>
                  <div className="tech-item highlight">
                    <span>Risk Index</span>
                    <strong>{riskScore}/100</strong>
                  </div>
                </div>
                <div className="score-track">
                  <div 
                    className={`score-bar score-level-${riskScore > 75 ? 'high' : riskScore > 40 ? 'medium' : 'low'}`} 
                    style={{ width: `${riskScore}%` }}
                  ></div>
                </div>
                <div className="feature-small-list">
                  <div className="feature-tag">Year Penalty: x{yearPenalty}</div>
                  <div className="feature-tag">Height Warning: {isOverLimit ? 'YES' : 'NO'}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewClientAnalyzer;
