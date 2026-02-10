#!/usr/bin/env python3
"""SPARC Member Management – Flask web application."""

import os

from flask import Flask, jsonify, render_template, request
import psycopg2
import psycopg2.extras

app = Flask(__name__)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:***REDACTED***@turntable.proxy.rlwy.net:57735/railway",
)

EDITABLE_COLUMNS = {
    "firstname",
    "lastname",
    "phone",
    "email",
    "board_contact",
    "membership_level",
    "attendance_notes",
    "outreach_notes",
    "tickets_feb_2026",
    "tickets_apr",
    "active",
}


def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


# ── Pages ──────────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


# ── API ────────────────────────────────────────────────────────────────────────


@app.route("/api/members")
def api_members():
    search = request.args.get("search", "").strip()
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if search:
            like = f"%{search}%"
            cur.execute(
                """SELECT * FROM member
                   WHERE firstname ILIKE %s
                      OR lastname  ILIKE %s
                      OR email     ILIKE %s
                      OR phone     ILIKE %s
                      OR board_contact ILIKE %s
                   ORDER BY lastname, firstname""",
                (like, like, like, like, like),
            )
        else:
            cur.execute("SELECT * FROM member ORDER BY lastname, firstname")
        rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()


@app.route("/api/members/<int:member_id>")
def api_member(member_id):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM member WHERE id = %s", (member_id,))
        row = cur.fetchone()
        if row is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row)
    finally:
        conn.close()


@app.route("/api/members/<int:member_id>", methods=["PUT"])
def api_update_member(member_id):
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Only allow known columns
    fields = {k: v for k, v in data.items() if k in EDITABLE_COLUMNS}
    if not fields:
        return jsonify({"error": "No valid fields provided"}), 400

    # Type coercion
    for col in ("tickets_feb_2026", "tickets_apr"):
        if col in fields:
            val = fields[col]
            if val is None or val == "":
                fields[col] = None
            else:
                try:
                    fields[col] = int(val)
                except (ValueError, TypeError):
                    return jsonify({"error": f"Invalid integer for {col}"}), 400

    if "active" in fields:
        val = fields["active"]
        if isinstance(val, str):
            fields["active"] = val.lower() in ("true", "1", "yes")

    # Build parameterised UPDATE
    set_parts = [f"{col} = %s" for col in fields]
    values = list(fields.values()) + [member_id]

    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            f"UPDATE member SET {', '.join(set_parts)} WHERE id = %s RETURNING *",
            values,
        )
        row = cur.fetchone()
        conn.commit()
        if row is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row)
    except Exception as exc:
        conn.rollback()
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()


@app.route("/api/membership_levels")
def api_membership_levels():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT level FROM membership ORDER BY id")
        levels = [r[0] for r in cur.fetchall()]
        return jsonify(levels)
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
