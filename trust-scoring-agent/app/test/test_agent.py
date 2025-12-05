import os
import requests
import pytest
from dotenv import load_dotenv
from web3 import Web3
from app.components.trust_scoring_agent import TrustScoringAgent

load_dotenv()
agent_url = "http://trust-scoring-agent:5000"

def test_agent_faucet():
    # Arrange
    w3 = Web3()
    address = w3.eth.account.create().address

    # Act
    agent = TrustScoringAgent(
        model=None,
        blockchain_url=os.getenv("RPC_URL"),
        engine_url=os.getenv("TRUST_ENGINE_URL"),
        token_contract_address=os.getenv("TOKEN_CONTRACT_ADDRESS"),
        scoring_contract_address=os.getenv("SCORING_CONTRACT_ADDRESS"),
        private_key=os.getenv("PRIVATE_KEY")
    )
    result = agent.faucet(address)

    # Assert
    assert result is True 

def test_api_faucet():
    load_dotenv()
    w3 = Web3()
    address = w3.eth.account.create().address
    url = f"{agent_url}/faucet?address={address}"

    header = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=header)
    result_json = response.json()

    # Assert
    assert isinstance(result_json["message"], str)

@pytest.mark.parametrize(
    ["contract_address", "from_address", "to_address_list"],
    [
        (
            "0x32F4866B63CaDeD01058540Cff9Bb1fcC05E1cb7",
            "0x85381B8892fa5AaC9c740c625806992c7728dC46",
            [
                "0x87F1CAbAf32cf952E53C4f817c146F68be17316d"
            ]
        ),
        (
            "0x32F4866B63CaDeD01058540Cff9Bb1fcC05E1cb7",
            "0x85381B8892fa5AaC9c740c625806992c7728dC46",
            [
                "0x87F1CAbAf32cf952E53C4f817c146F68be17316d",
                "0xaf84E1C4FDaC978A23CC39e048FB0c40761FE179"
            ]
        ),
        (
            "0x32F4866B63CaDeD01058540Cff9Bb1fcC05E1cb7",
            "0x5efB7cFD76F2eF2875D9344f27dC97e6f0Ed0297",
            [
                "0x87F1CAbAf32cf952E53C4f817c146F68be17316d",
                "0x6548361D4BB907FD65De3aAa7927ca894095F3bf"
            ]
        )
    ]
)
def test_auth_api_users(contract_address, from_address, to_address_list):
    load_dotenv()
    url = f"{agent_url}/auth"

    # Act
    header = {
        "Content-Type": "application/json"
    }
    request_body = {
        "contract_address": contract_address,
        "from_address": from_address,
        "to_address_list": to_address_list
    }
    response = requests.post(url, headers=header, json=request_body)
    response_json = response.json()

    # Assert
    assert "authorized_users" in response_json
    assert "authorized_score_users" in response_json["other"]
    assert "authorized_graph_users" in response_json["other"]
    assert isinstance(response_json["authorized_users"], list)

