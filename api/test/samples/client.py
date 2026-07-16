#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サンプルAPIクライアント (Python 標準ライブラリのみ / 依存なし)

server.py を起動した状態で実行すると、一連のエンドポイントを順番に呼び出して
結果を表示します。API 動作確認のサンプルです。

    python client.py
    python client.py --base-url http://127.0.0.1:9000
"""

import argparse
import json
import os
import urllib.error
import urllib.request


def call(method, url, body=None):
    """API を呼び出して (ステータス, JSON) を返す。"""
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            payload = {"error": "HTTP %s" % exc.code}
    except urllib.error.URLError as exc:
        raise SystemExit(
            "サーバーに接続できませんでした: %s\n"
            "先に server.py を起動してください。" % exc.reason
        )
    return status, payload


def show(title, method, url, status, payload):
    print("\n=== %s ===" % title)
    print("%s %s -> %s" % (method, url, status))
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="サンプルAPIクライアント")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BASE_URL", "http://127.0.0.1:8000"),
        help="API のベースURL (既定: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    # 1) ヘルスチェック
    status, payload = call("GET", base + "/health")
    show("ヘルスチェック", "GET", base + "/health", status, payload)

    # 2) echo
    status, payload = call("POST", base + "/echo", {"hello": "world", "n": 42})
    show("echo", "POST", base + "/echo", status, payload)

    # 3) 一覧
    status, payload = call("GET", base + "/api/items")
    show("アイテム一覧", "GET", base + "/api/items", status, payload)

    # 4) 作成
    status, created = call("POST", base + "/api/items", {"name": "クライアントから作成", "note": "テスト"})
    show("アイテム作成", "POST", base + "/api/items", status, created)
    new_id = created.get("id")

    # 5) 取得
    if new_id is not None:
        url = base + "/api/items/%d" % new_id
        status, payload = call("GET", url)
        show("アイテム取得", "GET", url, status, payload)

        # 6) 更新
        status, payload = call("PUT", url, {"note": "更新しました"})
        show("アイテム更新", "PUT", url, status, payload)

        # 7) 削除
        status, payload = call("DELETE", url)
        show("アイテム削除", "DELETE", url, status, payload)

    print("\n完了しました。")


if __name__ == "__main__":
    main()
