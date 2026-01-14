import networkx as nx

def calculate_centrality(graph: nx.DiGraph) -> dict:
    # 有向グラフの中心性指標を計算
    degree_centrality = nx.in_degree_centrality(graph)
    betweenness_centrality = nx.betweenness_centrality(graph)
    pagerank = nx.pagerank(graph, max_iter=500)

    # 平均値を求める
    average_centrality = {
        "degree": sum(degree_centrality.values()) / len(degree_centrality),
        "betweenness": sum(betweenness_centrality.values()) / len(betweenness_centrality),
        "pagerank": sum(pagerank.values()) / len(pagerank)
    }

    return {
        "degree": degree_centrality,
        "betweenness": betweenness_centrality,
        "pagerank": pagerank,
        "average": average_centrality
    }
