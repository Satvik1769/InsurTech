// src/components/KYC.js
import React, { useState } from 'react';
import './KYC.css';

function KYC() {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    // Handle file upload logic here
    console.log('File uploaded:', file);
  };

  return (
    <div className="kyc-container">
      <h2>KYC Verification</h2>
      <form onSubmit={handleSubmit}>
        <div className="file-upload">
          <input type="file" onChange={handleFileChange} accept="image/*, .pdf" />
        </div>
        <button type="submit" className="upload-button">Upload Document</button>
      </form>
    </div>
  );
}

export default KYC;
