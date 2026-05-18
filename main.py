import os
from flask import Flask, jsonify
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "app_db"),
        user=os.getenv("DB_USER", "app_user"),
        password=os.getenv("DB_PASSWORD", "app_password"),
    )


@app.get("/")
def root():
    return jsonify({"message": "API is running", "environment": os.getenv("APP_ENV", "dev")})


@app.get("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "database": "up", "environment": os.getenv("APP_ENV", "dev")}), 200
    except OperationalError:
        return jsonify({"status": "error", "database": "down", "environment": os.getenv("APP_ENV", "dev")}), 503


@app.get("/live")
def live():
    return jsonify({"status": "alive", "environment": os.getenv("APP_ENV", "dev")}), 200


@app.get("/config")
def config():
    return jsonify(
        {
            "app_env": os.getenv("APP_ENV", "dev"),
            "app_port": int(os.getenv("APP_PORT", "8000")),
            "db_host": os.getenv("DB_HOST", "localhost"),
            "db_port": int(os.getenv("DB_PORT", "5432")),
            "db_name": os.getenv("DB_NAME", "app_db"),
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("APP_PORT", "8000")))

