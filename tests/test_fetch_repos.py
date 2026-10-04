import pytest
import os
import json
import sys

# Add scripts directory to path to import fetch_github_repos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
import fetch_github_repos

@pytest.fixture
def sample_readme_content():
    return """# Project Name
This is a cool test project.

## Business Impact
- 100% test coverage
- Saved $50,000

## Architecture
```mermaid
graph TD
    A --> B
```
"""

def test_extract_mermaid(sample_readme_content):
    mermaid = fetch_github_repos.extract_mermaid(sample_readme_content)
    assert mermaid is not None
    assert "graph TD" in mermaid
    assert "A --> B" in mermaid

def test_extract_impact(sample_readme_content):
    impact = fetch_github_repos.extract_impact(sample_readme_content)
    assert impact is not None
    assert len(impact) == 2
    assert impact[0] == "100% test coverage"
    assert impact[1] == "Saved $50,000"

def test_extract_description(sample_readme_content):
    desc = fetch_github_repos.extract_description(sample_readme_content, "Fallback")
    assert desc == "This is a cool test project."

def test_extract_description_fallback():
    desc = fetch_github_repos.extract_description("", "Fallback")
    assert desc == "Fallback"

def test_fetch_readme(mocker):
    # Test fetch_readme with a mocked requests.get
    class MockResponse:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text
            
    mocker.patch('requests.get', return_value=MockResponse(200, "Mocked README"))
    content = fetch_github_repos.fetch_readme("user/repo", {'Authorization': 'token test'})
    assert content == "Mocked README"

def test_fetch_repos(mocker):
    # Test fetch_repos
    mocker.patch.dict(os.environ, {'GITHUB_TOKEN': 'mock_token'})
    
    class MockResponse:
        def __init__(self, status_code, json_data, links):
            self.status_code = status_code
            self._json_data = json_data
            self.links = links
        def json(self):
            return self._json_data
            
    mocker.patch('requests.get', return_value=MockResponse(200, [{'name': 'repo1'}], {}))
    
    repos, headers = fetch_github_repos.fetch_repos()
    assert len(repos) == 1
    assert repos[0]['name'] == 'repo1'
    assert headers['Authorization'] == 'token mock_token'

def test_integration_json_writing(tmp_path, mocker):
    # Mock the API responses
    mocker.patch('fetch_github_repos.fetch_repos', return_value=([
        {
            'name': 'test-repo',
            'full_name': 'user/test-repo',
            'description': 'Test description',
            'html_url': 'https://github.com/user/test-repo',
            'private': False,
            'language': 'Python'
        }
    ], {}))
    
    mocker.patch('fetch_github_repos.fetch_readme', return_value="# Test\nA test project.\n```mermaid\ngraph LR\nX-->Y\n```\n")
    
    test_out_dir = tmp_path / "src" / "data"
    os.makedirs(test_out_dir, exist_ok=True)
    
    # We patch the hardcoded path in main by mocking os.path.join
    original_join = os.path.join
    def mock_join(*args):
        if 'projects.json' in args:
            return str(test_out_dir / 'projects.json')
        return original_join(*args)
        
    mocker.patch('os.path.join', side_effect=mock_join)
    
    fetch_github_repos.main()
    
    out_file = test_out_dir / 'projects.json'
    assert out_file.exists()
    
    with open(out_file) as f:
        data = json.load(f)
        
    assert len(data) == 1
    assert data[0]['title'] == 'test-repo'
    assert data[0]['description'] == 'A test project.'
    assert "graph LR" in data[0]['mermaid_diagram']
