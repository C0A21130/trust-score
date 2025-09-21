import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langfuse.langchain import CallbackHandler
from components.trust_scoring_agent import TrustScoringAgent
from components.models import RequestLogs, State, User, AuthRequestBody
from components.database import Database
from tools.engine import Engine
from tools.tools import get_tools

load_dotenv()
app = FastAPI()
langfuse_handler = CallbackHandler()
database = Database(os.environ["GRAPH_DB_URL"])
engine = Engine(os.environ["TRUST_ENGINE_URL"])
tools = get_tools(
    rpc_url=os.environ["RPC_URL"],
    url=os.environ["TRUST_ENGINE_URL"],
    token_contract_address=os.environ["TOKEN_CONTRACT_ADDRESS"],
    scoring_contract_address=os.environ["SCORING_CONTRACT_ADDRESS"],
    private_key=os.environ["PRIVATE_KEY"]
)
model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)
trust_score_agent = TrustScoringAgent(
    model=model,
    tools=tools,
    contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
    handler=langfuse_handler
)

def get_graph():
    """
    Trust Scoring Agentの状態遷移グラフを生成する
    """
    # 状態遷移グラフを初期化
    graph_builder = StateGraph(State)

    # 状態遷移グラフにノードを追加
    graph_builder.add_node("thinking", trust_score_agent.get_agent)
    graph_builder.add_node("tool", trust_score_agent.get_bind_tool_agent)
    graph_builder.add_node("end", trust_score_agent.get_bind_tool_agent)

    # ノード間にエッジを追加
    graph_builder.add_edge(START, "thinking")
    graph_builder.add_conditional_edges("thinking", TrustScoringAgent.get_route)
    graph_builder.add_edge("tool", "thinking")
    graph_builder.add_edge("end", END)

    return graph_builder.compile()
graph = get_graph()

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

@app.get("/")
def get_root():
    return {"message": "Welcome to the Scoring Engine API"}

@app.post("/logs")
def post_logs(request_logs: RequestLogs):
    """
    変換したログを保存する
    """
    try:
        database.save_address(logs=request_logs.transfer_logs)
        database.save_relationship(logs=request_logs.transfer_logs)
        return {"message": "Logs recorded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/scores")
def get_score(contract_address: str):
    """
    信用スコアを取得する
    """
    original_centrality, predict_centrality = engine.predict_score(contract_address=contract_address)
    return {"original_score": original_centrality, "predict_score": predict_centrality}

@app.post("/auth")
def get_auth(requestBody: AuthRequestBody):
    """
    取引先の信頼スコアを評価し、ユーザーを認可する
    """

    # リクエストから取引先のアドレスを取得
    from_address = requestBody.from_address
    to_address_list = requestBody.to_address_list

    # Trust Scoring Agentの状態を初期化
    state = State(
        messages=[],
        my_info=User(address=from_address, info=""),
        transfer_partners=[User(address=address, info="") for address in to_address_list],
        authorized_user=None,
        status="start"
    )

    # 結果を取得
    result = None
    streams = graph.stream(state, config={"callbacks": [langfuse_handler]}, stream_mode="values")
    for stream in streams:
        print(stream)
        result = stream

    return {
        "messages": result["messages"],
        "partners": result["transfer_partners"],
        "user": result["authorized_user"]
    }

@app.on_event("shutdown")
def shutdown_event():
    global database
    if database:
        database.close()
