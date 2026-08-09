"""Tests for sidecar collector routes."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.mark.unit
def test_collector_status_endpoint(client):
    response = client.get("/api/v1/collector")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert "runtime" in data


@pytest.mark.unit
def test_sidecar_report_conflict_when_not_in_sidecar_mode(client):
    payload = {
        "sidecar_version": "1.0.0",
        "schema_version": "1",
        "host_id": "host-a",
        "state": {"salad_version": "2.0.0"},
    }
    with patch("src.api.routes_v1.COLLECTOR_MODE", "local_psutil"):
        response = client.post("/api/v1/sidecar/report", json=payload, headers={"X-Sidecar-Token": "token"})
    assert response.status_code == 409


@pytest.mark.unit
def test_sidecar_report_requires_token_configuration(client):
    payload = {
        "sidecar_version": "1.0.0",
        "schema_version": "1",
        "host_id": "host-a",
        "state": {"salad_version": "2.0.0"},
    }
    with patch("src.api.routes_v1.COLLECTOR_MODE", "sidecar_push"), patch("src.api.routes_v1.SIDECAR_AUTH_TOKEN", None):
        response = client.post("/api/v1/sidecar/report", json=payload)
    assert response.status_code == 503


@pytest.mark.unit
def test_sidecar_report_accepts_valid_payload(client):
    payload = {
        "sidecar_version": "1.2.3",
        "schema_version": "1",
        "host_id": "host-a",
        "state": {"salad_version": "2.0.0", "salad_bowl_version": "3.0.0"},
    }
    with patch("src.api.routes_v1.COLLECTOR_MODE", "sidecar_push"), patch("src.api.routes_v1.SIDECAR_AUTH_TOKEN", "token"):
        response = client.post("/api/v1/sidecar/report", json=payload, headers={"X-Sidecar-Token": "token"})
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is True
