import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { Map, BrainCircuit, ShieldAlert, Settings, BarChart3, Dices } from 'lucide-react';
import './DashboardLayout.css';

const DashboardLayout: React.FC = () => {
  const navItems = [
    { name: 'GIS Platform', path: '/map', icon: <Map size={20} /> },
    { name: 'Analytical Engine', path: '/analytics', icon: <BrainCircuit size={20} /> },
    { name: 'Risk Simulation', path: '/simulation', icon: <Dices size={20} /> },
    { name: 'Portfolio Intel', path: '/database', icon: <BarChart3 size={20} /> },
  ];

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel">
        <div className="sidebar-header">
          <div className="gam-logo-wrap">
            <img src="/logo.png" alt="GAM Assurances" className="gam-logo-img" />
          </div>
          <p className="subtitle">Simulation Engine</p>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'active' : ''}`
              }
            >
              <span className="icon-wrapper">{item.icon}</span>
              <span className="nav-text">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item settings-btn">
             <span className="icon-wrapper"><Settings size={20} /></span>
             <span className="nav-text">Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardLayout;
