// src/components/PolicyDetailDashboard.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './PolicyDetailDashboard.css';

function PolicyDetailDashboard({ policy, companies }) {
  const navigate = useNavigate();
  const handleCompanyClick = (company) => {
    navigate('/kyc', { state: { company } });
  };

  return (
    <div className="policy-detail-dashboard">
      <div className="main-company-card">
        <h3>{policy.mainCompany}</h3>
        <div className="main-button-container">
          <button className="main-button" onClick={() => handleCompanyClick(policy.mainCompany)}>Select</button>
        </div>
      </div>
      <div className="other-companies">
        {companies.map((company, index) => (
          <div key={index} className="company-card">
            <h4>{company.name}</h4>
            <button className="company-button" onClick={() => handleCompanyClick(company.name)}>Select</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PolicyDetailDashboard;
