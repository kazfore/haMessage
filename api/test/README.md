# テスト用 汎用サンプルAPI

Python の標準ライブラリだけで動く、テスト用の汎用サンプルAPIです。
**追加インストール（pip install）は不要**で、Windows のコマンドプロンプトから
`python server.py` だけで起動できます。

## 1. 前提

- Windows に **Python 3.7 以降** がインストールされていること
  - インストール時に **「Add python.exe to PATH」にチェック**を入れてください
  - 確認: コマンドプロンプトで `python --version`（または `py --version`）

## 2. 起動方法（Windows コマンドプロンプト）

### 方法A: バッチファイル（かんたん）

`run.bat` をダブルクリック、またはコマンドプロンプトで：

```bat
cd api\test
run.bat
```

### 方法B: python コマンドで直接

```bat
cd api\test
python server.py
```

起動すると次のように表示されます：

```
============================================================
 テスト用 汎用サンプルAPI を起動しました
 URL      : http://127.0.0.1:8000
 ヘルス   : http://127.0.0.1:8000/health
 停止     : Ctrl + C
============================================================
```

停止は **Ctrl + C** です。

### ポート番号を変える

```bat
set PORT=9000
python server.py
```

または引数で：

```bat
python server.py --host 127.0.0.1 --port 9000
```

## 3. エンドポイント一覧

| メソッド | パス                | 説明                         |
| -------- | ------------------- | ---------------------------- |
| GET      | `/`                 | API 情報                     |
| GET      | `/health`           | ヘルスチェック               |
| POST     | `/echo`             | 送った JSON をそのまま返す   |
| GET      | `/api/items`        | アイテム一覧                 |
| POST     | `/api/items`        | アイテム作成（`name` 必須）  |
| GET      | `/api/items/{id}`   | アイテム取得                 |
| PUT      | `/api/items/{id}`   | アイテム更新                 |
| DELETE   | `/api/items/{id}`   | アイテム削除                 |

> データはメモリ上に保持され、サーバーを止めると消えます（テスト用途）。

## 4. 動作確認

### サンプルクライアントで一括確認

別のコマンドプロンプトを開いて：

```bat
cd api\test\samples
python client.py
```

一連のエンドポイントを順に呼び出して結果を表示します。

### curl（コマンドプロンプト / Windows 10 以降は標準搭載）

```bat
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/echo -H "Content-Type: application/json" -d "{\"hello\":\"world\"}"

curl http://127.0.0.1:8000/api/items
```

> コマンドプロンプトの curl では、JSON 内の `"` を `\"` にエスケープしてください。

### PowerShell

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health

Invoke-RestMethod http://127.0.0.1:8000/api/items -Method Post `
  -ContentType 'application/json' `
  -Body '{"name":"PowerShellから作成"}'
```

### ブラウザ

`http://127.0.0.1:8000/health` や `http://127.0.0.1:8000/api/items` を
ブラウザで開けば GET の結果を確認できます。CORS を許可しているので、
HTML/JavaScript からの `fetch()` でも呼び出せます。

## 5. うまくいかないとき

| 症状                                   | 対処                                                            |
| -------------------------------------- | --------------------------------------------------------------- |
| `python は認識されていません`          | Python 未インストール、または PATH 未設定。`py` を試すか再インストール |
| `OSError: [WinError 10048]` (ポート使用中) | `set PORT=9000` など別ポートで起動                             |
| ブラウザ/curl でつながらない           | サーバーが起動しているか、ポート番号が一致しているか確認         |
| 外部PCからアクセスしたい               | `python server.py --host 0.0.0.0` で起動（社内LANのみ推奨）      |

## 6. 本番環境への移行

テストがうまくいったら、`../prod/README.md` を参照してください。
本番向けの構成（WSGI サーバー、永続化、Windows サービス化など）の
移行手順をまとめています。
