// src/components/Login.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LoginSignup.css'; // Update the path to the CSS file

function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="form-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input type="email" placeholder="Email" required />
        <input type="password" placeholder="Password" required />
        <button type="submit" className="login-button">Login</button>
      </form>
    </div>
  );
}

export default Login;
