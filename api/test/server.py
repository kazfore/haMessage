#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト用 汎用サンプルAPIサーバー (Python 標準ライブラリのみ)

依存ライブラリなし。Windows のコマンドプロンプトで以下だけで起動できます。

    python server.py

環境変数または引数でホスト/ポートを変更できます。

    set PORT=9000
    python server.py --host 127.0.0.1 --port 9000

提供エンドポイント (汎用サンプル):
    GET    /                 API 情報
    GET    /health           ヘルスチェック
    POST   /echo             送られた JSON をそのまま返す
    GET    /api/items        アイテム一覧
    POST   /api/items        アイテム作成      body: {"name": "...", ...}
    GET    /api/items/{id}   アイテム取得
    PUT    /api/items/{id}   アイテム更新      body: {"name": "...", ...}
    DELETE /api/items/{id}   アイテム削除

データはメモリ上に保持されます (再起動で消えます / テスト用途)。
CORS を許可しているのでブラウザの HTML からも直接呼び出せます。
"""

import argparse
import json
import os
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ----------------------------------------------------------------------------
# 簡易インメモリ・データストア (スレッドセーフ)
# ----------------------------------------------------------------------------


class ItemStore:
    """メモリ上でアイテムを管理する簡単なストア。テスト用。"""

    def __init__(self):
        self._items = {}
        self._next_id = 1
        self._lock = threading.Lock()
        # サンプルの初期データを投入
        self.create({"name": "サンプル1", "note": "最初のアイテムです"})
        self.create({"name": "サンプル2", "note": "2番目のアイテムです"})

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def list(self):
        with self._lock:
            return [dict(v) for v in self._items.values()]

    def get(self, item_id):
        with self._lock:
            item = self._items.get(item_id)
            return dict(item) if item else None

    def create(self, data):
        with self._lock:
            item_id = self._next_id
            self._next_id += 1
            item = dict(data)
            item["id"] = item_id
            item["created_at"] = self._now()
            item["updated_at"] = item["created_at"]
            self._items[item_id] = item
            return dict(item)

    def update(self, item_id, data):
        with self._lock:
            item = self._items.get(item_id)
            if not item:
                return None
            for key, value in data.items():
                if key not in ("id", "created_at"):
                    item[key] = value
            item["updated_at"] = self._now()
            return dict(item)

    def delete(self, item_id):
        with self._lock:
            return self._items.pop(item_id, None) is not None


STORE = ItemStore()


# ----------------------------------------------------------------------------
# HTTP ハンドラ
# ----------------------------------------------------------------------------


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "SampleTestAPI/1.0"

    # ---- 共通ユーティリティ -------------------------------------------------

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_cors()
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        """リクエストボディを JSON として読む。失敗時は (None, error_message)。"""
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}, None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8")), None
        except (ValueError, UnicodeDecodeError) as exc:
            return None, "リクエストボディが正しい JSON ではありません: %s" % exc

    def _path_parts(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        return [p for p in path.split("/") if p != ""]

    # ---- メソッドディスパッチ ----------------------------------------------

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parts = self._path_parts()

        if not parts:
            self._send_json(200, {
                "name": "テスト用 汎用サンプルAPI",
                "version": "1.0",
                "endpoints": [
                    "GET    /health",
                    "POST   /echo",
                    "GET    /api/items",
                    "POST   /api/items",
                    "GET    /api/items/{id}",
                    "PUT    /api/items/{id}",
                    "DELETE /api/items/{id}",
                ],
            })
            return

        if parts == ["health"]:
            self._send_json(200, {
                "status": "ok",
                "time": datetime.now(timezone.utc).isoformat(),
            })
            return

        if parts == ["api", "items"]:
            items = STORE.list()
            self._send_json(200, {"count": len(items), "items": items})
            return

        if len(parts) == 3 and parts[0] == "api" and parts[1] == "items":
            item_id = self._parse_id(parts[2])
            if item_id is None:
                return
            item = STORE.get(item_id)
            if item is None:
                self._send_json(404, {"error": "指定されたアイテムが見つかりません", "id": item_id})
                return
            self._send_json(200, item)
            return

        self._not_found()

    def do_POST(self):
        parts = self._path_parts()

        if parts == ["echo"]:
            data, err = self._read_json_body()
            if err:
                self._send_json(400, {"error": err})
                return
            self._send_json(200, {
                "youSent": data,
                "receivedAt": datetime.now(timezone.utc).isoformat(),
            })
            return

        if parts == ["api", "items"]:
            data, err = self._read_json_body()
            if err:
                self._send_json(400, {"error": err})
                return
            if not isinstance(data, dict) or "name" not in data:
                self._send_json(400, {"error": "'name' フィールドは必須です"})
                return
            item = STORE.create(data)
            self._send_json(201, item)
            return

        self._not_found()

    def do_PUT(self):
        parts = self._path_parts()
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "items":
            item_id = self._parse_id(parts[2])
            if item_id is None:
                return
            data, err = self._read_json_body()
            if err:
                self._send_json(400, {"error": err})
                return
            if not isinstance(data, dict):
                self._send_json(400, {"error": "リクエストボディはオブジェクトである必要があります"})
                return
            item = STORE.update(item_id, data)
            if item is None:
                self._send_json(404, {"error": "指定されたアイテムが見つかりません", "id": item_id})
                return
            self._send_json(200, item)
            return

        self._not_found()

    def do_DELETE(self):
        parts = self._path_parts()
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "items":
            item_id = self._parse_id(parts[2])
            if item_id is None:
                return
            if STORE.delete(item_id):
                self._send_json(200, {"deleted": True, "id": item_id})
            else:
                self._send_json(404, {"error": "指定されたアイテムが見つかりません", "id": item_id})
            return

        self._not_found()

    # ---- ヘルパー -----------------------------------------------------------

    def _parse_id(self, raw):
        try:
            return int(raw)
        except ValueError:
            self._send_json(400, {"error": "id は整数である必要があります", "value": raw})
            return None

    def _not_found(self):
        self._send_json(404, {"error": "エンドポイントが見つかりません", "path": self.path})

    # ログ形式を見やすく上書き
    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


# ----------------------------------------------------------------------------
# 起動処理
# ----------------------------------------------------------------------------


def parse_args(argv):
    parser = argparse.ArgumentParser(description="テスト用 汎用サンプルAPIサーバー")
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="バインドするホスト (既定: 127.0.0.1 / 環境変数 HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="待ち受けるポート (既定: 8000 / 環境変数 PORT)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    server = ThreadingHTTPServer((args.host, args.port), ApiHandler)
    url = "http://%s:%d" % (args.host, args.port)
    print("=" * 60)
    print(" テスト用 汎用サンプルAPI を起動しました")
    print(" URL      : %s" % url)
    print(" ヘルス   : %s/health" % url)
    print(" 停止     : Ctrl + C")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n停止しています...")
    finally:
        server.server_close()
        print("サーバーを終了しました。")


if __name__ == "__main__":
    main()
