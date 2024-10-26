// src/components/Signup.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LoginSignup.css'; // Update the path to the CSS file

function Signup() {
  const navigate = useNavigate();

  const handleSignup = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="form-container">
      <h2>Signup</h2>
      <form onSubmit={handleSignup}>
        <input type="text" placeholder="Full Name" required />
        <input type="email" placeholder="Email" required />
        <input type="password" placeholder="Password" required />
        <button type="submit" className="signup-button">Signup</button>
      </form>
    </div>
  );
}

export default Signup;
