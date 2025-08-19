import torch
from torch_geometric.nn import VGAE
from torch_geometric.data import Data
import pandas as pd
import networkx as nx
from components.model import GraphEncoder

def generate(df_feature: pd.DataFrame, data: Data, tau: float = 0.5) -> list:
    # 学習用のモデルをロード
    in_channels = data.x.size(-1)
    out_channels = 3
    model = VGAE(GraphEncoder(in_channels=in_channels, out_channels=out_channels))
    checkpoint = torch.load("data/best_model.pt")
    model.load_state_dict(checkpoint['model_state_dict'])

    # ネットワーク生成
    model.eval()
    with torch.no_grad():
        z = model.encode(data.x, data.edge_index)  # エンコーダを使用して潜在ベクトルzを生成
        adj = z @ z.t()  # xとzの内積を計算して隣接行列を生成
        adj = torch.sigmoid(adj)  # Sigmoid関数を適用して隣接行列を確率に変換
        adj_matrix = (adj > tau).nonzero(as_tuple=False).t()
        sample = adj_matrix[:, torch.randperm(adj_matrix.size(1))[:data.num_edges]]  # エッジをサンプリング
    
    # sampleをリストに変換する
    sample_list = sample.t().tolist()
    node_labels = df_feature.index.tolist()
    # sample_listの各エッジのノードインデックスを対応するラベルに変換
    labeled_sample_list = []
    for edge in sample_list:
        source_idx, target_idx = edge
        source_label = node_labels[source_idx]
        target_label = node_labels[target_idx]
        labeled_sample_list.append([source_label, target_label])

    # sampleをNetworkXデータに変換する
    # generate_graph = nx.Graph()
    # generate_graph.add_edges_from(sample_list)
    
    return labeled_sample_list
