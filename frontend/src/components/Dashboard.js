import React from 'react';
import './Dashboard.css';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();

  const policies = [
    'Health Insurance',
    'Life Insurance',
    'Home Insurance',
    'Motor Insurance',
    'Travel Insurance',
    'Whole Life Insurance',
    'Group Insurance',
    'Child Plan',
    'Money-back Policy',
    'Critical Illness Cover',
    'Family Floater Insurance',
    'Property Insurance'
  ];

  const handlePolicyClick = (policy) => {
    const companies = [
      { name: 'Company A', description: 'Top rated for Health Insurance.' },
      { name: 'Company B', description: 'Best coverage options.' },
      { name: 'Company C', description: 'Affordable plans.' },
      { name: 'Company D', description: 'Fast claim process.' },
      { name: 'Company E', description: 'Excellent customer service.' },
    ];

    navigate(`/policy/${policy.replace(/\s+/g, '-')}`, { state: { policy, companies } });
  };

  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>
      <div className="dashboard-grid">
        {policies.map((policy, index) => (
          <div key={index} className="dashboard-card" onClick={() => handlePolicyClick(policy)}>
            <div className="card-content">{policy}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
