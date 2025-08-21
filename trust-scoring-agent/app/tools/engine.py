from typing import Tuple
import requests

class Engine:
    def __init__(self, url :str):
        self.url = url

    def predict_score(self, contract_address: str) -> Tuple[dict, dict]:
        centrality_key = "pagerank"
        params = {
            "contract_address": contract_address,
            "tau": 0.5
        }
        response = requests.get(f"{self.url}/generate", params=params)
        if response.status_code == 200:
            original_centrality = response.json().get("original centrality")
            predict_centrality = response.json().get("predict centrality")
            return original_centrality[centrality_key], predict_centrality[centrality_key]
        return {}, {}
