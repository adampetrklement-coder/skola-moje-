from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import jwt
import datetime
import sqlite3
from db import get_db_connection, init_db
from config import SECRET_KEY, CORS_ORIGINS

app = Flask(__name__)
# CORS: explicitně povolíme metody a hlavičky používané webem
CORS(
    app,
    resources={r"/*": {"origins": CORS_ORIGINS}},
    supports_credentials=False,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.config['SECRET_KEY'] = SECRET_KEY

# Inicializace databáze při startu
with app.app_context():
    try:
        init_db()
    except Exception as err:
        print(f"Chyba při inicializaci databáze: {err}")

# 🔎 Základní healthcheck
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

# 🧩 Registrace
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password:
        return jsonify({"error": "Chybí uživatelské jméno nebo heslo"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if cur.fetchone() is not None:
        return jsonify({"error": "Uživatel už existuje"}), 400

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cur.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", (username, hashed_pw, email))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Účet úspěšně vytvořen!"}), 201


# 🔑 Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "Neplatné jméno nebo heslo"}), 401

    user = {"id": row[0], "username": row[1], "password_hash": row[2]}
    # password_hash je uložen jako BLOB (bytes)
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return jsonify({"error": "Neplatné jméno nebo heslo"}), 401

    token = jwt.encode({
        "user_id": user["id"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"token": token})


# 🏋️‍♂️ Přidání tréninku
@app.route('/add_workout', methods=['POST'])
def add_workout():
    data = request.get_json()
    token = data.get("token")

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded["user_id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token vypršel"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Neplatný token"}), 401

    exercise = data.get("exercise")
    sets = data.get("sets")
    reps = data.get("reps")
    weight = data.get("weight")
    note = data.get("note", "")

    # Základní validace číselných polí
    try:
        sets = int(sets)
        reps = int(reps)
        weight = float(weight)
    except (TypeError, ValueError):
        return jsonify({"error": "Neplatné hodnoty pro sets/reps/weight"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO workouts (user_id, exercise, sets, reps, weight, note) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, exercise, sets, reps, weight, note)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Trénink uložen"}), 201


# 📋 Získání tréninků uživatele
@app.route('/get_workouts', methods=['GET'])
def get_workouts():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token chybí"}), 401

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded["user_id"]
    except jwt.InvalidTokenError:
        return jsonify({"error": "Neplatný token"}), 401

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, exercise, sets, reps, weight, note, date FROM workouts WHERE user_id=? ORDER BY date DESC", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # sqlite3.Row by šel převést na dict, ale používáme obyčejný cursor -> mapujeme ručně
    workouts = [
        {
            "id": r[0],
            "user_id": r[1],
            "exercise": r[2],
            "sets": r[3],
            "reps": r[4],
            "weight": r[5],
            "note": r[6],
            "date": r[7],
        }
        for r in rows
    ]

    return jsonify({"workouts": workouts})


if __name__ == '__main__':
    # Spuštění na portu 5001, aby nekolidoval s lokálním web serverem na 5000
    app.run(debug=True, port=5001)
