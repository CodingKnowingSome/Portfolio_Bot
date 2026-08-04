"""
API endpoints and database setup.
"""
from flask import Flask, request, jsonify
import sqlite3
from Functions.get_roblox_id import get_roblox_id
from datetime import datetime
import logging
import requests

app = Flask(__name__)
db_path = "data/kos_blacklist.db"
logger = logging.getLogger(__name__)


def init_db():
    """
    Creates the databases if they don't exist.
    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS kos (
            user_id INTEGER PRIMARY KEY NOT NULL,
            kos BOOLEAN NOT NULL
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            user_id INTEGER PRIMARY KEY NOT NULL,
            reason STRING NOT NULL,
            added_by NOT NULL,
            last_edit INTEGER NOT NULL
        )
        """)
        conn.commit()


@app.route('/api/kos', methods=['POST'])
def set_kos():
    """
    API endpoint for setting a user's KoS status.
    Returns: Success or failure packet.

    """
    data = request.json or {}
    username = data.get('username')
    status = data.get('status')
    if not username or status is None:
        return jsonify({"success": False, "error": "Missing input"}), 400
    user_id, exact_username = get_roblox_id(username)
    if not user_id:
        return jsonify({"success": False, "error": "User not found"}), 404
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO kos (user_id, kos) VALUES (?, ?)
            ON CONFLICT (user_id) DO UPDATE SET
                kos = excluded.kos
            """, (user_id, bool(status)))
        conn.commit()
    return jsonify({
        "success": True,
        "user_id": user_id,
        "username": exact_username,
        "status": status
    }), 200


@app.route('/api/koscheck/<string:username>', methods=['GET'])
def koscheck(username):
    """
    API endpoint for checking a user's KoS status.
    Args:
        username: The user to be checked.

    Returns: Packet with their KoS status.

    """
    user_id, exact_username = get_roblox_id(username)
    if not user_id:
        return jsonify({"success": False, "error": "User not found"}), 404
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT kos FROM kos WHERE user_id = ?
            """, (user_id,))
        row = c.fetchone()
    if row is None:
        return jsonify({
            "success": True,
            "user_id": user_id,
            "username": exact_username,
            "status": "never_kos",
        }), 200

    return jsonify({
        "success": True,
        "user_id": user_id,
        "username": exact_username,
        "status": "current_kos" if row[0] == True else "former_kos"
    }), 200


@app.route('/api/blacklist', methods=['POST'])
def set_blacklist():
    """
    Sets a user's blacklist.
    Returns: Success/failure packet.

    """
    data = request.json or {}
    username = data.get('username')
    action = data.get("action", "add")
    reason = data.get('reason', "No reason provided")
    added_by = data.get('added_by', "Unknown")
    last_edit = int(datetime.now().timestamp())
    user_id, exact_username = get_roblox_id(username)
    if not user_id:
        return jsonify({"success": False, "error": "User not found"}), 404
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        if action == "remove":
            c.execute("""
                DELETE FROM blacklist WHERE user_id = ?
                """, (user_id,))
            conn.commit()
        else:
            c.execute("""
                INSERT INTO blacklist (user_id, reason, added_by, last_edit) VALUES (?, ?, ?, ?)
                ON CONFLICT (user_id) DO UPDATE SET
                    reason = excluded.reason,
                    added_by = excluded.added_by,
                    last_edit = excluded.last_edit
                """, (user_id, reason, added_by, last_edit))
            conn.commit()
    return jsonify({
        "success": True,
        "user_id": user_id,
        "username": exact_username,
        "reason": reason,
        "added_by": added_by,
        "last_edit": last_edit
    }), 200


@app.route('/api/blacklistlist', methods=['GET'])
def get_blacklist():
    """
    Lists all active blacklisted users.
    Returns: A packet including all blacklists or a failure packet.

    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT user_id, reason, added_by, last_edit FROM blacklist
        """)
        rows = c.fetchall()
    if not rows: return jsonify({"success": True, "count": 0, "blacklist": []})
    user_ids = list({row[0] for row in rows})
    username_map = {}
    try:
        roblox_resp = requests.post(
            "https://users.roblox.com/v1/users",
            json={"userIds": user_ids[:100], "excludeBannedUsers": False},
            timeout=5
        )
        if roblox_resp.status_code == 200:
            user_data = roblox_resp.json().get("data", [])
            username_map = {user["id"]: user["name"] for user in user_data}
    except Exception as e:
        logger.warning(f"Failed to get user data: {e}")
    blacklist = [
        {
            "user_id": r[0],
            "reason": r[1],
            "added_by": r[2],
            "last_edit": r[3],
            "username": username_map.get(r[0], "Unknown user")
        }
        for r in rows
    ]
    return jsonify({
        "success": True,
        "count": len(blacklist),
        "blacklist": blacklist
    }), 200


@app.route('/api/blacklist/<string:username>', methods=['GET'])
def is_blacklist(username):
    """
    API endpoint for checking a user's blacklist.
    Args:
        username: The user to be checked.

    Returns: A packet containing their status, or a failure packet.

    """
    user_id, exact_username = get_roblox_id(username)
    if not user_id:
        return jsonify({"success": False, "error": "User not found"}), 404
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM blacklist WHERE user_id = ?
        """, (user_id,))
        row = c.fetchone()
        conn.commit()
    if row:
        blacklist = [
            {
                "user_id": row[0],
                "reason": row[1],
                "added_by": row[2],
                "last_edit": row[3],
                "username": exact_username
            }
        ]
    return jsonify({
        "success": True,
        "status": True if row else False,
        "blacklist": blacklist if row else None
    }), 200


def run_api():
    """
    Runs the APIs.
    """
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    run_api()
