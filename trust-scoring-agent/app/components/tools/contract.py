from web3 import Web3
from eth_account import Account
from .abi import token_abi, scoring_abi

class Contract:
    def __init__(self, rpc_url: str, token_contract_address: str, scoring_contract_address: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.token_contract = None
        self.scoring_contract = None
        self.account = None
        self.private_key = private_key

        # Ethereumネットワークへの接続
        if not self.w3.is_connected():
            raise Exception("Failed to connect to the Ethereum network")
        elif self.private_key is None:
            raise Exception("Private key is None")
        else:
            self.token_contract = self.w3.eth.contract(address=token_contract_address, abi=token_abi)
            self.scoring_contract = self.w3.eth.contract(address=scoring_contract_address, abi=scoring_abi)
            self.account = Account.from_key(private_key)

    def regist_score(self, address: str, score: float) -> None:
        """
        信用スコアをブロックチェーンに登録する
        """
        score = int(score * 100)

        # トランザクションを構築
        tx = self.scoring_contract.functions.rate(address, score).build_transaction({
            "from": self.account.address,
            "gas": 300000,
            "gasPrice": self.w3.to_wei("50", "gwei"),
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
        })

        # トランザクションの署名と送信をしてスコアを取得
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def get_score(self, address: str) -> float:
        """
        ブロックチェーンに登録された信用スコアを検索して取得する
        """
        score = self.scoring_contract.functions.ratingOf(address).call()
        return float(score) / 100.0

    def compare_score(self, address1: str, address2: str) -> float:
        """
        2つのアドレスの信用スコアを比較する
        """
        result_auth = self.scoring_contract.functions.compare(address1, address2).call()
        return result_auth

    def faucet(self, address: str) -> bool:
        """
        スマートコントラクトにETHを送信し、指定したアドレスにスマートコントラクトからETHを送信する
        """
        chain_id = self.w3.eth.chain_id
        if chain_id == 1337:
            gasprice = self.w3.to_wei("0", "gwei")
        elif chain_id == 31337:
            gasprice = self.w3.to_wei("50", "gwei")

        # 指定したコントラクトアドレスにETHを送信
        try: 
            tx1 = {
                "to": self.token_contract.address,
                "value": self.w3.to_wei(0.31, "ether"),
                "from": self.account.address,
                "gas": 600000,
                "gasPrice": gasprice,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "chainId": chain_id
            }
            signed_tx1 = self.w3.eth.account.sign_transaction(tx1, private_key=self.private_key)
            tx_hash1 = self.w3.eth.send_raw_transaction(signed_tx1.raw_transaction)
            self.w3.eth.wait_for_transaction_receipt(tx_hash1)
        except Exception as e:
            print(f"Error sending ether: {e}")
            return False

        # 指定したアドレスにETHを送信
        try:
            tx2 = self.token_contract.functions.faucet(address).build_transaction({
                "from": self.account.address,
                "gas": 600000,
                "gasPrice": gasprice,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "chainId": chain_id
            })
            signed_tx2 = self.w3.eth.account.sign_transaction(tx2, private_key=self.private_key)
            tx_hash2 = self.w3.eth.send_raw_transaction(signed_tx2.raw_transaction)
            self.w3.eth.wait_for_transaction_receipt(tx_hash2)
        except Exception as e:
            print(f"Error sending faucet transaction: {e}")
            return False
        return True
