# trust-score

GNNベースの信用スコアリングにより、Web3サービスの初期段階から安全なユーザー間取引を実現する分散型アクセス制御システム

Keywords: Web3, Graph Neural Network(GNN), Network Analysis, Non-Fungible Token(NFT), AI Agent, Blockchain

## Overview

Web3サービスはブロックチェーン技術により、中央管理者やサーバーを持たずに提供される。
しかし、認可サーバーが存在しないため、ユーザー間のアクセス制御が困難であり、安全なサービス提供に課題がある。
Trust Scoreing Systemでは、認可サーバーの代替としてWeb3サービスで機能するシステムである。

- NFT取引ログを基にユーザー間の関係を抽出しユーザーの信用スコアを算出する
- 取引ログをネットワーク構造に変換し、中心性指標から評判・人気度を評価し信用スコアを算出する
- GNNによりリンク予測を行い、初期段階でも安定したスコアリングを実現
- Agentがユーザー情報に応じてデータ取得・スコア計算・アクセス制御を自律的に実行

## System Architecture

システムアーキテクチャを以下に示す。
![Analytics Method](/docs/images/architecture.png)

**システムコンポーネント**
- Turst Scoring Agent
    - ユーザーの信用スコアの情報からアクセス制御する
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
1. trust-scoring-agent
2. trust-engine
3. graph-db
4. document-db

**関連リポジトリ**
- Decentralized Application(DApps)
    - 実際にユーザーが操作するDApps
    - ブロックチェーン上のスマートコントラクトを呼び出すことでNFT取引をする
    - [web3-demo-app](https://github.com/C0A21130/web3-demo-app)
- Contract Agent
    - ユーザーに代わりスマートコントラクトを呼び出すエージェント
    - [contract-agent](https://github.com/C0A21130/contract-agent)
- Blockchain・IPFS
    - Qo-Quorumを利用したブロックチェーン環境とIPFS Kuboを利用したIPFS環境を構築する
    - [web3-infrastructure](https://github.com/c0a22098ea/web3-infrastructure)

## Directory Structure

``` bash
.
├── docs: 開発者用ドキュメント
│   ├── images
│   ├── environment.md
│   ├── trust-engine.md
│   └── trust-scoring-agent.md
├── mongo: オブジェクトデータベースに関わるディレクトリ
├── neo4j: グラフデータベースに関わるディレクトリ
├── trust-engine: NFT取引履歴を分析し信用度を算出する
│   ├── 2023
│   ├── 2024
│   ├── 2025
│   ├── app: 
│   ├── basic: デモンストレーションに関わるディレクトリ, 学習に利用が可能
│   │   ├── 01graph.ipynb: グラフ理論の基礎, グラフ可視化や次数に関わる手法を解説
│   │   ├── 02centrality.ipynb: 中心性分析に関わる手法を解説
│   │   ├── 03search.ipynb: グラフにおける探索に関わる手法を解説
│   │   ├── 04group.ipynb: グラフの分割やコミュニティの抽出に関わる手法を解説
│   │   ├── 05model.ipynb: モデルによるグラフ生成の手法を解説
│   │   ├── gcn.ipynb: GCNに関わる解説
│   │   └── vgae.ipynb: VGAEに関わる解説
│   └── data
└── trust-scoring-agent
    └── app
        ├── components
        └── test
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
- Jupyter-labではネットワーク分析やGNNの動作を確認することが可能である
- [http://localhost:8888](http://localhost:8888)にアクセスすることで利用可能
- [/trust-engine/basic](/trust-engine/basic/)の`ipynb`ファイルを参照することで検証することが可能である

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
