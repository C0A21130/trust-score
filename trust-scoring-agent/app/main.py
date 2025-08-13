from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from components.models import RequestLogs
from components.post_logs import PostLogs

app = FastAPI()
post_logs = PostLogs("bolt://graph-db:7687")

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

@app.get("/score/{address}")
def get_score(address: str):
    # ここではスコアを計算するロジックを実装する
    # 仮のスコアを返す
    score = 100
    return {"address": address, "score": score}
