from typing import List, Literal, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class Log(BaseModel):
    """
    Blockchain transaction log
    """
    token_id: str = Field(..., description="The ID of the token for which logs are requested.")
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

class State(BaseModel):
    """
    The state for trust scoring agent 
    """
    messages: Annotated[List[BaseMessage], add_messages] = []
    logs: List[Log] = []
    contract_address: str = ""
    my_address: str = ""
    to_address: str = ""
    trust_score: float | None = None
    predict_trust_score: float | None = None
    transfer_status: bool | None = None
    status: Literal["start", "regist_score", "get_score", "predict_score", "thinking"] = "start"

class OutputJson(BaseModel):
    message: str = Field(..., description="判断した理由")
    transfer_status: bool | None = Field(None, description="NFT取引の可否, Trueなら取引可能")
    status: Literal["regist_score", "get_score", "predict_score"] = Field(..., description="情報が不足している場合はregist_score、情報が十分であればpredict_scoreとする。")
