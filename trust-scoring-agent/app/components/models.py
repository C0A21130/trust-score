from pydantic import BaseModel, Field

class Log(BaseModel):
    """
    Represents a log entry.
    """
    token_id: int | None = Field(..., description="The ID of the token associated with the log.")
    from_address: str = Field(..., description="The address from which the log was emitted.")
    to_address: str = Field(..., description="The address to which the log was emitted.")
    transaction_hash: str = Field(..., description="The hash of the transaction that emitted the log.")
    gas_used: float | None = Field(..., description="The amount of gas used in the transaction.")
    gas_price: float | None = Field(..., description="The price of gas for the transaction.")

class Logs(BaseModel):
    """
    Represents a collection of log entries.
    """
    logs: list[Log] = Field(..., description="A list of log entries.")

class RequestLog(BaseModel):
    """
    Represents a request for logs.
    """
    from_address: str = Field(..., description="The address from which the logs are requested.")
    to_address: str = Field(..., description="The address to which the logs are requested.")
    token_id: int = Field(..., description="The ID of the token for which logs are requested.")
    block_number: int = Field(..., description="The block number for which logs are requested.")
    gas_price: float = Field(..., description="The price of gas for the transaction for which logs are requested.")
    gas_used: float = Field(..., description="The amount of gas used in the transaction for which logs are requested.")
    transaction_hash: str = Field(..., description="The hash of the transaction for which logs are requested.")

class RequestLogs(BaseModel):
    """
    Represents a collection of request logs.
    """
    contract_address: str = Field(..., description="The address of the contract for which logs are requested.")
    transfer_logs: list[RequestLog] = Field(..., description="A list of request log entries.")

