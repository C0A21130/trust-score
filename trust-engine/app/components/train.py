import os
import logging
import torch
from torch_geometric.data import Data
from torch_geometric.nn import VGAE
from components.model import GraphEncoder

def train(data: Data, epoch_num: int = 300):
    # logging設定
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("data/train.log", encoding='utf-8')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # 特徴量の次元数、MLモデルを設定
    in_channels = data.x.size(-1)
    out_channels = 3
    model = VGAE(GraphEncoder(in_channels=in_channels, out_channels=out_channels))
    logger.info("=== ML Model Info ===")
    logger.info(f"Input Feature Dimension: {in_channels}")
    logger.info(f"Output Feature Dimension: {out_channels}")

    # dataとmodelをGPUに転送
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    data = data.to(device)
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    logger.info(f"Use Device: {device}")
    logger.info(f"Optimizer: Adam")
    logger.info(f"Epochs: {epoch_num}")
    logger.info("=== Training Data Info ===")
    logger.info(f"Number of Nodes: {data.num_nodes}")
    logger.info(f"Number of Edges: {data.edge_index.size(1)}")
    logger.info(f"Number of Features: {data.x.size(-1)}")

    # モデルを学習
    logger.info("=== Training Start ===")
    best_loss = float('inf')
    for epoch in range(1, epoch_num + 1):
        model.train()
        optimizer.zero_grad()
        z = model.encode(data.x, data.edge_index)
        recon_loss = model.recon_loss(z, data.edge_index)
        kl_loss = (1 / data.num_nodes) * model.kl_loss()
        loss = recon_loss + kl_loss
        loss.backward()
        optimizer.step()

        # ベストモデルの更新
        if loss < best_loss:
            best_loss = loss
            # モデルの保存
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': loss,
            }, os.path.join("data", 'best_model.pt'))
        logger.info(f"Epoch: {epoch}, Loss: {loss.item()}, Best Loss: {best_loss.item()}")
