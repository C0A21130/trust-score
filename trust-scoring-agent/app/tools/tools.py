from typing import Annotated, List, Tuple
from langchain_core.tools import tool
from tools.contract import Contract
from tools.engine import Engine

def get_tools(rpc_url: str, url: str, token_contract_address: str, scoring_contract_address: str, private_key: str) -> List[tool]:
    """
    トラストスコアリングに関連するツールを取得する。

    **ツール一覧**
    1. `regist_score`: 信用スコアをブロックチェーンに登録する
    2. `predict_score`: 中心性分析とGNNによって信用スコアと予測的信用スコアを算出する
    3. `get_transaction`: ブロックチェーンから取引情報を取得する
    """
    contract = Contract(
        rpc_url=rpc_url,
        token_contract_address=token_contract_address,
        scoring_contract_address=scoring_contract_address,
        private_key=private_key
    )
    engine = Engine(url=url)

    @tool
    def regist_score(
        address: Annotated[str, "The address to register the score for"],
        score: Annotated[float, "The score to register"]
    ) -> None:
        """
        Register a score for a specific address on the blockchain.
        """
        contract.regist_score(address, score)

    @tool
    def get_score(
        address: Annotated[str, "The address to get the score for"]
    ) -> float:
        """
        Get the score for a specific address.
        """
        return contract.get_score(address)
    
    @tool
    def predict_score(
        my_address: Annotated[str, "The my user's address"],
        address_list: Annotated[List[str], "The list of multiple user`s addressess to get scores for"],
        contract_address: Annotated[str, "The contract address for NFT collection"]
    ) -> Tuple[List[float], List[dict]]:
        """
        `Trust Score` and `Predict Trust Score` for a specific address by trust engine.
        `Trust Score` is calculated from the centrality of the transaction network.
        `Predict Trust Score` is calculated from the centrality of the transaction network predicted by the GNN.
        """
        score, predict_score = engine.predict_score(contract_address=contract_address)
        try :
            my_score = {
                "address": my_address,
                "score": score[my_address],
                "predict_score": predict_score[my_address]
            }
        except KeyError:
            my_score = {
                "address": my_address,
                "score": 0.0,
                "predict_score": 0.0
            }
        partner_scores = {}
        for address in address_list:
            try:
                partner_scores[address] = {
                    "address": address,
                    "score": score[address],
                    "predict_score": predict_score[address]
                }
            except KeyError:
                partner_scores[address] = {
                    "address": address,
                    "score": 0.0,
                    "predict_score": 0.0
                }
        return my_score, partner_scores

    @tool
    def get_transaction(
        contract_address: Annotated[str, "The contract address"],
        address: Annotated[str, "The user address for filtering"]
    ) -> dict:
        """
        Get the recent transaction information for a specific user.
        If there is no difference in the `Trust Score` or `Predict Trust Score` and you are having difficulty authorizing a user, please call this tool.
        You can use the information obtained from this tool to make a more informed decision about whether to authorize the user or not.
        """
        result = engine.get_transaction(contract_address=contract_address, address=address)
        return result if result else {}

    return [ regist_score, predict_score, get_transaction ]
