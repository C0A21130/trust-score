import os
import sys
import pytest
from unittest.mock import MagicMock
from neo4j import GraphDatabase

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.post_logs import PostLogs
from components.model import Logs, Log

DB_URL = "bolt://10.203.92.71:7687"

@pytest.fixture
def mock_driver():
    """Neo4jドライバーのモック"""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    return mock_driver

@pytest.fixture
def sample_logs() -> Logs:
    """テスト用ログデータ"""
    return [
        Log(token_id=1, from_address="0x123", to_address="0x456", gas_used=21000, gas_price=1000000000, transaction_hash="0xabc"),
        Log(token_id=2, from_address="0x789", to_address="0xabc", gas_used=21000, gas_price=1000000000, transaction_hash="0xdef")
    ]

def test_save_adress_with_unique_addresses(sample_logs):
    """一意のアドレスが正しく保存されることをテスト"""

    def fetch_transaction(tx, address):
        """指定されたアドレスのトランザクションを取得するクエリ"""
        query = """MATCH (n:User {address: $address}) RETURN n"""
        # クエリを実行してトランザクションを取得
        transactions = tx.run(query, address=address)
        return [record["n"] for record in transactions]

    post_logs = PostLogs(DB_URL)

    # メソッド実行
    post_logs.save_adress(sample_logs)

    # 検証
    driver = GraphDatabase.driver(DB_URL)
    for log in sample_logs:
        with driver.session() as session:
            transactions = session.execute_read(fetch_transaction, log.from_address)
            assert transactions[0]["address"] == log.from_address
    
def test_save_relationship(sample_logs):
    """save_relationshipメソッドのテスト"""
    contract_address = "0x50cA110B20FebEF46647c9bd68cAF848c56d9d03"

    def fetch_transaction(tx, address):
        """指定されたアドレスのトランザクションを取得するクエリ"""
        query = """MATCH p=()-[r:TRANSFER {contractAddress: $address}]->() RETURN p"""
        # クエリを実行してトランザクションを取得
        transactions = tx.run(query, address=address)
        return [record["p"] for record in transactions]

    # PostLogsのインスタンスを作成
    post_logs = PostLogs(DB_URL)
    # メソッド実行
    post_logs.save_relationship(contract_address, sample_logs)

    # 検証
    transactions = []
    driver = GraphDatabase.driver(DB_URL)
    with driver.session() as session:
        transactions = session.execute_read(fetch_transaction, contract_address)

    for transaction in transactions:
        # トランザクションのパスを取得
        path = transaction
        start_node = path.start_node
        end_node = path.end_node
        assert start_node["address"] in [log.from_address for log in sample_logs]
        assert end_node["address"] in [log.to_address for log in sample_logs]
