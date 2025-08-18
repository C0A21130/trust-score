from web3 import Web3
from eth_account import Account
from tools.ssdlab_token_abi import token_abi
from tools.scoring_abi import scoring_abi

class Contract:

    # コントラクトインスタンスの初期化
    def __init__(self, rpc_url: str, token_contract_address: str, scoring_contract_address: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.token_contract = None
        self.scoring_contract = None
        self.account = None
        self.private_key = private_key
        
        # Connect to the Ethereum network
        if not self.w3.is_connected():
            raise Exception("Failed to connect to the Ethereum network")
        if self.private_key is None:
            raise Exception("Private key is None")
        else:
            self.token_contract = self.w3.eth.contract(address=token_contract_address, abi=token_abi)
            self.scoring_contract = self.w3.eth.contract(address=scoring_contract_address, abi=scoring_abi)
            self.account = Account.from_key(private_key)

    # アカウントのアドレスを取得する関数
    def get_address(self) -> str:
        # This function returns the address of the account.
        return self.account.address

    # トークンの所有者を取得しエッジを追加する関数
    def add_edges(self) -> list:
        tokens = []
        logs = self.token_contract.events.Transfer().get_logs(from_block=0)

        # 取得した取引履歴を基にエッジを追加する
        for log in logs:
            if log["args"]["from"] == "0x0000000000000000000000000000000000000000":
                continue
            if log["args"]["from"] == log["args"]["to"]:
                continue

            token = {
                "from_address": log["args"]["from"],
                "to_address": log["args"]["to"],
                "token_id": log["args"]["tokenId"]
            }

            # エッジを追加するトランザクションを構築
            try:
                tx = self.scoring_contract.functions.addEdge(token["from_address"], token["to_address"]).build_transaction({
                    "from": self.account.address,
                    "gas": 300000,
                    "gasPrice": self.w3.to_wei("50", "gwei"),
                    "nonce": self.w3.eth.get_transaction_count(self.account.address),
                })

                # トランザクションの署名と送信
                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                self.w3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                print(f"Error adding edge: {e}")
                continue

            # トークンをリストに追加
            tokens.append(token)

        return tokens

    def regist_score(self, address: str) -> None:
        self.add_edges()

        # トランザクションを構築
        tx = self.scoring_contract.functions.registScore(address).build_transaction({
            "from": self.account.address,
            "gas": 300000,
            "gasPrice": self.w3.to_wei("50", "gwei"),
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
        })

        # トランザクションの署名と送信をしてスコアを取得
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def get_score(self, address: str) -> int:
        score = self.scoring_contract.functions.ratingOf(address).call()
        return score
