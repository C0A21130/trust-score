import networkx as nx

def calculate_centrality(graph: nx.DiGraph) -> dict:
    return {
        "degree": nx.in_degree_centrality(graph),
        "betweenness": nx.betweenness_centrality(graph),
        "pagerank": nx.pagerank(graph, max_iter=500)
    }
