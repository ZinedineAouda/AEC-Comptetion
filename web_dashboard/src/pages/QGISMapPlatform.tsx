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
  const [activeLayerIds, setActiveLayerIds] = useState<string[]>([]);
  
  const [selectedFeature, setSelectedFeature] = useState<any>(null);
  const [aiIntel, setAiIntel] = useState<any>(null);
  const [modelR2, setModelR2] = useState<number | null>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const [intelRes, r2Res, layersRes] = await Promise.all([
          fetch('http://localhost:8000/api/geo/intelligence'),
          fetch('http://localhost:8000/api/model/r2'),
          fetch('http://localhost:8000/api/geo/layers')
        ]);
        const intelData = await intelRes.json();
        const r2Data = await r2Res.json();
        const layersData = await layersRes.json();
        
        setAiIntel(intelData);
        setModelR2(r2Data.r2);
        setLayers(layersData);
        // Default to all layers active for initial view
        setActiveLayerIds(layersData.map((l: any) => l.id));
      } catch (err) {
        console.error("Discovery fetch failed", err);
      }
    };
    fetchConfig();
  }, []);

  const toggleLayer = (id: string) => {
    setActiveLayerIds(prev => 
      prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id]
    );
  };

  const isLayerActive = (id: string) => activeLayerIds.includes(id);

  return (
    <div className={`qgis-platform ${isFullscreen ? 'fullscreen' : ''}`}>
      <header className="platform-header">
        <div className="platform-brand">
          <div className="logo-box">
            <Globe className="logo-icon" size={24} />
          </div>
          <div>
            <h1>QGIS Risk Intelligence</h1>
            <p>Algerian Seismic Vulnerability & Exposure Mapper</p>
          </div>
        </div>

        <div className="platform-metrics">
          <div className="metric-item">
            <Database size={14} className="text-blue-400" />
            <div className="metric-content">
              <span className="metric-label">Geo-Collection</span>
              <span className="metric-value">{geoStats?.total_policies?.toLocaleString() || '...'} Assets</span>
            </div>
          </div>
          <div className="metric-divider" />
          <div className="metric-item">
            <Activity size={14} className="text-orange-400" />
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
                <div className={`layer-item ${isLayerActive(layer.id) ? 'active' : ''}`} key={layer.id}>
                  <input 
                    type="checkbox" 
                    checked={isLayerActive(layer.id)} 
                    onChange={() => toggleLayer(layer.id)} 
                    id={`layer-${layer.id}`}
                  />
                  <label htmlFor={`layer-${layer.id}`}>{layer.name}</label>
                </div>
              ))}
              {layers.length === 0 && <p className="text-xs text-slate-500">Discovering layers...</p>}
            </div>
          </div>

          <div className="panel-section intelligence-section">
            <div className="section-title">
              <Activity size={14} />
              <span>AI Intelligence: {
                activeLayerIds.length > 0 ? "Autonomous Perspective" : "System Idle"
              }</span>
            </div>
            
            <div className="intelligence-content animate-fade-in">
              {activeLayerIds.length > 0 && aiIntel ? (
                <div className="insight-card ai-mode animate-fade-in">
                  <div className="insight-header">
                    <ShieldCheck size={16} className="text-blue-500" />
                    <span>Cross-Layer Analytics</span>
                  </div>
                  <div className="vulnerability-grid">
                    {aiIntel.vulnerability_scores?.map((vuln: any) => (
                      <div className="vuln-pill" key={vuln.type}>
                        <div className="vuln-type">{vuln.type}</div>
                        <div className={`vuln-score severity-${vuln.severity}`}>{vuln.score}%</div>
                        <div className="vuln-label">{vuln.severity.toUpperCase()} RISK</div>
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
            <p>AI Engine Internalized - Regulatory Compliance Verified.</p>
          </div>
        </aside>

        <main className="map-engine-wrap">
          <div className="map-search-overlay">
            <Search size={16} />
            <input type="text" placeholder="Locate Wilaya or Asset..." />
          </div>
          
          <div className="map-inner-host">
            <MapRiskVisualizer 
              activeLayers={layers.filter(l => activeLayerIds.includes(l.id))}
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
