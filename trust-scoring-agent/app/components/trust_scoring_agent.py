from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage
from components.models import State, OutputJson

class TrustScoringAgent:
    def __init__(self, model, tools: List, handler=None):
        self.model = model
        self.tools = tools
        self.config = {"callbacks": [handler]}

    def get_agent(self, state: State):
        # Define the output parser
        output_parser = PydanticOutputParser(pydantic_object=OutputJson)
        format_instructions = output_parser.get_format_instructions()

        # Define the prompt
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    # Trust Scoring Agent

                    ## 目的
                    あなたは、信用スコアに基づいてNFT(Non-Fungible Token)の取引を認可するエージェントです。
                    取引相手のウォレットアドレスを信用スコアや一般的信頼に基づいた信用スコアに基づいて選択します。
                    
                    ## ステップ
                    - もし信用スコアの情報が不足していれば`predict_score`関数を呼び出して、信用スコアを予測してください。
                    - もし信用スコアの情報を持っていたら`regist_score`関数を呼び出して信用スコアを登録し、取引可否(transfer_status)を決定してください。

                    ## 用語
                    - 信用スコア
                        - 取引相手に関する(過去の取引履歴やユーザーの特徴を元に算出される)信用度を定量化したスコア
                        - ネットワーク中心性(次数中心性・媒介中心性・PageRank)に基づいて算出される
                    - 一般的信頼に基づいた信用スコア
                        - 一般的信頼とは相手についての情報が少ない場合の相手の信頼性に対するデフォルト値
                        - GNN(Graph Neural Network)による取引予測によって算出される
                    - 取引ネットワーク
                        - ユーザー間の取引関係を示すグラフ構造
                        - ノードはユーザーを、エッジは取引を表す

                    ## 出力形式
                    {format_instructions}
                    """
                ),
                (
                    "system",
                    """
                    # ユーザーのウォレットアドレス一覧

                    ## ユーザーの項目
                    - Address: ユーザーのウォレットアドレス
                    - Trust Score: 信用スコア
                    - Predict Trust Score: 一般的信頼に基づいた信用スコア

                    ## ユーザー情報
                    {user_list}
                    """
                ),
                (
                    "human",
                    """
                    {input}
                    """
                )
            ]
        )
        user_info = """
        現在ユーザーの取引情報が不足しているため`predict_score`関数を呼び出して、信用スコアを予測してください。
        """
        if state.trust_score != None:
            user_info = f"""
            - Address: {state.to_address}
            - Trust Score: {state.trust_score}
            - Predict Trust Score: {state.predict_trust_score}
            """

        prompt = prompt_template.partial(
            format_instructions=format_instructions,
            user_list=user_info
        )

        agent = prompt | self.model | output_parser

        # Get the user input
        if self.config["callbacks"][0] == None:
            output = agent.invoke(
                {"input": ""}
            )
        else:
            output = agent.invoke(
                {"input": ""},
                config=self.config
            )

        return {
            "messages": [SystemMessage(output.message)],
            "logs": state.logs,
            "contract_address": state.contract_address,
            "my_address": state.my_address,
            "to_address": state.to_address,
            "trust_score": state.trust_score,
            "predict_trust_score": state.predict_trust_score,
            "transfer_status": output.transfer_status,
            "status": output.status
        }

    def get_bind_tool_agent(self, state: State) -> State:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    # Trust Scoring Agent
                    ユーザーの入力情報を基に信用スコアを計算し、NFTの取引を認可するエージェント

                    ## 目的
                    現在の状態から信用スコアを計算するためにツールを呼び出す
                    """
                ),
                (
                    "system",
                    """
                    ## 呼び出す内容
                    {input}
                    """
                )
            ]
        )

        if(state.status == "regist_score"):
            input_word = f"""
            ユーザーの信用スコアを登録するためにツールを呼び出す
            - ツール名: regist_score
            - 登録するユーザーアドレス: {state.to_address}
            """
        elif(state.status == "get_score"):
            input_word = f"""
            ユーザーの信用スコアを取得するためにツールを呼び出す
            - ツール名: get_score
            - 取得するユーザーアドレス: {state.to_address}
            """
        elif(state.status == "predict_score"):
            input_word = f"""
            予測スコアを取得するためにツールを呼び出す
            - ツール名: get_score
            - 予測するユーザーアドレス: {state.to_address}
            - コントラクトアドレス: {state.contract_address}
            """
        prompt = prompt_template.format_messages(
            input=input_word
        )

        # Bind tools to the model
        model_with_tool = self.model.bind_tools(self.tools)

        # Invoke the model with the prompt
        if self.config["callbacks"][0] == None:
            output = model_with_tool.invoke(prompt)
        else:
            output = model_with_tool.invoke(prompt, config=self.config)

        # Process tool calls
        message = ""
        trust_score, predict_trust_score = None, None
        for tool_call in output.tool_calls:
            print(tool_call["name"])
            if tool_call["name"] == "regist_score":
                # self.tools[0].invoke(tool_call["args"])
                message = f"{state.to_address}の信用スコアが登録されました。"
            elif tool_call["name"] == "get_score":
                trust_score = self.tools[1].invoke(tool_call["args"])
                message = f"{state.to_address}の信用スコアは{trust_score}です。"
            elif tool_call["name"] == "predict_score":
                trust_score, predict_trust_score = self.tools[2].invoke(tool_call["args"])
                message = f"{state.to_address}の信用スコアは{trust_score}、予測スコアは{predict_trust_score}です。"

        return {
            "messages": [SystemMessage(message)],
            "logs": state.logs,
            "contract_address": state.contract_address,
            "my_address": state.my_address,
            "to_address": state.to_address,
            "trust_score": trust_score,
            "predict_trust_score": predict_trust_score,
            "transfer_status": state.transfer_status,
            "status": "thinking",
        }
