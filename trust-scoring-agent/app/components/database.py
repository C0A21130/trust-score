from typing import List
from neo4j import GraphDatabase
from components.models import Log

class Database:
    def __init__(self, url: str) -> None:
        self.driver = GraphDatabase.driver(url)

    @staticmethod
    def _create_addresses(tx, addresses: set) -> None:
        addresses = list(addresses)
        tx.run(
            """
            UNWIND $addresses AS address
            MERGE (u:User {address: address})
            """,
            addresses=addresses
        )

    def save_address(self, logs: List[Log]) -> None:
        """
        NFT取引ログからユーザーのアドレスを保存する
        """

        # Logsのtoとfromアドレスの重複なしリストを作成する
        unique_addresses = set()
        for log in logs:
            unique_addresses.add(log.from_address)
            unique_addresses.add(log.to_address)

        # 重複を排除したアドレスリストをデータベースに保存する
        with self.driver.session() as session:
            session.execute_write(self._create_addresses, unique_addresses)

    @staticmethod
    def _create_relationship(tx, logs: List[Log]) -> None:
        logs = [log.dict() for log in logs]

        # 一括でTRANSFERリレーションシップを作成（重複チェック付き）
        tx.run(
            """
            UNWIND $logs AS log
            MATCH (from:User {address: log.from_address}), (to:User {address: log.to_address})
            MERGE (from)-[:TRANSFER {
                tokenId: log.token_id, 
                contractAddress: log.contract_address, 
                blockNumber: log.block_number,
                gasPrice: log.gas_price,
                gasUsed: log.gas_used,
                tokenUri: log.token_uri
            }]->(to)
            """,
            logs=logs
        )

    def save_relationship(self, logs: List[Log]) -> None:
        """
        NFT取引ログからユーザー間のエッジを保存する
        """
        with self.driver.session() as session:
            session.execute_write(self._create_relationship, logs)
