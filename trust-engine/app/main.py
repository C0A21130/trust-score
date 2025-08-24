from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import torch
from components.database import Database
from components.train import train
from components.generate import generate
from components.centralality import calculate_centrality

app = FastAPI()
database = Database('neo4j://graph-db:7687')

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

@app.get("/")
def root():
    if torch.cuda.is_available():
        return {
            "message": "Fast API",
            "CUDA": torch.version.cuda,
            "GPU": torch.cuda.get_device_name(0)
        }
    else:
        return {
            "message": "Fast API",
            "GPU": "Not Available"
        }

def run_train(contract_address: str) -> None:
    # 学習用のデータを取得
    df_transaction, graph = database.get_transaction(contract_address=contract_address)
    df_feature = database.get_features(df_transaction=df_transaction, graph=graph)
    data = database.transform_data(df_transaction=df_transaction, df_feature=df_feature)
    
    # モデルの学習
    train(data)

@app.get("/train")
def train_model(background_tasks: BackgroundTasks, contract_address: str = "all"):
    background_tasks.add_task(run_train, contract_address)
    return {"message": "Training started"}

@app.get("/generate")
def generate_network(contract_address: str, tau: float=0.5):
    # 生成に必要なデータを取得
    df_transaction, graph = database.get_transaction(contract_address=contract_address)
    df_feature = database.get_features(df_transaction=df_transaction, graph=graph)
    data = database.transform_data(df_transaction=df_transaction, df_feature=df_feature)

    # 元の中心性を取得
    original_centrality = calculate_centrality(graph=graph)

    # ネットワーク生成
    predict_centrality = generate(df_feature=df_feature, data=data, tau=tau)
    
    return {
        "message": "Generation finished",
        "centrality": original_centrality,
        "predict_centrality": predict_centrality
    }

@app.get("/transaction")
def get_transaction(contract_address: str, address: str):
    df_transaction, graph = database.get_transaction(contract_address=contract_address)
    df_transaction = df_transaction.sort_values(by="blockNumber", ascending=False)
    result = df_transaction[df_transaction["from"] == address][["from", "to", "tokenUri"]]
    if result.empty:
        result = df_transaction[df_transaction["to"] == address][["from", "to", "tokenUri"]]

    return {
        "message": "Transaction data retrieved",
        "result": result.iloc[0].to_dict() if not result.empty else None,
    }

@app.on_event("shutdown")
def shutdown_event():
    global database
    if database:
        database.close()
