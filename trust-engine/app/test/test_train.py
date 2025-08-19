import pytest
import torch
from torch_geometric.data import Data
from components.train import train
from components.database import Database

@pytest.fixture
def mock_data():
    """モックデータ"""
    x = torch.randn(10, 6)  # 10 nodes, 6 features
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.long)
    data = Data(x=x, edge_index=edge_index)
    data.num_nodes = 10
    return data

@pytest.fixture
def mock_database():
    database = Database('neo4j://graph-db:7687')
    return database

def test_train(mock_data):
    """学習関数のテスト"""
    data = mock_data
    train(data, epoch_num=10)

def test_train_for_validation(mock_database):
    """学習関数のテスト(DBからのデータ取得)"""
    database = mock_database
    df_transaction, graph = database.get_transaction()
    df_feature = database.get_features(df_transaction, graph)
    data = database.transform_data(df_transaction, df_feature)
    train(data, epoch_num=10)
