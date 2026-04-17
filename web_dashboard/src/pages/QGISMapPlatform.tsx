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
  
  // Layer visibility state
  const [showZones, setShowZones] = useState(true);
  const [showLocations, setShowLocations] = useState(true);
  const [selectedFeature, setSelectedFeature] = useState<any>(null);

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
              <span>Layer Control</span>
            </div>
            <div className="layer-list">
              <div className={`layer-item ${showZones ? 'active' : ''}`}>
                <input 
                  type="checkbox" 
                  checked={showZones} 
                  onChange={() => setShowZones(!showZones)} 
                  id="layer-zones"
                />
                <label htmlFor="layer-zones">Seismic Zones (RPA 99/2003)</label>
              </div>
              <div className={`layer-item ${showLocations ? 'active' : ''}`}>
                <input 
                  type="checkbox" 
                  checked={showLocations} 
                  onChange={() => setShowLocations(!showLocations)} 
                  id="layer-locs"
                />
                <label htmlFor="layer-locs">Portfolio Concentration</label>
              </div>
            </div>
          </div>

          {/* DYNAMIC INTELLIGENCE SYSTEM - DRIVEN BY GEOJSON ONLY */}
          <div className="panel-section intelligence-section">
            <div className="section-title">
              <Activity size={14} />
              <span>Intelligence: {
                (showZones && showLocations) ? "Portfolio Exposure" :
                (showZones) ? "Seismic Inventory" :
                (showLocations) ? "Asset Density" : "System Idle"
              }</span>
            </div>
            
            <div className="intelligence-content animate-fade-in">
              {showZones && showLocations && geoStats ? (
                <div className="insight-card exposure-mode">
                  <div className="insight-header">
                    <AlertTriangle size={16} className="text-red-500" />
                    <span>Portfolio Distribution</span>
                  </div>
                  <div className="multi-risk-bars">
                    {[
                      { id: 'III', label: 'Critical (Zone III)', color: 'danger', val: geoStats.exposure_breakdown?.III },
                      { id: 'II', label: 'Severe (Zone II)', color: 'warning', val: geoStats.exposure_breakdown?.II },
                      { id: 'I', label: 'Moderate (Zone I)', color: 'safe', val: geoStats.exposure_breakdown?.I },
                      { id: '0', label: 'Low (Zone 0)', color: 'neutral', val: geoStats.exposure_breakdown?.['0'] }
                    ].map(zone => (
                      <div className="risk-bar-container mini" key={zone.id}>
                        <div className="risk-bar-label">
                          <span>{zone.label}</span>
                          <strong>{zone.val?.toLocaleString()}</strong>
                        </div>
                        <div className="risk-bar-track">
                          <div 
                            className={`risk-bar-fill ${zone.color}`} 
                            style={{ width: `${(zone.val / geoStats.total_policies) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="insight-note">Geospatial analysis of {geoStats.total_policies?.toLocaleString()} Assets.</p>
                </div>

              ) : showZones && geoStats ? (
                <div className="insight-card regulatory-mode">
                  <div className="insight-header">
                    <Shield size={16} className="text-green-500" />
                    <span>RPA Regulation Overlap</span>
                  </div>
                  <div className="zone-summary">
                    <div className="summary-item">
                      <span>RPA Classified Wilayas</span>
                      <strong>{geoStats.total_zones}</strong>
                    </div>
                    <div className="map-legend-box">
                      <div className="legend-row">
                        <span className="legend-dot z-3"></span>
                        <span>Zone III: {geoStats.by_zone?.III} wilayas</span>
                      </div>
                      <div className="legend-row">
                        <span className="legend-dot z-2"></span>
                        <span>Zone II: {geoStats.by_zone?.II} wilayas</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : showLocations && geoStats ? (
                <div className="insight-card density-mode">
                  <div className="insight-header">
                    <Database size={16} className="text-blue-500" />
                    <span>Distribution Analytics</span>
                  </div>
                  <div className="density-stats">
                    <div className="stat-pill">
                      <span className="label">Geo-Located Assets</span>
                      <span className="value">{geoStats.total_policies?.toLocaleString()}</span>
                    </div>
                    <p className="insight-note">Analysis based on current Clipped.geojson package.</p>
                  </div>
                </div>
              ) : (
                <div className="sidebar-empty-state">
                  <Layers size={24} strokeWidth={1} />
                  <p>Initialize geospatial analysis by selecting map layers.</p>
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
            <div className="info-icon-box"><Info size={14} /></div>
            <p>Pure GIS Analysis - No Database Dependencies.</p>
          </div>
        </aside>

        <main className="map-engine-wrap">
          <div className="map-search-overlay">
            <Search size={16} />
            <input type="text" placeholder="Locate Wilaya or Asset..." />
          </div>
          
          <div className="map-inner-host">
            <MapRiskVisualizer 
              showZones={showZones}
              showLocations={showLocations}
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
