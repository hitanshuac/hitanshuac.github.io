import React from 'react';
import { Link } from 'react-router-dom';
import projectsData from '../data/projects.json';
import './ProjectGrid.css';

const ProjectGrid = () => {
  return (
    <section className="projects-container">
      <h2 className="section-title">My Project Ecosystem</h2>
      <div className="project-grid">
        {projectsData.map((project, index) => {
          // Create a URL-friendly slug from the title
          const slug = project.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '');
          
          return (
            <Link to={`/project/${slug}`} key={index} style={{ textDecoration: 'none' }}>
              <div className="project-card glass-panel animate-fade-in" style={{ animationDelay: `${index * 0.05}s` }}>
                <h4 className="project-title">{project.title}</h4>
                <p className="project-description">{project.description}</p>
                <div className="view-details">View Architecture →</div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
};

export default ProjectGrid;
