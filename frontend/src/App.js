// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Login from '../../InsurTech/frontend/src/components/Login';
import Signup from '../../InsurTech/frontend/src/components/Signup';
import Dashboard from '../../InsurTech/frontend/src/components/Dashboard';
import KYC from '../../InsurTech/frontend/src/components/KYC';
import PolicyDetailDashboard from '../../InsurTech/frontend/src/components/PolicyDetailDashboard';
import './styles/LoginSignup.css';
import '../../InsurTech/frontend/src/components/KYC.css';

function App() {
  return (
    <Router>
      <div>
        <nav className="nav-bar">
          <Link to="/" className="nav-link">Login</Link>
          <Link to="/signup" className="nav-link">Signup</Link>
          <Link to="/dashboard" className="nav-link">Dashboard</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/kyc" element={<KYC />} />
          <Route path="/policy/:policyName" element={<PolicyDetailDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
