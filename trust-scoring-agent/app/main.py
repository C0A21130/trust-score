from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from components.models import RequestLogs, Log
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
    # 受け取ったを保存する形式に変換する
    transfer_logs = []
    for log in request_logs.transfer_logs:
        transfer_log = Log(
            token_id=log.token_id,
            from_address=log.from_address,
            to_address=log.to_address,
            transaction_hash=log.transaction_hash,
            gas_used=log.gas_used,
            gas_price=log.gas_price
        )
        transfer_logs.append(transfer_log)

    # 変換したログを保存する
    try:
        post_logs.save_adress(logs=transfer_logs)
        post_logs.save_relationship(contract_address=request_logs.contract_address, logs=transfer_logs)
        return {"message": "Logs recorded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/score/{address}")
def get_score(address: str):
    # ここではスコアを計算するロジックを実装する
    # 仮のスコアを返す
    score = 100
    return {"address": address, "score": score}
