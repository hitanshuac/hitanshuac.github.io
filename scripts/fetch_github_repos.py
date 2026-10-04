import os
import sys
import json
import re
import requests

def extract_mermaid(content):
    """Extracts the first mermaid code block found in the markdown."""
    match = re.search(r'```mermaid\s+(.*?)\s+```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_impact(content):
    """Extracts bullet points under a Business Impact header."""
    match = re.search(r'#+\s*Business\s*Impact\s*(.*?)(?=\n#+ |\Z)', content, re.DOTALL | re.IGNORECASE)
    if match:
        impact_text = match.group(1).strip()
        bullets = [line.strip().lstrip('-*').strip() for line in impact_text.split('\n') if line.strip().startswith(('- ', '* '))]
        return bullets if bullets else [impact_text]
    return None

def extract_description(content, repo_description):
    """Extracts a short, concise description from the markdown, or falls back to repo description."""
    if not content:
        return repo_description or "No description available."
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
    return repo_description or "Custom data infrastructure module."

def fetch_repos():
    token = os.environ.get('GH_PAT') or os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GH_PAT or GITHUB_TOKEN environment variable not set.")
        sys.exit(1)
        
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Fetch user repos (this endpoint gets public and private repos for the authenticated user)
    # Using 'user/repos' to get repositories for the authenticated user (which includes private ones if token has repo scope)
    # Affiliation owner ensures we get repos owned by the user.
    repos_url = 'https://api.github.com/user/repos?affiliation=owner&per_page=100'
    repos = []
    
    while repos_url:
        print(f"Fetching {repos_url}...")
        response = requests.get(repos_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch repos: {response.text}")
            sys.exit(1)
        repos.extend(response.json())
        
        # Handle pagination
        if 'next' in response.links:
            repos_url = response.links['next']['url']
        else:
            repos_url = None

    print(f"Found {len(repos)} repositories.")
    return repos, headers

def fetch_readme(repo_full_name, headers):
    readme_url = f'https://api.github.com/repos/{repo_full_name}/readme'
    
    # If we request with Accept: application/vnd.github.v3.raw, the response is the raw file content
    headers_raw = headers.copy()
    headers_raw['Accept'] = 'application/vnd.github.v3.raw'
    
    response = requests.get(readme_url, headers=headers_raw)
    if response.status_code == 200:
        return response.text
    return None

def main():
    repos, headers = fetch_repos()
    projects = []
    
    for repo in repos:
        name = repo['name']
        print(f"Processing {name}...")
        
        readme_content = fetch_readme(repo['full_name'], headers)
        
        desc = extract_description(readme_content, repo.get('description'))
        mermaid_diagram = extract_mermaid(readme_content) if readme_content else None
        impact_metrics = extract_impact(readme_content) if readme_content else None
        
        projects.append({
            'title': name,
            'description': desc,
            'mermaid_diagram': mermaid_diagram,
            'impact_metrics': impact_metrics,
            'url': repo['html_url'],
            'is_private': repo['private'],
            'language': repo['language']
        })
        
    # Inject DuckDB Pipeline manually if desired, or skip if it's already in the repos
    # We'll skip manual injection since this is automated from GitHub now.
    
    # Save to src/data/projects.json
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'projects.json')
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=2)
        
    print(f"Successfully generated JSON with {len(projects)} projects.")

if __name__ == '__main__':
    main()
