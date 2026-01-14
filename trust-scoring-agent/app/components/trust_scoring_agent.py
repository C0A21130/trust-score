from typing import List, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langfuse.langchain import CallbackHandler
from .models import State, User
from .tools.contract import Contract
from .tools.engine import Engine

class TrustScoringAgent:
    def __init__(self, model, blockchain_url: str, engine_url: str, token_contract_address: str, scoring_contract_address: str, private_key: str):
        self.model = model
        self.private_key = private_key
        self.engine = Engine(engine_url)
        langfuse_handler = CallbackHandler()
        self.config = {"callbacks": [langfuse_handler]}

        try:
            self.contract = Contract(
                rpc_url=blockchain_url,
                token_contract_address=token_contract_address,
                scoring_contract_address=scoring_contract_address,
                private_key=private_key
            )
        except Exception as e:
            self.contract = None
            print(f"Error initializing Contract: {e}")
    
    @staticmethod
    def get_route(state: State) -> Literal["fetchTransaction", "report"]:
        """
        現在の状態に応じたノードの遷移先を決定する
        """
        if state.status == "thinking":
            return "thinking"
        elif state.status == "tool":
            return "tool"
        elif state.status == "end":
            return "end"
        else:
            return "thinking"

    def create_info(self, name: str, description: str, image_base64: str) -> str:
        """
        画像を認識して説明文を生成する
        """
        message = HumanMessage(
            content=[
                {"type": "text", "text": f"This is the image associated with the NFT({name}). You will need to extract a description of the image and any trust information associated with it. Description: {description}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        )
        output = self.model.invoke([message])
        return output.content

    def get_agent(self, state: State) -> State:
        """
        ツールをバインドさせたエージェントを取得する。
        Tool Callingを使用して動的にツールを呼び出す。
        """
        new_message = ""
        my_info: User = state.my_info
        transfer_partners = state.transfer_partners
        new_predict_score = None
        new_status = "thinking"

        prompt = self.create_prompt(state)

        # モデルにツールをバインドさせて実行
        model_with_tool = self.model.bind_tools(self.tools)
        if self.config["callbacks"][0] == None:
            output = model_with_tool.invoke(prompt)
        else:
            output = model_with_tool.invoke(prompt, config=self.config)
        
        # モデルの呼び出し結果を基にツールを実行
        for tool_call in output.tool_calls:
            if tool_call["name"] == "fetchTransaction":
                user_info = self.tools[2].invoke(tool_call["args"])
                info = self.create_info(user_info["result"]["tokenUri"])
                message = "ユーザーの追加情報を取得しました"
                transfer_partners = [
                    User(
                        address=partner.address,
                        trust_score=partner.trust_score,
                        predict_trust_score=partner.predict_trust_score,
                        info=info if partner.address in [user_info["result"]["from"], user_info["result"]["to"]] else partner.info
                    ) for partner in state.transfer_partners
                ]
            elif tool_call["name"] == "sumarizeTransaction":
                summary = self.tools[3].invoke(tool_call["args"])
                message = "ユーザーの追加情報を要約しました"
                transfer_partners = [
                    User(
                        address=partner.address,
                        trust_score=partner.trust_score,
                        predict_trust_score=partner.predict_trust_score,
                        info=summary["result"] if partner.address == tool_call["args"]["address"] else partner.info
                    ) for partner in state.transfer_partners
                ]

        return State(
            messages=[SystemMessage(message)],
            my_info=my_info,
            transfer_partners=transfer_partners,
            authorized_user=state.authorized_user,
            status="thinking"
        )
        
    def auth(self, contract_address: str, from_address: str, to_address_list: List[str], requireFetch: bool = False) -> dict:
        """
        取引先の信頼スコアを評価し、ユーザーを認可する
        1. 信用スコアを予測
        2. fromとtoの信用スコアをブロックチェーンに登録
        3. スマートコントラクトが信用スコアに基づいて認可するユーザーを決定
        4. 信用スコアをブロックチェーンに記録
        """
        authorized_users = []       # 生成されたグラフの中心性と隣接するユーザーから認可するユーザーを決定
        authorized_score_users = [] # 生成されたグラフの中心性のみから認可するユーザーを決定
        authorized_graph_users = [] # 生成されたグラフの隣接するユーザーのみから認可するユーザーを決定

        # トラストエンジンに問い合わせて信用スコアを予測
        if not requireFetch:
            result_score = self.engine.predict_score(contract_address=contract_address)
        else:
            transactions = self.contract.fetch_tokens()
            result_score = self.engine.predict_score(contract_address=contract_address, transactions=transactions)
        original_scores = result_score.get("original_score", {})
        predict_scores = result_score.get("predict_score", {})
        generate_graph = result_score.get("generate_graph", [])

        # fromとtoの信用スコアで最も高いスコアをブロックチェーンに登録
        from_score = max(
            original_scores.get(from_address, 0.0),
            predict_scores.get(from_address, 0.0)
        )
        self.contract.regist_score(address=from_address, score=from_score)
        for to_address in to_address_list:
            to_original_score = original_scores.get(to_address, 0.0)
            to_predict_score = predict_scores.get(to_address, 0.0)
            to_score = max(to_original_score, to_predict_score)
            self.contract.regist_score(address=to_address, score=to_score)

        # 生成されたグラフから隣接する取引相手を選択する
        for edge in generate_graph:
            source = target = None
            if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                source, target = edge[0], edge[1]
            if source == from_address and target is not None:
                authorized_users.append(target)
                authorized_graph_users.append(target)

        # 認可するユーザーを返す
        return {
            "authorized_users": authorized_users,
            "authorized_graph_users": authorized_graph_users,
            "authorized_score_users": authorized_score_users
        }

    def faucet(self, address: str) -> bool:
        """
        テスト用のトークンを配布する
        """
        return self.contract.faucet(address)
