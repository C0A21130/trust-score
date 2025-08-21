import os
import pytest
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from components.models import Log, State
from components.trust_scoring_agent import TrustScoringAgent
from tools.tools import get_tools

@pytest.mark.parametrize(
    [
        "state"
    ],
    [
        pytest.param(
            State(
                messages=[],
                logs=[],
                contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
                my_address="0xdD2FD4581271e230360230F9337D5c0430Bf44C0",
                to_address="0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
                trust_score=None,
                predict_trust_score=None,
                status="thinking",
            ),
            id="no_logs",
        ),
        pytest.param(
            State(
                messages=[],
                logs=[
                    Log(
                        token_id="1",
                        from_address="0x1",
                        to_address="0x2",
                        block_number=123456,
                        gas_price=0.1,
                        gas_used=0.1,
                        contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
                        transaction_hash="0xTransactionHash",
                        token_uri="https://token-uri.com/1"
                    )
                ],
                contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
                my_address="0xdD2FD4581271e230360230F9337D5c0430Bf44C0",
                to_address="0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
                trust_score=0.1,
                predict_trust_score=0.2,
                transfer_status=None,
                status="thinking",
            ),
            id="with_logs",
        ),
    ],
)
def test_trust_agent(state):
    load_dotenv()
    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )
    tools = get_tools(
        rpc_url=os.environ["RPC_URL"],
        url=os.environ["TRUST_ENGINE_URL"],
        token_contract_address=os.environ["TOKEN_CONTRACT_ADDRESS"],
        scoring_contract_address=os.environ["SCORING_CONTRACT_ADDRESS"],
        private_key=os.environ["PRIVATE_KEY"]
    )
    trust_agent = TrustScoringAgent(
        model=model,
        tools=tools
    )
    response = trust_agent.get_agent(
        state=state
    )

    print(response)
    
    if state.trust_score == None:
        assert type(response["logs"]) == list
        assert type(response["contract_address"]) == str
        assert type(response["my_address"]) == str
        assert type(response["to_address"]) == str
        assert response["trust_score"] == None
        assert response["predict_trust_score"] == None
        assert response["status"] == "get_score" or response["status"] == "predict_score"
    else:
        assert type(response["logs"]) == list
        assert all(isinstance(log, Log) for log in response["logs"])
        assert type(response["contract_address"]) == str
        assert type(response["my_address"]) == str
        assert type(response["to_address"]) == str
        assert type(response["trust_score"]) == float
        assert type(response["predict_trust_score"]) == float
        assert type(response["transfer_status"]) == bool
        assert response["status"] == "regist_score"

@pytest.mark.parametrize(
    [
        "state"
    ],
    [
        pytest.param(
            State(
                messages=[],
                logs=[],
                contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
                my_address="0x23d3957BE879aBa6ca925Ee4F072d1A8C4E8c890",
                to_address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                trust_score=None,
                predict_trust_score=None,
                status="predict_score",
            ),
            id="predict_score",
        ),
        pytest.param(
            State(
                messages=[],
                logs=[],
                contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
                my_address="0x23d3957BE879aBa6ca925Ee4F072d1A8C4E8c890",
                to_address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                trust_score=0.1,
                predict_trust_score=0.2,
                status="regist_score",
            ),
            id="regist_score",
        ),
    ],
)
def test_trust_with_tools_agent(state):
    load_dotenv()
    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )
    tools = get_tools(
        rpc_url=os.environ["RPC_URL"],
        url=os.environ["TRUST_ENGINE_URL"],
        token_contract_address=os.environ["TOKEN_CONTRACT_ADDRESS"],
        scoring_contract_address=os.environ["SCORING_CONTRACT_ADDRESS"],
        private_key=os.environ["PRIVATE_KEY"]
    )
    trust_agent = TrustScoringAgent(
        model=model,
        tools=tools
    )
    response = trust_agent.get_bind_tool_agent(
        state=state
    )

    # assert
    assert type(response["logs"]) == list
    assert type(response["contract_address"]) == str
    assert type(response["my_address"]) == str
    assert type(response["to_address"]) == str
    assert response["status"] == "thinking"
    if state.status == "predict_score":
        assert response["trust_score"] != None
        assert response["predict_trust_score"] != None
