from neo4j import GraphDatabase
import atexit
import pandas as pd
import torch
from torch_geometric.data import Data
import networkx as nx
from typing import Tuple
from components.centralality import calculate_centrality

class Database:
    def __init__(self, url):
        # neo4j serverに接続するdriverの設定
        self.driver = GraphDatabase.driver(url)
        atexit.register(self.close)  # プログラム終了時にclose()を呼び出す
    
    def close(self):
        if hasattr(self, 'driver') and self.driver:
            self.driver.close()
            self.driver = None

    # 取引データを取得する
    @staticmethod
    def fetch_transaction(tx, contract_address: str) -> Tuple[pd.DataFrame, nx.DiGraph]:
        relation_list = []
        graph = nx.DiGraph()

        # データベースからトランザクションを取得
        if contract_address == "all":
            query = "MATCH p=()-[r:TRANSFER]->() RETURN p"
        else:
            query = """
            MATCH p=()-[r:TRANSFER {contractAddress: $address}]->()
            RETURN p
            """
        transactions = tx.run(query, address=contract_address)

        # トランザクションの結果をリストに保存
        for transaction in transactions:
            path = transaction["p"]
            relationship = path.relationships[0]
            relation_list.append({
                "tokenId": relationship["tokenId"],
                "from": path.start_node["address"], 
                "to": path.end_node["address"],
                "gasPrice": relationship["gasPrice"],
                "gasUsed": relationship["gasUsed"],
                "contractAddress": relationship["contractAddress"],
                "tokenUri": relationship["tokenUri"],
                "blockNumber": relationship["blockNumber"],
            })
            # グラフにエッジを追加
            graph.add_edge(str(path.start_node["address"]), str(path.end_node["address"]))
        return relation_list, graph

    # 取引データを取得する
    def get_transaction(self, contract_address: str = "all") -> Tuple[pd.DataFrame, nx.DiGraph]:

        # neo4jに接続してトランザクションを実行
        with self.driver.session() as session:
            relation_list, graph = session.execute_read(self.fetch_transaction, contract_address)

        # DataFrameに変換
        relations = pd.DataFrame(relation_list).astype({
            "tokenId": "string",
            "from": "string",
            "to": "string",
            "gasPrice": "float32",
            "gasUsed": "float32",
            "contractAddress": "string",
            "tokenUri": "string",
            "blockNumber": "uint32",
        }, copy=False)
        del relation_list # メモリを節約するためにリストを削除

        return relations, graph
    
    # 特徴量を取得する
    def get_features(self, df_transaction: pd.DataFrame, graph: nx.DiGraph) -> pd.DataFrame:
        # グラフが空の場合は空のDataFrameを返す
        if graph.number_of_nodes() == 0:
            return pd.DataFrame(columns=["degree", "betweenness", "pagerank"])

        # ユニークなノードを取得
        df_feature = pd.DataFrame(
            index=list(graph.nodes),
            columns=["degree", "betweenness", "pagerank"]
        )

        # 中心性を計算
        centrality = calculate_centrality(graph)
        df_feature["degree"] = pd.Series(centrality["degree"], dtype="float32")
        df_feature["betweenness"] = pd.Series(centrality["betweenness"], dtype="float32")
        df_feature["pagerank"] = pd.Series(centrality["pagerank"], dtype="float32")
        del centrality  # メモリを節約するために辞書を削除

        # ガス代を集計して特徴量に追加
        df_feature = df_feature.merge(
            df_transaction.groupby('from')[['gasPrice', "gasUsed"]].sum().add(
                df_transaction.groupby('to')[['gasPrice', "gasUsed"]].sum(),
                fill_value=0
            ),
            left_index=True,
            right_index=True,
            how='left'
        )

        # ブロック番号を追加
        df_feature = df_feature.merge(
            df_transaction.groupby('from')[['blockNumber']].first().add(
                df_transaction.groupby('to')[['blockNumber']].first(),
                fill_value=0
            ),
            left_index=True,
            right_index=True,
            how='left'
        )

        return df_feature

    # Dataframe(取引履歴とノードの特徴量)をPyTorch GeometricのDataオブジェクトに変換する
    def transform_data(self, df_transaction: pd.DataFrame, df_feature: pd.DataFrame) -> Data:
        # ノードのユニークIDを取得し、ノードのインデックスを辞書として作成
        unique_nodes = pd.concat([df_transaction['from'], df_transaction['to']]).unique()
        node_to_index = {node: idx for idx, node in enumerate(unique_nodes)}

        # トランザクションからエッジインデックスを作成
        edge_index = torch.tensor(
            [[node_to_index[row['from']], node_to_index[row['to']]] for _, row in df_transaction.iterrows()],
            dtype=torch.long
        ).t().contiguous()

        # ノードの特徴量をdf_featureから取得
        x = torch.tensor(df_feature.loc[unique_nodes].values, dtype=torch.float)
        data = Data(x=x, edge_index=edge_index)
        return data
