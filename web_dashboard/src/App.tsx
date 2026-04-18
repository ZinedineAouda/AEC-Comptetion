import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import QGISMapPlatform from './pages/QGISMapPlatform';
import AnalyticalEnginePage from './pages/AnalyticalEnginePage';
import MyDatabasePage from './pages/MyDatabasePage';
import RiskSimulationPage from './pages/RiskSimulationPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Navigate to="/map" replace />} />
          <Route path="map" element={<QGISMapPlatform />} />
          <Route path="analytics" element={<AnalyticalEnginePage />} />
          <Route path="simulation" element={<RiskSimulationPage />} />
          <Route path="database" element={<MyDatabasePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
