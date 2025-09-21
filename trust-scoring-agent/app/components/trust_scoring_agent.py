from typing import List, Literal
import base64
import json
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from components.models import State, User, OutputJson

class TrustScoringAgent:
    def __init__(self, model, tools: list, contract_address: str, handler=None):
        self.model = model
        self.tools = tools
        self.contract_address = contract_address
        self.config = {"callbacks": [handler]}
    
    @staticmethod
    def get_route(state: State) -> Literal["thinking", "tool", "end"]:
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

    def create_user_list_prompt(self, state: State) -> str:
        """
        ユーザー一覧のプロンプトを作成する
        """

        # ユーザー一覧のプロンプトを作成
        user_list = f"""
        ## Content for User List
        - Trust Score
            - 取引相手に関する(過去の取引履歴やユーザーの特徴を元に算出される)信用度を定量化したスコア
            - ネットワーク中心性(次数中心性・媒介中心性・PageRank)に基づいて算出される
        - Predict Trust Score
            - 一般的信頼とは相手についての情報が少ない場合の相手の信頼性に対するデフォルト値
            - GNN(Graph Neural Network)による取引予測によって算出される
        - Transaction Network
            - ユーザー間の取引関係を示すグラフ構造
            - ノードはユーザーを、エッジは取引を表す

        ## User List

        """
        user_list += f"""
        **Information for Me**
        - Address: {state.my_info.address}
        - Trust Score: {state.my_info.trust_score if state.my_info.trust_score is not None else "未登録"}
        - Predict Trust Score: {state.my_info.predict_trust_score if state.my_info.predict_trust_score is not None else "未登録"}
        - Information: {state.my_info.info if state.my_info.info is not None else "未登録"}
        
        """
        user_list += "**Information for Transfer Partners**\n"
        user_list += "\n".join([
            f"""
            User {i + 1}:
            - Address: {user.address}
            - Trust Score: {user.trust_score if user.trust_score is not None else '未登録'}
            - Predict Trust Score: {user.predict_trust_score if user.predict_trust_score is not None else '未登録'}
            - Information: {user.info if user.info is not None else '未登録'}
            """
            for i, user in enumerate(state.transfer_partners)
        ])
        return user_list

    def create_info(self, tokenUri: str) -> str:
        """
        Token URIから最近の取引情報を取得し、画像を認識して説明文を生成する
        """
        try:
            meta_data = base64.b64decode(tokenUri.split(",")[1])
            meta_data_dict = json.loads(meta_data)
            ipfs_url = meta_data_dict["image"]
            name = meta_data_dict["name"]
            description = meta_data_dict["description"]
            response = requests.get(f"https://ipfs.io/ipfs/{ipfs_url.split('/')[-1]}")
            if response.status_code == 200:
                image = response.content
                image_base64 = base64.b64encode(image).decode("utf-8")
        except (IndexError, json.JSONDecodeError):
            print(tokenUri)
            response = requests.get(tokenUri)
            image_base64 = base64.b64encode(response.content).decode("utf-8")

        # 画像を認識して説明文を生成
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
        エージェントを取得する。
        事前に信用スコアを計算し信用スコアに基づいて取引相手を認可する。
        """
        # 出力形式を定義
        output_parser = PydanticOutputParser(pydantic_object=OutputJson)
        format_instructions = output_parser.get_format_instructions()

        # プロンプトテンプレートを作成
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    # Trust Scoring Agent

                    ## Overview
                    あなたは、信用スコアに基づいてNFT(Non-Fungible Token)の取引相手を認可するエージェントです。
                    取引相手のウォレットアドレスを`Trust Score`や`Predict Trust Score`に基づいた信用スコアに基づいて選択します。
                    ユーザーの追加情報に基づいて`Trust Score`に加点してください。
                    - NFTが信頼できる発行元から発行されている → +0.01
                    - 画像が信頼できるものである → +0.01
                    - NFTからユーザーのスキルを証明可能 → +0.01

                    ## ステップ
                    1. `tool`を呼び出して信用スコアを計算する
                    2. もし`Trust Score`や`Predict Trust Score`に0.05以下しか差がない場合は`tool`を呼び出す
                    3. 信用スコアから認可する取引相手`authorized_user`を選択する(もし認可できない場合は`authorized_user`を`None`にする)

                    ## 出力形式
                    {format_instructions}
                    """
                ),
                (
                    "system",
                    "{user_list_prompt}"
                )
            ]
        )
        user_list_prompt = self.create_user_list_prompt(state)
        prompt = prompt_template.partial(
            format_instructions=format_instructions,
            user_list_prompt=user_list_prompt
        )

        # モデルを実行
        agent = prompt | self.model | output_parser
        if self.config["callbacks"][0] == None:
            output: OutputJson = agent.invoke({"input": ""})
        else:
            output: OutputJson = agent.invoke({"input": ""}, config=self.config)
        
        return State(
            messages=[SystemMessage(output.message)],
            my_info=state.my_info,
            transfer_partners=state.transfer_partners,
            authorized_user=output.authorized_user if output.authorized_user else None,
            status="thinking" if output.status == "end" and output.authorized_user == None else output.status
        )

    def get_bind_tool_agent(self, state: State) -> State:
        """
        ツールをバインドさせたエージェントを取得する。
        Tool Callingを使用して動的にツールを呼び出す。
        """
        message = ""
        my_info: User = state.my_info
        transfer_partners: List[User] = state.transfer_partners

        # 信用スコアを登録する
        if(state.status == "end"):
            self.tools[0].invoke({
                "address": state.authorized_user.address,
                "score": state.authorized_user.trust_score
            })
            message += f"{state.authorized_user.address}の信用スコアが登録されました"
            return state

        # プロンプトを作成
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    # Trust Scoring Agent
                    ユーザーの入力情報を基に信用スコアを計算し、NFTの取引を認可するエージェント
                    必要な情報を取得するためのツールを選択してください
                    `contract_address`は {contract_address}

                    ## ステップ
                    1. `User List`の`Trust Score`や`Predict Trust Score`が未登録なら`predict_score`を呼び出す
                    2. `Trust Score`や`Predict Trust Score`に0.05以下でしか差がない場合は`get_transaction`を呼び出す
                    3. `User List`をもとに、認可する取引相手`authorized_user`を選択する
                    """
                ),
                (
                    "system",
                    "{user_list_prompt}"
                )
            ]
        )
        user_list_prompt = self.create_user_list_prompt(state)
        prompt = prompt_template.format_messages(
            contract_address=self.contract_address,
            user_list_prompt=user_list_prompt,
        )

        # モデルにツールをバインドさせて実行
        model_with_tool = self.model.bind_tools(self.tools)
        if self.config["callbacks"][0] == None:
            output = model_with_tool.invoke(prompt)
        else:
            output = model_with_tool.invoke(prompt, config=self.config)
        
        # モデルの呼び出し結果を基にツールを実行
        for tool_call in output.tool_calls:
            print(tool_call["name"])
            if tool_call["name"] == "predict_score":
                my_score, partner_scores = self.tools[1].invoke(tool_call["args"])
                message = "信用スコアを予測しました"
                my_info = User(address=state.my_info.address, trust_score=my_score["score"], predict_trust_score=my_score["predict_score"], info=state.my_info.info)
                transfer_partners = [
                    User(
                        address=user.address,
                        trust_score=partner_scores[user.address]["score"],
                        predict_trust_score=partner_scores[user.address]["predict_score"],
                        info=user.info
                    ) for user in state.transfer_partners
                ]
            elif tool_call["name"] == "get_transaction":
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

        return State(
            messages=[SystemMessage(message)],
            my_info=my_info,
            transfer_partners=transfer_partners,
            authorized_user=state.authorized_user,
            status="thinking"
        )
