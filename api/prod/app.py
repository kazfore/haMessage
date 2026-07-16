#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本番向けサンプルAPI (Flask アプリ)

テスト用 server.py と同じエンドポイントを Flask で実装したものです。
本番では開発用サーバーではなく WSGI サーバー (waitress など) 経由で動かします。

ローカル確認 (開発用サーバー):
    pip install -r requirements.txt
    python app.py

本番起動 (waitress / Windows でも動作):
    pip install -r requirements.txt
    waitress-serve --host=0.0.0.0 --port=8000 app:app

このサンプルはデータを SQLite に永続化します (テスト用の server.py は
メモリ保持でした)。DB ファイルのパスは環境変数 DB_PATH で変更できます。
"""

import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "data.sqlite3"))

app = Flask(__name__)


# ----------------------------------------------------------------------------
# DB (SQLite による永続化)
# ----------------------------------------------------------------------------


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            note       TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


# ----------------------------------------------------------------------------
# ルーティング (テスト用 server.py と同じ構成)
# ----------------------------------------------------------------------------


@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.get("/")
def index():
    return jsonify({
        "name": "本番向けサンプルAPI (Flask)",
        "version": "1.0",
        "endpoints": [
            "GET    /health",
            "POST   /echo",
            "GET    /api/items",
            "POST   /api/items",
            "GET    /api/items/<id>",
            "PUT    /api/items/<id>",
            "DELETE /api/items/<id>",
        ],
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok", "time": now_iso()})


@app.post("/echo")
def echo():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "リクエストボディが正しい JSON ではありません"}), 400
    return jsonify({"youSent": data, "receivedAt": now_iso()})


@app.get("/api/items")
def list_items():
    rows = get_db().execute("SELECT * FROM items ORDER BY id").fetchall()
    items = [row_to_dict(r) for r in rows]
    return jsonify({"count": len(items), "items": items})


@app.post("/api/items")
def create_item():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "name" not in data:
        return jsonify({"error": "'name' フィールドは必須です"}), 400
    ts = now_iso()
    db = get_db()
    cur = db.execute(
        "INSERT INTO items (name, note, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (data["name"], data.get("note"), ts, ts),
    )
    db.commit()
    row = db.execute("SELECT * FROM items WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(row_to_dict(row)), 201


@app.get("/api/items/<int:item_id>")
def get_item(item_id):
    row = get_db().execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return jsonify({"error": "指定されたアイテムが見つかりません", "id": item_id}), 404
    return jsonify(row_to_dict(row))


@app.put("/api/items/<int:item_id>")
def update_item(item_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "リクエストボディはオブジェクトである必要があります"}), 400
    db = get_db()
    row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return jsonify({"error": "指定されたアイテムが見つかりません", "id": item_id}), 404
    name = data.get("name", row["name"])
    note = data.get("note", row["note"])
    db.execute(
        "UPDATE items SET name = ?, note = ?, updated_at = ? WHERE id = ?",
        (name, note, now_iso(), item_id),
    )
    db.commit()
    row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    return jsonify(row_to_dict(row))


@app.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    db = get_db()
    cur = db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "指定されたアイテムが見つかりません", "id": item_id}), 404
    return jsonify({"deleted": True, "id": item_id})


# アプリ読み込み時に DB を初期化 (waitress 経由でも実行される)
init_db()


if __name__ == "__main__":
    # 開発用サーバー。本番では waitress-serve を使ってください。
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")))
