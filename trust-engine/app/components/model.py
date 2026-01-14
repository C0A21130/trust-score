import torch
from torch_geometric.nn import GCNConv
from pydantic import BaseModel

class GraphEncoder(torch.nn.Module):
    def __init__(self, in_channels, out_channels, dropout=0.2):
        super(GraphEncoder, self).__init__()
        self.conv1 = GCNConv(in_channels, 2 * out_channels)
        self.conv_mu = GCNConv(2 * out_channels, out_channels)
        self.conv_logstd = GCNConv(2 * out_channels, out_channels)
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.dropout(x)
        return self.conv_mu(x, edge_index), self.conv_logstd(x, edge_index)

class GenerateRequestBody(BaseModel):
    contract_address: str
    transactions: list = None
