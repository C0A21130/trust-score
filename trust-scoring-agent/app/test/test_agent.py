import os
import pytest
import requests
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from components.models import User, State
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
                my_info=User(
                    address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                    trust_score=None,
                    predict_trust_score=None,
                    info=""
                ),
                transfer_partners=[
                    User(
                        address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                        trust_score=None,
                        predict_trust_score=None,
                        info=""
                    )
                ],
                authorized_user=None,
                status="thinking"
            ),
            id="No Score and No Info",
        ),
        pytest.param(
            State(
                messages=[],
                my_info=User(
                    address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                    trust_score=0.3,
                    predict_trust_score=0.5,
                    info="This is my info"
                ),
                transfer_partners=[
                    User(
                        address="0x98afe053cD420e9308AEdE91731a03Cd1260808a",
                        trust_score=0.1,
                        predict_trust_score=0.2,
                        info="This is user1 info"
                    ),
                    User(
                        address="0x3A16907e3BA7e5663282cce0613dB47635bDCE4d",
                        trust_score=0.2,
                        predict_trust_score=0.4,
                        info="This is user2 info"
                    )
                ],
                authorized_user=None,
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
        tools=tools,
        contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
    )
    response = trust_agent.get_agent(
        state=state
    )

    print(response)

    if state.my_info.trust_score == None:
        assert type(response.my_info) == User
        assert type(response.transfer_partners) == list
        assert all(isinstance(partner, User) for partner in response.transfer_partners)
        assert response.authorized_user is None
        assert response.status == "tool"
    else:
        assert type(response.my_info) == User and response.my_info.trust_score == state.my_info.trust_score
        assert type(response.transfer_partners) == list
        assert all(isinstance(partner, User) for partner in response.transfer_partners)
        assert type(response.authorized_user) == User and response.authorized_user.trust_score == state.transfer_partners[1].trust_score
        assert response.status == "end"

@pytest.mark.parametrize(
    [
        "state"
    ],
    [
        pytest.param(
            State(
                messages=[],
                my_info=User(
                    address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                    trust_score=None,
                    predict_trust_score=None,
                    info=""
                ),
                transfer_partners=[
                    User(
                        address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                        trust_score=None,
                        predict_trust_score=None,
                        info=""
                    )
                ],
                authorized_user=None,
                status="tool"
            ),
            id="Predict Score",
        ),
        pytest.param(
            State(
                messages=[],
                my_info=User(
                    address="0x3B2C649350577c0BFc9875E8C2aeB4ec8141A00A",
                    trust_score=0.3,
                    predict_trust_score=0.5,
                    info=""
                ),
                transfer_partners=[
                    User(
                        address="0x98afe053cD420e9308AEdE91731a03Cd1260808a",
                        trust_score=0.1,
                        predict_trust_score=0.2,
                        info=""
                    ),
                    User(
                        address="0x808B9A2191BB9A0Ea26849B77feFDAa2825D6d84",
                        trust_score=0.1,
                        predict_trust_score=0.2,
                        info=""
                    )
                ],
                authorized_user=None,
                status="tool",
            ),
            id="Get Transaction",
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
        tools=tools,
        contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
    )
    response = trust_agent.get_bind_tool_agent(
        state=state
    )

    print(response)

    # assert
    assert type(response) == State
    assert response.status == "thinking"
    assert type(response.my_info) == User
    assert type(response.transfer_partners) == list
    assert all(isinstance(partner, User) for partner in response.transfer_partners)
    if state.status == "predict_score":
        assert response.my_info.trust_score != None
        assert response.my_info.predict_trust_score != None
        assert response.transfer_partners[0].trust_score != None
        assert response.transfer_partners[0].predict_trust_score != None
    elif state.status == "get_transaction":
        assert response.transfer_partners[0].info != ""

def test_create_info():
    load_dotenv()
    token_uri = "data:application/json;base64,eyJuYW1lIjoiRm91bmRyeSBDb3Vyc2UgTkZUIiwgImRlc2NyaXB0aW9uIjogIkN5ZnJpbiBGb3VuZHJ5IEZ1bGwgQ291cnNlOiDwn46yIEkgQU0gVEhFIFJBTkRPTU5FU1MgTUFTVEVSISEhIEkgSEFWRSBGT1VORCBNWSBGSVJTVCBFWFBMT0lUISEiLCAiYXR0cmlidXRlcyI6IFt7InRyYWl0X3R5cGUiOiAiUk5HLCBBdXRvbWF0aW9uLCBhbmQgT3JhY2xlbmVzcyIsICJ2YWx1ZSI6IDEwMH1dLCAiaW1hZ2UiOiJpcGZzOi8vUW1kcVZDRlRBaXJIVzd0RDFZcFZLbnFRRkRoUmQ4VW9wUWRMVHJtV0JqTmZyMyJ9"
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
        tools=tools,
        contract_address="0x76B50696B8EFFCA6Ee6Da7F6471110F334536321",
    )
    image_description = trust_agent.create_info(token_uri)
    print(image_description)

def test_auth_api():
    url = "http://trust-scoring-agent:5000/auth"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "from_address": "0x98afe053cD420e9308AEdE91731a03Cd1260808a",
        "to_address_list": [
            "0x3A16907e3BA7e5663282cce0613dB47635bDCE4d",
            "0xCc8188e984b4C392091043CAa73D227Ef5e0d0a7",
            "0x808B9A2191BB9A0Ea26849B77feFDAa2825D6d84"
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response_body = response.json()
    print(response_body)

    assert response.status_code == 200
    assert "messages" in response_body
    assert "user" in response_body
