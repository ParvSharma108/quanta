"""Unit and integration tests for FastAPI AI Engine endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "quanta-ai-engine"


def test_generate_strategy_endpoint():
    payload = {
        "problem": {
            "capital": 100.0,
            "step_size": 10.0,
            "assets": [
                {
                    "id": "gov_bond",
                    "name": "Gov Bonds",
                    "asset_type": "gov_bond",
                    "expected_return": 0.07,
                    "risk": 0.05,
                    "liquidity": 0.95
                },
                {
                    "id": "equity",
                    "name": "Equity",
                    "asset_type": "equity",
                    "expected_return": 0.14,
                    "risk": 0.40,
                    "liquidity": 0.80
                }
            ],
            "liabilities": [
                {
                    "id": "debt_1",
                    "name": "Loan",
                    "principal": 10.0,
                    "interest_rate": 0.08,
                    "priority": 1,
                    "is_mandatory_reserve": True
                }
            ],
            "constraints": [
                {
                    "id": "c_min_liq",
                    "constraint_type": "minimum_liquidity",
                    "parameters": {"threshold": 0.20}
                }
            ],
            "risk_tolerance": 0.50,
            "minimum_liquidity": 0.20
        },
        "algorithm": "astar"
    }
    response = client.post("/api/v1/strategy/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"]["is_compliant"]
    assert data["search_result"]["success"]
    assert "risk_breakdown" in data
    assert "constraint_audit" in data


def test_constraints_validate_endpoint():
    payload = {
        "state": {
            "total_capital": 100.0,
            "cash": 85.0,
            "allocations": {"gov_bond": 0.0},
            "reserved_for_debt": 15.0,
            "liquidity_ratio": 1.0,
            "risk_score": 0.01,
            "expected_return": 0.03
        },
        "problem": {
            "capital": 100.0,
            "step_size": 10.0,
            "assets": [],
            "liabilities": [],
            "constraints": [
                {
                    "id": "c_min_liq",
                    "constraint_type": "minimum_liquidity",
                    "parameters": {"threshold": 0.20}
                }
            ]
        }
    }
    response = client.post("/api/v1/constraints/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"]
    assert data["total_violations"] == 0
