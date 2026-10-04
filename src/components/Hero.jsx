import React from 'react';
import './Hero.css';

const Hero = () => {
  return (
    <section className="hero-container animate-fade-in">
      <div className="hero-content">
        <h1 className="hero-title">
          <span className="text-gradient">AI-Augmented</span> Data Infrastructure Consultant
        </h1>
        <p className="hero-subtitle">
          Bridging the gap between legacy manufacturing processes and modern, automated data accountability.
          I architect end-to-end ERP modules, AI API gateways, and automated ETL pipelines that hold operations accountable and protect financial margins.
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-value">₹50k/wk</span>
          <span className="stat-label">LD Penalty Protected</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">10-30%</span>
          <span className="stat-label">Margin Secured</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">150k+</span>
          <span className="stat-label">Monthly Units Tracked</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">10M+</span>
          <span className="stat-label">Rows Processed/Mo</span>
        </div>
      </div>
    </section>
  );
};

export default Hero;
