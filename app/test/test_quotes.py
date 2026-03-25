# Tests unitaires pour l'API quotes
# On utilise pytest + le test client Flask pour tester sans lancer le serveur

import sys
import os
import pytest

# On ajoute src/ au path pour que les imports marchent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app
from quotes import clear_quotes, _seed_defaults


@pytest.fixture
def client():
    """Cree un client de test Flask et reinitialise le store entre chaque test."""
    app.config["TESTING"] = True
    clear_quotes()
    _seed_defaults()
    with app.test_client() as client:
        yield client


def test_index_returns_service_info(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "quotes-api"
    assert "endpoints" in data


def test_health_returns_healthy(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert "quotes_count" in data


def test_metrics_returns_prometheus_format(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "http_requests_total" in body
    assert "app_quotes_total" in body


def test_list_quotes_returns_seeded_data(client):
    resp = client.get("/quotes")
    assert resp.status_code == 200
    quotes = resp.get_json()
    assert len(quotes) == 3  # 3 citations seedees par defaut


def test_create_quote_success(client):
    resp = client.post("/quotes", json={
        "author": "Alan Turing",
        "text": "We can only see a short distance ahead, but we can see plenty there that needs to be done.",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["author"] == "Alan Turing"
    assert "id" in data
    assert "created_at" in data


def test_create_quote_missing_fields(client):
    resp = client.post("/quotes", json={"author": "Nobody"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_single_quote(client):
    create_resp = client.post("/quotes", json={
        "author": "Ada Lovelace",
        "text": "That brain of mine is something more than merely mortal.",
    })
    quote_id = create_resp.get_json()["id"]

    resp = client.get(f"/quotes/{quote_id}")
    assert resp.status_code == 200
    assert resp.get_json()["author"] == "Ada Lovelace"


def test_get_quote_not_found(client):
    resp = client.get("/quotes/does-not-exist")
    assert resp.status_code == 404


def test_delete_quote(client):
    create_resp = client.post("/quotes", json={
        "author": "Test",
        "text": "To be deleted.",
    })
    quote_id = create_resp.get_json()["id"]

    resp = client.delete(f"/quotes/{quote_id}")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] is True

    # Verifier que la citation n'existe plus
    resp = client.get(f"/quotes/{quote_id}")
    assert resp.status_code == 404


def test_delete_quote_not_found(client):
    resp = client.delete("/quotes/does-not-exist")
    assert resp.status_code == 404
