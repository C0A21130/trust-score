# trust-score

GNNベースの信用スコアリングにより、Web3サービスの初期段階から安全なユーザー間取引を実現する分散型アクセス制御システム

Keywords: Web3, Graph Neural Network(GNN), Network Analysis, Non-Fungible Token(NFT), AI Agent, Blockchain

## Overview
Trust Scoreing Systemは、Web2サービスにおけるユーザーの信用度に基づいてアクセス制御するシステムである。
過去のNon-Fungible Token(NFT)の取引履歴からユーザーの間の関係をネットワーク形式で構築する。
Graph Nuural Network(GNN)の中でもVGAE(Variational Graph Auto-Encoder)を活用してネットワークに対してリンク予測することにより，ユーザー間のつながり度合いを推定する。
つながり度合いを推定した過去の取引履歴からユーザーの信用度を算出する。

## システムアーキテクチャ

![System Architecture](/docs/images/architecture.png)

**システムコンポーネント**
- Turst Scoring Agent
    - NFT取引履歴をグラフDBに記録することやスマートコントラクトの呼び出しによる信用スコアの登録を行う
    - 詳細については[trust-scoring-agent.md](/docs/trust-scoring-agent.md)を参照
- Trust Engine
    - Trust Scoring Agentのリクエストを受けてユーザーの信用スコアを算出する
    - 詳細については[trust-engine.md](/docs/trust-engine.md)を参照
- Graph Database
    - NFT取引ネットワークを記録するデータベース
    - 取引ネットワーク: ユーザーをノード・NFT取引をエッジ
    - ノード: ユーザーのウォレットアドレス
    - エッジ: ブロック番号、コントラクトアドレス、GasPrice、GasUsed、トークンID、トークンURI

**コンテナ**
[docker-compose.yml](docker-compose.yml) で定義される4つのサービスが連携して動作する。
1. trust-scoring-agent: [trust-scoring-agent/Dockerfile](trust-scoring-agent/Dockerfile) をビルドし、FastAPI ベースのエージェントを `:5000` で公開。`./trust-scoring-agent/app` をボリュームとしてマウントする
2. trust-engine: [trust-engine/Dockerfile](trust-engine/Dockerfile) をビルドしCUDA 12.9 + Python 3.13 環境でGNNを実行し、`uvicorn`と`jupyter-lab`を同一コンテナで起動する
3. graph-db: 公式 `neo4j:community` イメージを使用し、ポート `7474/7687` を公開、`./neo4j/{data,logs,conf}` を Neo4j の `/data`, `/logs`, `/conf` にマウントしてトランザクションログや設定を永続化する

**関連リポジトリ**
- 分散型アプリケーション
    - 実際にユーザーが操作する分散型アプリケーション
    - ブロックチェーン上のスマートコントラクトを呼び出すことでNFT取引をする
    - ユーザーはブロックチェーン上に記録されたスマートコントラクトを基にアクセス制御をする
    - [web3-demo-app](https://github.com/C0A21130/web3-demo-app)
- Contract Agent
    - ユーザーに代わりスマートコントラクトを呼び出すエージェント
    - [contract-agent](https://github.com/C0A21130/contract-agent)
- Blockchain・IPFS
    - Qo-Quorumを利用したブロックチェーン環境とIPFS Kuboを利用したIPFS環境を構築する
    - [blockchain](https://github.com/C0A21130/web3-demo-app/blob/main/docs/blockchain/blockchian.md)

## Directory Structure

``` bash
.
├── docs: 開発者用ドキュメント
│   ├── basic.md: ネットワーク分析やGNNの学習用ドキュメント
│   ├── environment.md: CUDA+Docker環境の構築方法の手順書
│   ├── trust-engine.md: トラストエンジンの仕様書
│   └── trust-scoring-agent.md: トラストスコアリングエージェントの仕様書
├── mongo: オブジェクトデータベースに関わるディレクトリ
├── neo4j: グラフデータベースに関わるディレクトリ
├── trust-engine: トラストエンジンに関するソースコード
│   ├── 2025
│   │   └── master-thesis.ipynb: 修論用の実験結果
│   ├── app
│   │   ├── components: モデルの学習・リンク予測・中心性算出を行うコンポーネント
│   │   ├── test: トラストエンジンのテストコード
│   │   └── main.py: Fast APIによるエンドポイント
│   ├── basic: デモンストレーションに関わるディレクトリ, 学習に利用が可能
│   │   ├── 01graph.ipynb: グラフ理論の基礎, グラフ可視化や次数に関わる手法を解説
│   │   ├── 02centrality.ipynb: 中心性分析に関わる手法を解説
│   │   ├── 03search.ipynb: グラフにおける探索に関わる手法を解説
│   │   ├── 04group.ipynb: グラフの分割やコミュニティの抽出に関わる手法を解説
│   │   ├── 05model.ipynb: モデルによるグラフ生成の手法を解説
│   │   ├── gcn.ipynb: GCNに関わる解説
│   │   └── vgae.ipynb: VGAEに関わる解説
│   ├── Dockerfile: CUDA+Pytorch Geometricsのコンテナイメージ作成ファイル
│   └── requirements.txt: インストールするpipライブラリ一覧
└── trust-scoring-agent: 信用スコアリングエージェントに関するソースコード
    ├── app
    │   ├── components: 各種ツールを呼び出しやエージェントに関するコンポーネント
    │   ├── test: 信用スコアリングエージェントのテストコード
    │   └── tools: スマートコントラクトやトラストエンジンの呼び出しを行うツール
    ├── Dockerfile: CUDA+Pytorch Geometricsのコンテナイメージ作成ファイル
    └── requirements.txt: インストールするpipライブラリ一覧
```

## Getting Started

もしGPUを利用した環境を構築する場合は[GPU Environment Construction](/docs/environment.md)を参照

リポジトリをクローンする。
```bash
git clone https://github.com/C0A21130/trust-score.git
```

コンテナを起動する
```bash
cd trust-score
docker-compose up -d
```

以下のシステムにアクセスすることで利用可能

**Trust Scoring Agent**
- [http://localhost:5000/docs](http://localhost:5000)にアクセス

**Trust Engine**
- [http://localhost:9000/docs](http://localhost:9000)にアクセス

**Jupyter-lab**
- Jupyter-labではネットワーク分析やGNNの動作の確認や基本的な実装方法を参照することが可能である
- [http://localhost:8888](http://localhost:8888)からアクセスし[/trust-engine/basic](/trust-engine/basic/)の`ipynb`ファイルを参照することで利用することが可能である
- より詳しい説明については[basic.md](/docs/basic.md)を参照

## Reference

- 経営情報学会　2024年度年次大会
    - [Web3サービス上の取引に向けた信用スコアリングの提案](https://jasmin2024annual.peatix.com/)
    - 2024年6月
- 情報処理学会　ソフトウェアエンジニアリングシンポジウム2024
    - [Web3サービスにおけるトラストモデルの提案](https://ipsj.ixsq.nii.ac.jp/ej/?action=pages_view_main&active_action=repository_view_main_item_detail&item_id=239284&item_no=1&page_id=13&block_id=8)
    - 2024年9月
- 日本機械学会　Journal of Advanced Mechanical Design, Systems, and Manufacturing
    - [A trustworthy architecture for Web3 service](https://www.jstage.jst.go.jp/article/jamdsm/18/7/18_2024jamdsm0095/_article/-char/en)
    - 2024年11月
- 日本機械学会　第35回設計工学・システム部門講演会
    - [Web3コミュニティ成長に伴う信頼モデルと認可の実現](https://pub.confit.atlas.jp/ja/event/dsdconf25)
    - 2025年9月
- 情報処理学会　ソフトウェアエンジニアリングシンポジウム2025
    - [コミュニティ萌芽期における繋がりの推定と信用のモデル化](https://ses.sigse.jp/2025/program.html)
    - 2025年9月
