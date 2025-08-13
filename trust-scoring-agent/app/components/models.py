from pydantic import BaseModel, Field

class Log(BaseModel):
    """
    Represents a request for logs.
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
    Represents a collection of request logs.
    """
    contract_address: str = Field(..., description="The address of the contract for which logs are requested.")
    transfer_logs: list[Log] = Field(..., description="A list of request log entries.")

