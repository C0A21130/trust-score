import os
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langfuse.langchain import CallbackHandler
from components.trust_scoring_agent import TrustScoringAgent
from components.models import RequestLogs
from components.post_logs import PostLogs
from components.models import State
from tools.engine import Engine
from tools.tools import get_tools

load_dotenv()
app = FastAPI()
post_logs = PostLogs(os.environ["GRAPH_DB_URL"])
engine = Engine(os.environ["TRUST_ENGINE_URL"])
tools = get_tools(
    rpc_url=os.environ["RPC_URL"],
    url=os.environ["TRUST_ENGINE_URL"],
    token_contract_address=os.environ["TOKEN_CONTRACT_ADDRESS"],
    scoring_contract_address=os.environ["SCORING_CONTRACT_ADDRESS"],
    private_key=os.environ["PRIVATE_KEY"]
)
# Initialize the Trust Scoring Agent with Azure OpenAI model
model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)
# Initialize handler for Langfuse
langfuse_handler = CallbackHandler()
# Initialize the Trust Scoring Agent
trust_score_agent = TrustScoringAgent(
    model=model,
    tools=tools,
    handler=langfuse_handler
)

def route(state: State) -> Literal["regist_score", "predict_score", "thinking"]:
    if state.status == "predict_score":
        return "predict_score"
    elif state.status == "thinking":
        return "thinking"
    elif state.status == "regist_score":
        return "regist_score"
    else:
        return "thinking"

def get_graph():
    # Initialize the state graph
    graph_builder = StateGraph(State)

    # Add nodes to the state graph
    graph_builder.add_node("regist_score", trust_score_agent.get_bind_tool_agent)
    graph_builder.add_node("get_score", trust_score_agent.get_bind_tool_agent)
    graph_builder.add_node("predict_score", trust_score_agent.get_bind_tool_agent)
    graph_builder.add_node("thinking", trust_score_agent.get_agent)

    # Add edges between the nodes
    graph_builder.add_edge(START, "thinking")
    graph_builder.add_conditional_edges("thinking", route)
    graph_builder.add_edge("get_score", "thinking")
    graph_builder.add_edge("predict_score", "thinking")
    graph_builder.add_edge("regist_score", END)

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
def read_root():
    return {"message": "Welcome to the Scoring Engine API"}

@app.post("/logs")
def create_address(request_logs: RequestLogs):
    # 変換したログを保存する
    try:
        post_logs.save_adress(logs=request_logs.transfer_logs)
        post_logs.save_relationship(logs=request_logs.transfer_logs)
        return {"message": "Logs recorded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/scores")
def get_score(contract_address: str):
    original_centrality, predict_centrality = engine.predict_score(contract_address=contract_address)
    return {"original_score": original_centrality, "predict_score": predict_centrality}

@app.get("/auth")
def get_auth(from_address: str, to_address: str):
    # Initialize the state for the trust scoring agent
    state = State(
        messages=[],
        logs=[],
        contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
        my_address=from_address,
        to_address=to_address,
        trust_score=None,
        predict_trust_score=None,
        status="start"
    )
    result = None
    streams = graph.stream(state, config={"callbacks": [langfuse_handler]}, stream_mode="values")
    for stream in streams:
        print(stream)
        result = stream

    return {"messages": result["messages"]}
