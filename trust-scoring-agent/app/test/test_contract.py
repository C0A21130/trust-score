from tools.tools import get_tools
from tools.contract import Contract

RPC_URL = "http://10.203.92.71:8545"
URL = "http://trust-engine:9000"
TOKEN_CONTRACT_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
SCORING_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def test_add_edges():
    # Act
    contract = Contract(
        rpc_url=RPC_URL,
        token_contract_address=TOKEN_CONTRACT_ADDRESS,
        scoring_contract_address=SCORING_CONTRACT_ADDRESS,
        private_key=PRIVATE_KEY
    )
    result = contract.add_edges()

    # Assert
    assert result is not None
    assert isinstance(result, list)

def test_regist_score():
    # Arrange
    tools = get_tools(
        rpc_url=RPC_URL,
        url=URL,
        token_contract_address=TOKEN_CONTRACT_ADDRESS,
        scoring_contract_address=SCORING_CONTRACT_ADDRESS,
        private_key=PRIVATE_KEY
    )
    regist_score = tools[0]
    address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    score = 0.1

    # Act
    result = regist_score.invoke({"address": address, "score": score})

    # Assert
    assert result is None

def test_get_score():
    # Arrange
    tools = get_tools(
        rpc_url=RPC_URL,
        url=URL,
        token_contract_address=TOKEN_CONTRACT_ADDRESS,
        scoring_contract_address=SCORING_CONTRACT_ADDRESS,
        private_key=PRIVATE_KEY
    )
    get_score = tools[1]
    address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

    # Act
    score = get_score.invoke({"address": address})
    print(score)

    # Assert
    assert score is not None
    assert isinstance(score, int)
