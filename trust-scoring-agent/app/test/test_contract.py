import os
from dotenv import load_dotenv
import pytest
from app.components.tools.contract import Contract
from web3 import Web3

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
URL = os.getenv("TRUST_ENGINE_URL")
TOKEN_CONTRACT_ADDRESS = os.getenv("TOKEN_CONTRACT_ADDRESS")
SCORING_CONTRACT_ADDRESS = os.getenv("SCORING_CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

contract = Contract(
    rpc_url=RPC_URL,
    token_contract_address=TOKEN_CONTRACT_ADDRESS,
    scoring_contract_address=SCORING_CONTRACT_ADDRESS,
    private_key=PRIVATE_KEY
)

def test_regist_score():
    # Arrange
    address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    score = 0.1

    # Act
    result = contract.regist_score(address, score)

    # Assert
    assert result is None

@pytest.mark.parametrize(
    "score",
    [
        -1.27, -1.1, -0.1, 0.0, 0.1, 1.1, 1.27
    ]
)
def test_get_score(score):
    # Arrange
    w3 = Web3()
    address = w3.eth.account.create().address

    # Act
    contract.regist_score(address, score)
    result_score = contract.get_score(address)

    # Assert
    assert result_score is not None
    assert isinstance(result_score, float)

@pytest.mark.parametrize(
    ["user1_score", "user2_score", "expected"],
    [
        (0.1, 0.2, False),
        (0.3, 0.1, True),
        (0.5, 0.5, True),
    ]
)
def test_compare_scores(user1_score, user2_score, expected):
    # Arrange
    w3 = Web3()
    user1_address = w3.eth.account.create().address
    user2_address = w3.eth.account.create().address

    # Act
    contract.regist_score(user1_address, user1_score)
    contract.regist_score(user2_address, user2_score)
    score1 = contract.get_score(user1_address)
    score2 = contract.get_score(user2_address)
    result = contract.compare_score(user1_address, user2_address)

    # Assert
    assert score1 is not None
    assert score2 is not None
    assert isinstance(score1, float)
    assert isinstance(score2, float)
    assert result is expected

def test_faucet():
    # Arrange
    w3 = Web3()
    address = w3.eth.account.create().address

    # Act
    result = contract.faucet(address)

    # Assert
    assert result is True 
