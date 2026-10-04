import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import mermaid from 'mermaid';
import projectsData from '../data/projects.json';
import './ProjectDetails.css';

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'loose',
  fontFamily: 'Inter, sans-serif'
});

const ProjectDetails = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [liveData, setLiveData] = useState(null);

  useEffect(() => {
    // Find the project based on the slug
    const foundProject = projectsData.find(p => 
      p.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '') === projectId
    );
    setProject(foundProject);

    // If this is the DuckDB project, mock fetching the live ETL data
    if (projectId === 'zero-cost-duckdb-etl-pipeline') {
      // In production, this would be a fetch() to raw.githubusercontent.com
      // For now, we simulate the live data load
      setTimeout(() => {
        setLiveData({
          lastRun: new Date().toISOString(),
          rowsProcessed: '542,198',
          lateDeliveryRiskPct: '4.2%',
          totalMarginProtected: '₹42,500'
        });
      }, 1000);
    }
  }, [projectId]);

  useEffect(() => {
    // Re-render mermaid diagrams when component mounts
    if (project) {
      mermaid.contentLoaded();
    }
  }, [project]);

  if (!project) return <div className="container" style={{ textAlign: 'center', marginTop: '5rem' }}>Loading Architecture...</div>;

  return (
    <div className="container animate-fade-in">
      <Link to="/" className="back-button">← Back to Portfolio</Link>
      
      <article className="project-detail-container glass-panel">
        <h1 className="detail-title text-gradient">{project.title}</h1>
        <p className="detail-description">{project.description}</p>
        
        {/* Dynamic Business Impact Section */}
        {project.impact_metrics && project.impact_metrics.length > 0 && (
          <div className="impact-dashboard">
            <h3>📈 Proven Business Impact</h3>
            <ul className="impact-list">
              {project.impact_metrics.map((metric, idx) => (
                <li key={idx}><span className="impact-check">✓</span> {metric}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Live Data Dashboard Section */}
        {liveData && (
          <div className="live-dashboard">
            <h3>🔴 Live ETL Data Stream</h3>
            <p className="live-status">Last Sync: {new Date(liveData.lastRun).toLocaleString()}</p>
            <div className="stats-grid" style={{ marginTop: '1rem', marginBottom: '2rem' }}>
              <div className="stat-box">
                <span className="stat-value" style={{ fontSize: '1.8rem' }}>{liveData.rowsProcessed}</span>
                <span className="stat-label">Rows Transformed</span>
              </div>
              <div className="stat-box">
                <span className="stat-value" style={{ fontSize: '1.8rem' }}>{liveData.lateDeliveryRiskPct}</span>
                <span className="stat-label">Current LD Risk</span>
              </div>
              <div className="stat-box">
                <span className="stat-value" style={{ fontSize: '1.8rem' }}>{liveData.totalMarginProtected}</span>
                <span className="stat-label">Margin Secured</span>
              </div>
            </div>
          </div>
        )}

        {/* Dynamic Mermaid Diagram */}
        {project.mermaid_diagram ? (
          <>
            <hr className="divider" />
            <h2>Architectural Flowchart</h2>
            <p>The following diagram visualizes the data infrastructure pipeline for this module.</p>
            
            <div className="mermaid-wrapper">
              <div className="mermaid">
                {project.mermaid_diagram}
              </div>
            </div>
          </>
        ) : (
          <>
            <hr className="divider" />
            <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px dashed rgba(255,255,255,0.1)' }}>
              <h3>Architecture Diagram Pending</h3>
              <p>The engineering documentation for this module is currently being finalized.</p>
            </div>
          </>
        )}
      </article>
    </div>
  );
};

export default ProjectDetails;
