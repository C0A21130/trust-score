import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from components.trust_scoring_agent import TrustScoringAgent
from components.models import RequestLogs, AuthRequestBody
from components.database import Database

load_dotenv()
app = FastAPI()
database = Database(os.environ["GRAPH_DB_URL"])
model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)
trust_score_agent = TrustScoringAgent(
    model=model,
    blockchain_url=os.environ["RPC_URL"],
    engine_url=os.environ["TRUST_ENGINE_URL"],
    token_contract_address=os.environ["TOKEN_CONTRACT_ADDRESS"],
    scoring_contract_address=os.environ["SCORING_CONTRACT_ADDRESS"],
    private_key=os.environ["PRIVATE_KEY"]
)

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

@app.post("/auth")
def get_auth(request_body: AuthRequestBody):
    """
    取引先の信頼スコアを評価し、ユーザーを認可する
    """
    # リクエストから取引先のアドレスを取得
    contract_address = request_body.contract_address
    from_address = request_body.from_address
    to_address_list = request_body.to_address_list

    # 結果を取得
    try:
        result = trust_score_agent.auth(
            contract_address=contract_address,
            from_address=from_address,
            to_address_list=to_address_list
        )
        return {
            "message": "Authorization process completed",
            "authorized_users": result["authorized_users"],
            "other": {
                "authorized_graph_users": result["authorized_graph_users"],
                "authorized_score_users": result["authorized_score_users"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/faucet")
def post_faucet(address: str):
    """
    テスト用のトークンを配布する
    """   
    try:
        success = trust_score_agent.faucet(address)
        if success:
            return {"message": "Faucet successful"}
        else:
            raise HTTPException(status_code=500, detail="Faucet failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    global database
    if database:
        database.close()
