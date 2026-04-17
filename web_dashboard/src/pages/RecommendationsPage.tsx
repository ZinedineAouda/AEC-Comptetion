import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck } from 'lucide-react';
import './RecommendationsPage.css';

const RecommendationsPage: React.FC = () => {
  const zone3Exposure = 35.4; 
  const zone1Exposure = 4.2;

  const alerts = [];
  if (zone3Exposure > 30) {
    alerts.push({
      id: 1, 
      type: 'critical', 
      icon: <AlertTriangle size={24} />,
      title: 'DANGER: Surconcentration in Zone III',
      desc: `High risk exposure (${zone3Exposure}% of portfolio) identified in heavily seismic zones (Algiers, Chlef, etc). Halt new commercial underwritings or rapidly execute facultative reinsurance treaties.`
    });
  }
  if (zone1Exposure < 10) {
    alerts.push({
      id: 2, 
      type: 'opportunity', 
      icon: <ShieldCheck size={24} />,
      title: 'Sous-concentration in Zone I',
      desc: `Opportunity to balance the portfolio. Risk levels are minimal but market share in Zone I (Laghouat, M'Sila) is only ${zone1Exposure}%. Expand commercial efforts here.`
    });
  }

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">RPA Strategy Engine</h1>
        <p className="page-subtitle">Automated balance recommendations derived from current thresholds</p>
      </div>

      <div className="alerts-container">
        {alerts.map((alert) => (
          <div key={alert.id} className={`alert-card glass-panel alert-${alert.type}`}>
            <div className="alert-header">
              <div className="alert-icon-wrapper">
                {alert.icon}
              </div>
              <h3 className="alert-title">{alert.title}</h3>
            </div>
            <p className="alert-desc">{alert.desc}</p>
            <div className="alert-action">
              <button className={`btn-${alert.type}`}>
                {alert.type === 'critical' ? 'View Hotspots' : 'Explore Markets'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationsPage;
