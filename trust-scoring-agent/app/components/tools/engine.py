from typing import Tuple
import requests

class Engine:
    def __init__(self, engine_url :str):
        self.url = engine_url

    def predict_score(self, contract_address: str, transactions: list = None) -> dict:
        """
        `Trust Engine`に接続し、信用スコアを予測する。
        信用スコアは、`Trust Score`と`Predict Trust Score`の2つの指標で表される。
        """
        centrality_key = "pagerank"
        json = {
            "contract_address": contract_address,
            "transactions": transactions
        }
        response = requests.get(f"{self.url}/generate", json=json)
        if response.status_code == 200:
            centrality = response.json().get("centrality")
            predict_centrality = response.json().get("predict_centrality")
            generate_graph = response.json().get("generate_graph")
            return {
                "original_score": centrality[centrality_key],
                "predict_score": predict_centrality[centrality_key],
                "generate_graph": generate_graph
            }
        return {}

    def get_transaction(self, contract_address: str, address: str) -> dict:
        """
        特定のユーザーの最近の取引情報を取得する。
        `Trust Score`または`Predict Trust Score`に変化がなく、ユーザーを承認する際に困難が生じている場合は、このツールを実行する。
        取得した情報を活用することで、ユーザーを承認するかどうかについて、より適切な判断を下すことが可能である。
        """
        params = {
            "contract_address": contract_address,
            "address": address
        }
        response = requests.get(f"{self.url}/transaction", params=params)
        if response.status_code == 200:
            return response.json()
        return {}
