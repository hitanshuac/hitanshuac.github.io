import os
import sys
import json
import re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECTS_ROOT = Path(r'D:\Projects')
IGNORE_DIRS = ['Resume', 'Mermaid', '__pycache__', 'portfolio_projects', 'Mermaid_Flowchart_Extract_Existing_Docs_Interlink', 'hitanshuac-portfolio']

projects = []

def extract_mermaid(content):
    """Extracts the first mermaid code block found in the markdown."""
    match = re.search(r'```mermaid\s+(.*?)\s+```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_impact(content):
    """Extracts bullet points under a Business Impact header."""
    # Look for ## Business Impact or similar, followed by text until the next # or EOF
    match = re.search(r'#+\s*Business\s*Impact\s*(.*?)(?=\n#+ |\Z)', content, re.DOTALL | re.IGNORECASE)
    if match:
        impact_text = match.group(1).strip()
        # Parse out the bullet points
        bullets = [line.strip().lstrip('-*').strip() for line in impact_text.split('\n') if line.strip().startswith(('- ', '* '))]
        return bullets if bullets else [impact_text] # Return raw text if no bullets found
    return None

def extract_description(content):
    """Extracts a short, concise description from the markdown."""
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if (line and not line.startswith('#') and not line.startswith('>') 
            and not line.startswith('<') and not line.startswith('!')
            and not line.startswith('[') and not line.startswith('-')
            and not line.startswith('title:') and not line.startswith('emoji:')
            and not line.startswith('color') and not line.startswith('sdk:')
            and not line.startswith('app_') and not line.startswith('pinned:')
            and not line.startswith('---') and not line.startswith('*')):
            desc = line
            if len(desc) > 150: 
                return desc[:147] + '...'
            return desc
    return "Custom data infrastructure module."

for p in PROJECTS_ROOT.iterdir():
    if p.is_dir() and p.name not in IGNORE_DIRS and not p.name.startswith('.'):
        # Look for the primary documentation files
        doc_files = [p / 'README.md', p / 'context.md', p / 'PROJECT_CONTEXT.md', p / 'fork.md']
        doc_path = next((doc for doc in doc_files if doc.exists()), None)
        
        title = p.name
        desc = 'Custom data infrastructure module.'
        mermaid_diagram = None
        full_text = ""
        
        if doc_path:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract title
                    h1 = re.search(r'^#\s+(.*)', content, re.MULTILINE)
                    if h1: 
                        title = h1.group(1).strip()
                    
                    # Extract description
                    desc = extract_description(content)
                    
                    # Extract Mermaid Diagram
                    mermaid_diagram = extract_mermaid(content)
                    
                    # Extract Business Impact
                    impact_metrics = extract_impact(content)
                    
            except Exception as e:
                print(f"Failed to parse {doc_path}: {e}")
                pass
                
        projects.append({
            'title': title, 
            'description': desc,
            'mermaid_diagram': mermaid_diagram,
            'impact_metrics': impact_metrics
        })

# Manually inject the DuckDB Pipeline since it lives inside the Resume folder
projects.append({
    'title': 'Zero-Cost DuckDB ETL Pipeline',
    'description': 'Automated cloud-native ETL pipeline using DuckDB and GitHub Actions to process 500k+ rows of supply chain data nightly at $0 cost.',
    'impact_metrics': [
        'Eliminated ₹50,000/week in LD Penalties by predicting late deliveries.',
        '100% Cloud Cost Reduction via serverless GitHub Actions and DuckDB architecture.',
        'Processes 542,000+ rows of live operational data every 24 hours.'
    ],
    'mermaid_diagram': """graph TD
        A[Kaggle Supply Chain API] -->|Extract: 500k rows| B(DuckDB In-Memory)
        B -->|SQL Transformation| C{Business Logic}
        C -->|Calculate Profit Margin| D[delivery_metrics.parquet]
        C -->|Calculate LD Risk| E[kpi_summary.parquet]
        D --> F[Live Dashboard API]
        E --> F"""
})

out_dir = Path(__file__).parent.parent / 'src' / 'data'
out_dir.mkdir(parents=True, exist_ok=True)
with open(out_dir / 'projects.json', 'w', encoding='utf-8') as f:
    json.dump(projects, f, indent=2)

print(f'Successfully generated JSON with {len(projects)} projects, including dynamic Mermaid extraction.')
