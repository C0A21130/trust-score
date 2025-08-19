import pytest
import pandas as pd
import torch
from torch_geometric.data import Data
from components.database import Database
from components.generate import generate

@pytest.fixture
def mock_data():
    """モックデータ"""
    # 頂点特徴量
    df_feature = pd.DataFrame({
        'degree': [0.1, 0.2, 0.3],
        'betweeness': [1.0, 1.1, 1.2],
        'pagerank': [2.0, 2.1, 2.2],
        "gasPrice": [3.0, 3.1, 3.2],
        "gasUsed": [4.0, 4.1, 4.2],
        "blockNumber": [5, 5, 5]
    }, index=["0x1", "0x1", "0x2"])

    # pytorch
    x = torch.tensor(df_feature.values, dtype=torch.float)  # 3 nodes, 6 features
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.long)
    data = Data(x=x, edge_index=edge_index)
    data.num_nodes = 3
    return df_feature, data

@pytest.fixture
def mock_database():
    """モックデータベース"""
    database = Database('neo4j://graph-db:7687')
    return database

def test_generate_basic(mock_data):
    # モックデータからネットワーク生成
    df_feature, data = mock_data
    result = generate(df_feature=df_feature, data=data, tau=0.5)
    print(result)

    # 結果の検証
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(edge, list) and len(edge) == 2 for edge in result)

def test_generate_database(mock_database):
    # モックデータベースからネットワーク生成
    database = mock_database
    df_transaction, graph = database.get_transaction("0x76B50696B8EFFCA6Ee6Da7F6471110F334536321")
    df_feature = database.get_features(df_transaction=df_transaction, graph=graph)
    data = database.transform_data(df_transaction=df_transaction, df_feature=df_feature)
    result = generate(df_feature=df_feature, data=data, tau=0.5)
    print(result)

    # 結果の検証
    assert isinstance(result, list)
    assert all(isinstance(edge, list) and len(edge) == 2 for edge in result)
