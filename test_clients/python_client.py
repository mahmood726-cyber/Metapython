# MetaPython Python Client (Generated)
import requests

class MetaPythonClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def run_meta_analysis(self, config):
        """Run meta-analysis via API"""
        response = requests.post(f"{self.base_url}/api/v1/analyze", json=config)
        return response.json()
