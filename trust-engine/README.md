# Trust Engine

## Overview
Trust Engineはユーザーの信用スコアを算出するためのTrust Scring Agentのコンポーネントである。

### Library
- **JupyterLab**
    - データサイエンスと機械学習のための統合開発環境
    - ノートブック、コードエディタ、ターミナルが統合
    - データ分析・可視化, 機械学習モデルの開発・実験
- **Neo4j**
    - グラフデータベースNeo4jのPython クライアントライブラリ
    - ノードとエッジのグラフデータを表現, Cypherクエリ言語をサポート
    - ソーシャルネットワーク分析, 知識グラフの構築
- **NetworkX**
    - 複雑なネットワークの作成・操作・分析を行うPythonライブラリ
    - ネットワーク分析機能の実装
    - 中心性分析・ネットワーク可視化
- **PyTorch**
    - 深層学習フレームワーク
    - ニューラルネットワークの構築・訓練
    - CUDA サポートによるGPU加速
- **PyTorch Geometric**
    - グラフニューラルネットワーク(GNN)ライブラリ
    - PyTorch ベースのグラフ深層学習

## Main function

**Centrality**

**database**

**Generate**

**Model**

**Train**

## Components
Trust Engineは2つのコンポーネントから構成される。

1. Centrality Calculator
2. Network Generator

### Centrality Calculator
ネットワークの中心性を活用して信用スコアを算出する。

**Degree Centrality**

**betweenness**

**PageRank**

### Network Generator
GNNを用いてユーザー間のつながりの推定をする。


## Example
ネットワーク分析やGNNの学習に適した資料を`trust-engine/basic`に設置している

- 01graph.ipynb
    - NetworkXの基本的な利用方法について解説している
    - ネットワークの可視化, 次数等
- 02centrality.ipynb
    - NetworkXを活用した中心性分析について解説している
    - 次数中心性, 近傍中心性, 媒介中心性, 固有ベクトル中心性, PageRank
- 03search.ipynb
    - ネットワークにおける経路探索について解説している
    - 経路探索, ダイクストラ法
- 04group.ipynb
    - ネットワークにの分割について解説している
    - ネットワーク分析とネットワークからのコミュニティ抽出
- 05model.ipynb
    - ネットワークモデルを活用した生成手法について解説している
    - ランダムモデル, コンフィグレーションモデル等 
- gcn.ipynb
    - Graph Convolution Network(GCN)について解説している
    - リンク予測
- vgae.ipynb
    - Variational Graph AutoEncoder(VGAE)について解説している
    - ネットワーク生成
- graphrnn.ipynb
    - Graph Recoren Neural Network(GraphRNN)について解説している
    - 順序に基づいたネットワーク生成
