import torch
import logging
from sklearn.metrics import roc_curve
from torch_geometric.nn import VGAE
from torch_geometric.data import Data
from torch_geometric.utils import negative_sampling
import pandas as pd
import networkx as nx
from components.model import GraphEncoder
from components.centralality import calculate_centrality

def generate(df_feature: pd.DataFrame, data: Data) -> dict:
    """
    学習済みのVGAEを用いてノード特徴量とエッジ情報から新しいネットワークを生成し、中心性を算出
    """
    # logging設定
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("data/generate.log", encoding='utf-8')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 入力・出力次元数の設定と学習用のモデルのロード
    in_channels = data.x.size(-1)
    out_channels = data.x.size(-1)
    try:
        model = VGAE(GraphEncoder(in_channels=in_channels, out_channels=out_channels))
        checkpoint = torch.load("data/best_model.pt")
        model.load_state_dict(checkpoint['model_state_dict'])
    except Exception as e:
        logger.error(f"モデルのロードに失敗しました: {e}")
        raise RuntimeError(f"モデルのロードに失敗しました: {e}")

    # ログ出力
    logger.info("=== Loaded Model Info ===")
    logger.info(f"Input Feature Dimension: {in_channels}")
    logger.info(f"Output Feature Dimension: {out_channels}")

    # ネットワーク生成
    logger.info("=== Network Generation Start ===")
    model.eval()
    with torch.no_grad():
        # ノードの潜在表現を取得
        z = model.encode(data.x, data.edge_index)

        # 正エッジを予測
        num_pos_edges = data.edge_index.size(1)
        pos_edge_index = data.edge_index[:, :num_pos_edges]
        pos_pred = model.decode(z, pos_edge_index).view(-1).cpu()

        # 負エッジを予測
        num_neg_edges = data.edge_index.size(1)
        neg_edge_index = negative_sampling(
            edge_index=data.edge_index,
            num_nodes=data.num_nodes,
            num_neg_samples=num_neg_edges
        )
        neg_pred = model.decode(z, neg_edge_index).view(-1).cpu()

        # 予測スコアとラベルを結合
        preds = torch.cat([pos_pred, neg_pred], dim=0)
        pos_labels = torch.ones(pos_pred.size(0))
        neg_labels = torch.zeros(neg_pred.size(0))
        labels = torch.cat([pos_labels, neg_labels], dim=0)

        # Youden's J statisticを利用して最適な閾値を決定
        fpr, tpr, thresholds = roc_curve(labels, preds)
        optimal_idx = (tpr - fpr).argmax()
        optimal_threshold = thresholds[optimal_idx]

        # accuracyを出力
        preds_binary = (preds >= optimal_threshold).float()
        accuracy = (preds_binary == labels).sum().item() / labels.size(0)
        logger.info(f"Optimal Threshold: {optimal_threshold:.4f}")
        logger.info(f"AUC: {(tpr - fpr).max():.4f}")
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {((preds_binary == 1) & (labels == 1)).sum().item() / (preds_binary == 1).sum().item():.4f}")
        logger.info(f"Recall: {((preds_binary == 1) & (labels == 1)).sum().item() / (labels == 1).sum().item():.4f}")

        # エッジを保存
        prob = torch.sigmoid(z @ z.t())
        adj_matrix = (prob > optimal_threshold).nonzero(as_tuple=False).t().cpu()
        network = adj_matrix[:, torch.randperm(adj_matrix.size(1))[:data.num_edges]]
    logger.info("=== Network Generation Finished ===")

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

    # CSVにエッジリストを保存
    edge_df = pd.DataFrame(node_with_label_list, columns=["source", "target"])
    edge_df.to_csv("data/generated_network_edges.csv", index=False)

    # node_with_label_listをNetworkXデータに変換する
    generate_graph = nx.DiGraph()
    generate_graph.add_nodes_from(df_feature.index.tolist())
    generate_graph.add_edges_from(node_with_label_list)
    centrality = calculate_centrality(generate_graph)
    del node_list
    del node_labels
    del node_with_label_list
    del generate_graph

    return {
        "centrality": centrality,
        "edges_list": edge_df.values.tolist()
    }
