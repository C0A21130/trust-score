import torch
from torch_geometric.nn import VGAE
from torch_geometric.data import Data
import pandas as pd
import networkx as nx
from typing import Tuple
from components.model import GraphEncoder
from components.centralality import calculate_centrality

def generate(df_feature: pd.DataFrame, data: Data, tau: float = 0.5) -> dict:
    """
    学習済みのVGAEを用いてノード特徴量とエッジ情報から新しいネットワークを生成し、中心性を算出
    """
    # 入力・出力次元数の設定と学習用のモデルのロード
    in_channels = data.x.size(-1)
    out_channels = 3
    try:
        model = VGAE(GraphEncoder(in_channels=in_channels, out_channels=out_channels))
        checkpoint = torch.load("data/best_model.pt")
        model.load_state_dict(checkpoint['model_state_dict'])
    except Exception as e:
        raise RuntimeError(f"モデルのロードに失敗しました: {e}")

    # ネットワーク生成
    model.eval()
    with torch.no_grad():
        z = model.encode(data.x, data.edge_index)
        adj = z @ z.t()
        adj = torch.sigmoid(adj)
        adj_matrix = (adj > tau).nonzero(as_tuple=False).t()
        network = adj_matrix[:, torch.randperm(adj_matrix.size(1))[:data.num_edges]]

    # networkをリストに変換する
    node_list = network.t().tolist()
    node_labels = df_feature.index.tolist()

    # node_listの各エッジのノードインデックスを対応するラベルに変換
    node_with_label_list = []
    for edge in node_list:
        source_idx, target_idx = edge
        source_label = node_labels[source_idx]
        target_label = node_labels[target_idx]
        node_with_label_list.append([source_label, target_label])
    del node_list
    del node_labels

    # node_with_label_listをNetworkXデータに変換する
    generate_graph = nx.DiGraph()
    generate_graph.add_edges_from(node_with_label_list)
    centrality = calculate_centrality(generate_graph)
    del node_with_label_list
    del generate_graph

    return centrality
