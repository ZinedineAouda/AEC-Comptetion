import React, { useState, useEffect } from 'react';
import { 
  Shield, Layers, Maximize2, Minimize2, 
  Search, Info, AlertTriangle, Activity, Database,
  TrendingDown, TrendingUp, Globe, MapPin, ShieldCheck
} from 'lucide-react';

import MapRiskVisualizer from '../components/MapRiskVisualizer';
import './QGISMapPlatform.css';

const QGISMapPlatform: React.FC = () => {
  const [geoStats, setGeoStats] = useState<any>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Dynamic Layer Registry
  const [layers, setLayers] = useState<any[]>([]);
  const [activeLayerId, setActiveLayerId] = useState<string | null>(null);
  
  const [selectedFeature, setSelectedFeature] = useState<any>(null);
  const [aiIntel, setAiIntel] = useState<any>(null);
  const [modelR2, setModelR2] = useState<number | null>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const [intelRes, r2Res, layersRes] = await Promise.all([
          fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/geo/intelligence`),
          fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/model/r2`),
          fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/geo/layers`)
        ]);
        const intelData = await intelRes.json();
        const r2Data = await r2Res.json();
        const layersData = await layersRes.json();
        
        setAiIntel(intelData);
        setModelR2(r2Data.r2);
        setLayers(layersData);
        // Default to the first layer for initial view
        if (layersData.length > 0) setActiveLayerId(layersData[0].id);
      } catch (err) {
        console.error("Discovery fetch failed", err);
      }
    };
    fetchConfig();
  }, []);

  const toggleLayer = (id: string) => {
    setActiveLayerId(id);
  };

  const isLayerActive = (id: string) => activeLayerId === id;


  return (
    <div className={`qgis-platform ${isFullscreen ? 'fullscreen' : ''}`}>
      <header className="platform-header">
        <div className="platform-brand">
          <div className="logo-box">
            <img src="/logo.png" alt="GAM" className="header-logo" />
          </div>
          <div>
            <h1>GAM Risk Intelligence</h1>
            <p>Seismic Vulnerability & Exposure Mapper</p>
          </div>
        </div>

        <div className="platform-metrics">
          <div className="metric-item">
            <Database size={14} className="metric-icon" />
            <div className="metric-content">
              <span className="metric-label">Geo-Collection</span>
              <span className="metric-value">{geoStats?.total_policies?.toLocaleString() || '...'} Assets</span>
            </div>
          </div>
          <div className="metric-divider" />
          <div className="metric-item">
            <Activity size={14} className="metric-icon-accent" />
            <div className="metric-content">
              <span className="metric-label">Regulatory Mesh</span>
              <span className="metric-value">{geoStats?.total_zones || '0'} Regions</span>
            </div>
          </div>
        </div>

        <div className="platform-actions">
          <button 
            className="action-btn" 
            onClick={() => setIsFullscreen(!isFullscreen)}
            title="Toggle Fullscreen"
          >
            {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
          </button>
        </div>
      </header>

      <div className="platform-viewport">
        <aside className="control-panel">
          <div className="panel-section">
            <div className="section-title">
              <Layers size={14} />
              <span>Layer Registry</span>
            </div>
            <div className="layer-list">
              {layers.map(layer => (
                <div 
                  className={`layer-item ${isLayerActive(layer.id) ? 'active' : ''}`} 
                  key={layer.id}
                  onClick={() => toggleLayer(layer.id)}
                >
                  <input 
                    type="radio" 
                    name="layer-selection"
                    checked={isLayerActive(layer.id)} 
                    onChange={() => {}} // Controlled via parent div onClick
                    id={`layer-${layer.id}`}
                  />
                  <label htmlFor={`layer-${layer.id}`}>{layer.name}</label>
                </div>
              ))}
              {layers.length === 0 && <p className="text-xs text-muted-sm">Discovering layers...</p>}
            </div>
          </div>

            <div className="panel-section intelligence-section">
            <div className="section-title">
              <Activity size={14} />
              <span>AI Intelligence: {
                activeLayerId ? "Autonomous Perspective" : "System Idle"
              }</span>
            </div>
            
            <div className="intelligence-content animate-fade-in">
              {activeLayerId && aiIntel ? (
                <div className="insight-card ai-mode animate-fade-in">
                  <div className="insight-header">
                    <ShieldCheck size={16} className="icon-accent" />
                    <span>Cross-Layer Analytics</span>
                  </div>
                  <div className="vulnerability-grid">
                    {aiIntel.vulnerability_scores?.map((vuln: any) => (
                      <div className="vuln-pill" key={vuln.type}>
                        <div className="vuln-type">{vuln.type}</div>
                        <div className={`vuln-score severity-${vuln.severity}`}>{vuln.score}%</div>
                        <div className={`vuln-label severity-${vuln.severity}`}>{vuln.severity.toUpperCase()} RISK</div>
                      </div>
                    ))}
                  </div>

                  <div className="model-confidence-box">
                    <div className="confidence-label">
                      <Activity size={12} />
                      <span>Model Stability Index</span>
                    </div>
                    <div className="confidence-value">{modelR2 ? `${modelR2}%` : 'Calculating...'}</div>
                    <div className="confidence-track">
                      <div className="confidence-fill" style={{ width: `${modelR2 || 0}%` }}></div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="sidebar-empty-state">
                  <Layers size={24} strokeWidth={1} />
                  <p>Initializing AI-Driven Geospatial Intelligence discovery...</p>
                </div>
              )}
            </div>
          </div>

          <div className="panel-section">
            <div className="section-title">
              <Info size={14} />
              <span>{selectedFeature?.is_commune ? "Pinpoint Intelligence" : "Zone Intelligence"}</span>
            </div>
            {selectedFeature ? (
              <div className="selected-feature-card animate-fade-in highlight">
                <small className="feature-label">
                  {selectedFeature.is_commune ? "Specific Commune" : "Active Region"}
                </small>
                <h3 className="feature-name">{selectedFeature.NAME_1 || selectedFeature.NAME || 'Unknown'}</h3>
                <div className="feature-zone">
                  <span className={`zone-pill zone-${selectedFeature.zone_rpa}`}>
                    RPA Zone {selectedFeature.zone_rpa}
                  </span>
                </div>
              </div>
            ) : (

              <div className="sidebar-empty-state">
                <MapPin size={24} strokeWidth={1.5} />
                <p>Hover regions for detailed Wilaya assessment</p>
              </div>
            )}
          </div>

          <div className="panel-info-card">
            <div className="info-icon-box"><ShieldCheck size={14} /></div>
            <p>GAM Engine Internalized - Regulatory Compliance Verified.</p>
          </div>
        </aside>

        <main className="map-engine-wrap">
          <div className="map-inner-host">
            <MapRiskVisualizer 
              activeLayers={layers.filter(l => activeLayerId === l.id)}
              onFeatureSelect={setSelectedFeature}
              onStatsReady={setGeoStats}
            />
          </div>
          <div className="map-coords">
            <span>Projection: EPSG:4326 (WGS 84)</span>
          </div>
        </main>
      </div>
    </div>
  );
};

export default QGISMapPlatform;
