import React from 'react';
import MapRiskVisualizer from '../components/MapRiskVisualizer';
import './MapPage.css';

const MapPage: React.FC = () => {
  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Geo-Seismic Map Platform</h1>
        <p className="page-subtitle">RPA 99/2003 Regulatory Zoning & Asset Exposure Analysis</p>
      </div>

      <MapRiskVisualizer />
    </div>
  );
};

export default MapPage;

