# 本番環境への移行ガイド

テスト用API (`../test/server.py`) がうまく動いたら、この手順で本番向け構成へ移行します。
本番アプリ (`app.py`) は **テスト用と同じエンドポイント**を提供するので、
クライアント側の変更は基本的に不要です。

## テスト版と本番版の違い

| 項目             | テスト版 (`../test/server.py`)      | 本番版 (`app.py`)                          |
| ---------------- | ----------------------------------- | ------------------------------------------ |
| 依存ライブラリ   | なし（標準ライブラリのみ）          | Flask + waitress（`pip install` 必要）     |
| HTTP サーバー    | 開発用 `http.server`                | 本番用 WSGI サーバー `waitress`            |
| データ保存       | メモリ（再起動で消える）            | SQLite ファイルに永続化                    |
| 同時アクセス     | 簡易対応                            | waitress のワーカーで安定処理              |
| 用途             | 動作確認・試作                      | 実運用                                     |

> テスト版はエンドポイントの契約（リクエスト/レスポンス形式）を本番版と揃えてあります。
> そのため「テストで確認 → 本番へ」がスムーズに行えます。

## 手順

### 1. Python と依存ライブラリの準備（初回のみ）

```bat
cd api\prod
python -m pip install -r requirements.txt
```

### 2. ローカルで本番アプリを確認

```bat
python app.py
```

`http://127.0.0.1:8000/health` にアクセスして `status: ok` が返れば成功です。
（`app.py` を直接実行すると Flask の開発サーバーで起動します。動作確認用です。）

### 3. 本番サーバー（waitress）で起動

本番では開発サーバーではなく **waitress** で動かします。Windows でそのまま動く WSGI サーバーです。

```bat
serve.bat
```

または手動で：

```bat
python -m waitress --host=0.0.0.0 --port=8000 app:app
```

- `--host=0.0.0.0` … 同じネットワーク内の他PCからアクセス可能にする
- `--host=127.0.0.1` … このPC内からのみアクセス可能

### 4. 設定（環境変数）

| 環境変数  | 説明                       | 既定値              |
| --------- | -------------------------- | ------------------- |
| `HOST`    | バインドするホスト         | `0.0.0.0`（serve.bat） |
| `PORT`    | 待ち受けるポート           | `8000`              |
| `DB_PATH` | SQLite ファイルのパス      | `data.sqlite3`      |

```bat
set PORT=80
set DB_PATH=C:\api-data\items.sqlite3
serve.bat
```

## 本番運用のチェックリスト

- [ ] **Windows サービス化** — PCログオン時に自動起動させる場合。
      [NSSM](https://nssm.cc/) を使うと `python -m waitress ... app:app` を
      サービスとして登録できます（例は下記）。
- [ ] **ファイアウォール** — 使用ポート（例: 8000）の受信を許可する。
      `netsh advfirewall firewall add rule name="SampleAPI" dir=in action=allow protocol=TCP localport=8000`
- [ ] **リバースプロキシ / HTTPS** — 外部公開する場合は IIS や nginx を前段に置き、
      TLS 終端させる（waitress を直接インターネットに晒さない）。
- [ ] **CORS の見直し** — 現在は `*`（全許可）。本番では呼び出し元ドメインに限定する。
- [ ] **バックアップ** — `DB_PATH` の SQLite ファイルを定期バックアップ。
- [ ] **ログ** — 標準出力を運用ログとして残す（サービス化時はログファイルへ）。

### NSSM による Windows サービス化の例

```bat
REM nssm.exe を入手して実行
nssm install SampleAPI "C:\Python312\python.exe" "-m waitress --host=0.0.0.0 --port=8000 app:app"
nssm set SampleAPI AppDirectory "C:\path\to\api\prod"
nssm start SampleAPI
```

## さらに拡張したいとき

- **認証** … APIキーや Bearer トークンを `before_request` で検証する
- **DB を強化** … 同時書き込みが多い場合は PostgreSQL / MySQL へ移行（SQLAlchemy 併用）
- **入力バリデーション** … pydantic などでリクエストを厳密に検証
- **自動ドキュメント** … より本格化するなら FastAPI へ移行すると OpenAPI が自動生成される
