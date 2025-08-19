import pytest
from unittest.mock import Mock, patch
import pandas as pd
import networkx as nx
import torch
from torch_geometric.data import Data
from components.database import Database

@pytest.fixture
def mock_database():
    """モックデータベース"""
    database = Database('neo4j://graph-db:7687')
    return database

@pytest.fixture
def sample_transaction_data():
    """サンプル取引データ"""
    return pd.DataFrame({
        'tokenId': [1, 2, 3],
        'from': ['addr1', 'addr2', 'addr1'],
        'to': ['addr2', 'addr3', 'addr3'],
        'gasPrice': [100.0, 200.0, 150.0],
        'gasUsed': [21000.0, 25000.0, 23000.0],
        'contractAddress': ['contract1', 'contract1', 'contract2'],
        'tokenUri': ['uri1', 'uri2', 'uri3'],
        'blockNumber': [1000, 1001, 1002]
    })

@pytest.fixture
def sample_graph():
    """サンプルグラフデータ"""
    graph = nx.DiGraph()
    graph.add_edge('addr1', 'addr2')
    graph.add_edge('addr2', 'addr3')
    graph.add_edge('addr1', 'addr3')
    return graph

def test_get_transaction_all_contracts(mock_database):
    """全てのコントラクトの取引を取得するテスト"""
    database = mock_database
    result = database.get_transaction()
    assert result is not None

def test_get_transaction_specific_contract(mock_database):
    """コントラクトアドレスを指定して特定のコントラクトの取引をグラフDB取得するテスト"""
    database = mock_database
    result = database.get_transaction("0x76B50696B8EFFCA6Ee6Da7F6471110F334536321")
    assert result is not None

@patch('components.database.calculate_centrality')
def test_get_features(mock_centrality, sample_transaction_data, sample_graph):
    """特徴量取得関数のテスト"""
    mock_centrality.return_value = {
        'degree': {'addr1': 2.0, 'addr2': 2.0, 'addr3': 2.0},
        'betweenness': {'addr1': 0.5, 'addr2': 0.5, 'addr3': 0.0},
        'pagerank': {'addr1': 0.4, 'addr2': 0.3, 'addr3': 0.3}
    }
    
    database = Database('neo4j://graph-db:7687')
    df_features = database.get_features(sample_transaction_data, sample_graph)
    
    assert isinstance(df_features, pd.DataFrame)
    assert 'degree' in df_features.columns
    assert 'betweenness' in df_features.columns
    assert 'pagerank' in df_features.columns
    assert 'gasPrice' in df_features.columns
    assert 'gasUsed' in df_features.columns
    assert 'blockNumber' in df_features.columns
    mock_centrality.assert_called_once_with(sample_graph)

def test_transform_data():
    """データ変換関数のテスト"""
    # Sample transaction data
    df_transaction = pd.DataFrame({
        "tokenId": ["1", "2"],
        'from': ['addr1', 'addr2'],
        'to': ['addr2', 'addr3'],
        'gasPrice': [100.0, 200.0],
        'gasUsed': [21000.0, 25000.0],
        'contractAddress': ['contract1', 'contract1'],
        'tokenUri': ['uri1', 'uri2'],
        'blockNumber': [1000, 1001]
    })
    
    # Sample feature data
    df_feature = pd.DataFrame({
        'degree': [1.0, 2.0, 3.0],
        'betweenness': [4.0, 5.0, 6.0],
        "pagerank": [7.0, 8.0, 9.0],
        "gasPrice": [100.0, 200.0, 150.0],
        "gasUsed": [21000.0, 25000.0, 23000.0],
        "blockNumber": [1000, 1001, 1002]
    }, index=['addr1', 'addr2', 'addr3'])
    
    data = Database.transform_data(df_transaction, df_feature)
    
    assert isinstance(data, Data)
    assert data.x.shape == (3, 6)  # 3 nodes, 6 features
    assert data.edge_index.shape == (2, 2)  # 2 edges
    assert isinstance(data.x, torch.Tensor)
    assert isinstance(data.edge_index, torch.Tensor)
