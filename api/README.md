# API（テスト用・本番用）

Windows のコマンドプロンプトから Python で実行できる、サンプルAPIの一式です。
まず `test/` で動作を確認し、うまくいったら `prod/` で本番構成へ移行します。

```
api/
├── test/                 テスト用 汎用サンプルAPI（依存なし・すぐ動く）
│   ├── server.py         標準ライブラリだけで動くAPIサーバー
│   ├── run.bat           Windows 用 起動スクリプト
│   ├── README.md         起動方法・動作確認方法
│   └── samples/          呼び出しサンプル
│       ├── client.py     サンプルクライアント（一括動作確認）
│       └── requests.http REST Client 用リクエスト集
│
└── prod/                 本番向けサンプルAPI（Flask + waitress + SQLite）
    ├── app.py            本番アプリ（テストと同じエンドポイント）
    ├── requirements.txt  依存ライブラリ
    ├── serve.bat         Windows 用 本番起動スクリプト
    └── README.md         本番環境への移行ガイド
```

## クイックスタート（テスト）

```bat
cd api\test
python server.py
```

別のコマンドプロンプトで：

```bat
cd api\test\samples
python client.py
```

詳しくは [`test/README.md`](test/README.md) を参照してください。

## 本番へ

テストがうまくいったら [`prod/README.md`](prod/README.md) の移行手順に従ってください。
テスト版と本番版はエンドポイントの形式（リクエスト/レスポンス）を揃えてあるため、
呼び出し側を変えずに移行できます。

## 共通のエンドポイント

| メソッド | パス              | 説明                        |
| -------- | ----------------- | --------------------------- |
| GET      | `/`               | API 情報                    |
| GET      | `/health`         | ヘルスチェック              |
| POST     | `/echo`           | 送った JSON をそのまま返す  |
| GET      | `/api/items`      | アイテム一覧                |
| POST     | `/api/items`      | アイテム作成（`name` 必須） |
| GET      | `/api/items/{id}` | アイテム取得                |
| PUT      | `/api/items/{id}` | アイテム更新                |
| DELETE   | `/api/items/{id}` | アイテム削除                |
