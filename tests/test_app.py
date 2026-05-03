from pathlib import Path
import sys

from psycopg2 import OperationalError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


class DummyCursor:
    def execute(self, query):
        assert query == "SELECT 1"

    def fetchone(self):
        return (1,)

    def close(self):
        return None


class DummyConnection:
    def cursor(self):
        return DummyCursor()

    def close(self):
        return None


def test_root_endpoint():
    client = main.app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "API is running"


def test_health_endpoint_success(monkeypatch):
    monkeypatch.setattr(main, "get_db_connection", lambda: DummyConnection())
    client = main.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["database"] == "up"


def test_health_endpoint_failure(monkeypatch):
    def raise_operational_error():
        raise OperationalError("db down")

    monkeypatch.setattr(main, "get_db_connection", raise_operational_error)
    client = main.app.test_client()

    response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json()["database"] == "down"


def test_config_endpoint(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("APP_PORT", "8000")
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "app_staging")

    client = main.app.test_client()
    response = client.get("/config")

    assert response.status_code == 200
    assert response.get_json()["app_env"] == "staging"
    assert response.get_json()["db_name"] == "app_staging"
