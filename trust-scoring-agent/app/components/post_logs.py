from neo4j import GraphDatabase
from .models import Logs

class PostLogs:
    def __init__(self, url: str) -> None:
        self.driver = GraphDatabase.driver(url)

    def save_adress(self, logs: Logs) -> None:
        # Logsのtoとfromアドレスの重複なしリストを作成する
        unique_addresses = set()
        for log in logs:
            unique_addresses.add(log.from_address)
            unique_addresses.add(log.to_address)

        with self.driver.session() as session:
            session.execute_write(self._create_addresses, unique_addresses)

    @staticmethod
    def _create_addresses(tx, addresses):
        # 配列に含まれるアドレスをまとめて作成
        for address in addresses:
            tx.run("CREATE (u:User {address: $address}) RETURN u", address=address)

    def save_relationship(self, contract_address: str, logs: Logs) -> None:
        with self.driver.session() as session:
            session.execute_write(self._create_relationship, contract_address, logs)

    @staticmethod
    def _create_relationship(tx, contract_address: str, logs: Logs):
        for log in logs:
            # from_addressとto_addressの間にTRANSFERリレーションシップを作成
            tx.run(
                """
                MATCH (from:User {address: $from_address}), (to:User {address: $to_address})
                CREATE (from)-[:TRANSFER {tokenId: $tokenId, contractAddress: $contractAddress, gasPrice: $gasPrice, gasUsed: $gasUsed}]->(to)
                """,
                from_address=log.from_address,
                to_address=log.to_address,
                tokenId=log.token_id,
                contractAddress=contract_address,
                gasPrice=log.gas_price,
                gasUsed=log.gas_used
            )
        

