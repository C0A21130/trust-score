from typing import List, Literal, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class Log(BaseModel):
    """
    Blockchain transaction log
    """
    token_id: str = Field(..., description="The ID of the NFT for which logs are requested.")
    from_address: str = Field(..., description="The address from which the logs are requested.")
    to_address: str = Field(..., description="The address to which the logs are requested.")
    block_number: int = Field(..., description="The block number for which logs are requested.")
    gas_price: float = Field(..., description="The price of gas for the transaction for which logs are requested.")
    gas_used: float = Field(..., description="The amount of gas used in the transaction for which logs are requested.")
    contract_address: str = Field(..., description="The address of the contract for which logs are requested.")
    transaction_hash: str = Field(..., description="The hash of the transaction for which logs are requested.")
    token_uri: str = Field(..., description="The URI of the token for which logs are requested.")

class RequestLogs(BaseModel):
    """
    The request body for posting transfer logs
    """
    contract_address: str = Field(..., description="The address of the contract for which logs are requested.")
    transfer_logs: list[Log] = Field(..., description="A list of request log entries.")

class AuthRequestBody(BaseModel):
    """
    The request body for user authentication
    """
    from_address: str = Field(..., description="The address of the user to authenticate.")
    to_address_list: List[str] = Field(..., description="The addresses of the users to authenticate.")

class User(BaseModel):
    """
    Information about a user in the trust scoring system.
    """
    address: str = Field(..., description="The address of the user.")
    trust_score: float | None = Field(None, description="The trust score of the user.")
    predict_trust_score: float | None = Field(None, description="The predicted trust score of the user.")
    info: str = Field(..., description="Additional information about the user.")

class State(BaseModel):
    """
    The state for trust scoring agent 
    """
    messages: Annotated[List[BaseMessage], add_messages] = []
    my_info: User = Field(..., description="Information about the user's own wallet address.")
    transfer_partners: List[User] = []
    authorized_user: User | None = Field(..., description="The authorized one user.")
    status: Literal["start", "thinking", "tool", "end"] = "start"

class OutputJson(BaseModel):
    """
    The output format for the trust scoring agent.
    """
    message: str = Field(..., description="The message to be authorized to the user.")
    authorized_user: User | None = Field(None, description="The information of the user who was authorized as a result.")
    status: Literal["thinking", "tool", "end",] = Field(..., description="If the trading partner can be approved, it will be `end`. If the trading partner cannot be selected, it will be `tool`.")
