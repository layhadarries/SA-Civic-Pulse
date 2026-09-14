"""
tests/test_main.py

Unit and route-level tests for the SA Civic Pulse FastAPI application.
All database executions are mocked via unittest.mock.patch on run_query.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

# Import app from your module path (e.g., api.main or main)
from api.main import app

client = TestClient(app)


# --------------------------------------------------------------------
# 1. Root & Documentation
# --------------------------------------------------------------------
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "SA Civic Pulse API" in response.json()["message"]


# --------------------------------------------------------------------
# 2. GET /events
# --------------------------------------------------------------------
@patch("api.main.run_query")
def test_get_events_default(mock_run_query):
    mock_run_query.return_value = [
        {
            "global_event_id": 1320689300,
            "sql_date": "2026-08-31",
            "province_name": "Western Cape",
            "category_label": "Protest",
            "actor1_name": "CITIZENS",
            "actor2_name": "POLICE",
            "avg_tone": -4.25,
            "goldstein_scale": -5.0,
            "source_url": "https://example.com/article",
        }
    ]

    response = client.get("/events")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["global_event_id"] == 1320689300

    # Ensure run_query was executed with default limit parameter 50
    mock_run_query.assert_called_once()
    sql_arg, params_arg = mock_run_query.call_args[0]
    assert 50 in params_arg


@patch("api.main.run_query")
def test_get_events_with_filters(mock_run_query):
    mock_run_query.return_value = []

    response = client.get(
        "/events?province=Gauteng&start_date=2026-01-01&end_date=2026-06-30&limit=10"
    )
    assert response.status_code == 200

    sql_arg, params_arg = mock_run_query.call_args[0]
    assert "loc.province_name = %s" in sql_arg
    assert "t.sql_date >= %s" in sql_arg
    assert "t.sql_date <= %s" in sql_arg
    assert "Gauteng" in params_arg
    assert 10 in params_arg


def test_get_events_limit_exceeded_validation():
    # Schema defines Query(50, le=500). limit=501 must trigger a 422 Unprocessable Entity
    response = client.get("/events?limit=501")
    assert response.status_code == 422


# --------------------------------------------------------------------
# 3. GET /provinces
# --------------------------------------------------------------------
@patch("api.main.run_query")
def test_get_provinces(mock_run_query):
    mock_run_query.return_value = [
        {"province_name": "Western Cape", "adm1_code": "SF11", "event_count": 450, "avg_tone": -2.15},
        {"province_name": "Gauteng", "adm1_code": "SF06", "event_count": 320, "avg_tone": -3.40},
    ]

    response = client.get("/provinces?min_count=100")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["province_name"] == "Western Cape"

    sql_arg, params_arg = mock_run_query.call_args[0]
    assert params_arg == (100,)


# --------------------------------------------------------------------
# 4. GET /event-types/top
# --------------------------------------------------------------------
@patch("api.main.run_query")
def test_get_top_event_types(mock_run_query):
    mock_run_query.return_value = [
        {"cameo_root_code": "14", "category_label": "Protest", "quad_class": 3, "event_count": 180},
        {"cameo_root_code": "02", "category_label": "Appeal", "quad_class": 1, "event_count": 95},
    ]

    response = client.get("/event-types/top?limit=2&province=Western%20Cape")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["cameo_root_code"] == "14"

    sql_arg, params_arg = mock_run_query.call_args[0]
    assert "Western Cape" in params_arg
    assert 2 in params_arg


# --------------------------------------------------------------------
# 5. GET /events/count
# --------------------------------------------------------------------
@patch("api.main.run_query")
def test_get_events_count(mock_run_query):
    mock_run_query.return_value = {"total_events": 1284}

    response = client.get("/events/count?province=KwaZulu-Natal&cameo_root_code=14")
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] == 1284

    # Verify fetch_one=True was passed to run_query
    _, kwargs = mock_run_query.call_args
    assert kwargs.get("fetch_one") is True


# --------------------------------------------------------------------
# 6. GET /events/{event_id}
# --------------------------------------------------------------------
@patch("api.main.run_query")
def test_get_event_by_id_found(mock_run_query):
    mock_run_query.return_value = {
        "global_event_id": 1320689300,
        "sql_date": "2026-08-31",
        "year": 2026,
        "month": 8,
        "adm1_code": "SF11",
        "province_name": "Western Cape",
        "country_code": "SF",
        "cameo_root_code": "14",
        "cameo_base_code": "140",
        "quad_class": 3,
        "category_label": "Protest",
        "actor1_name": "PROTESTERS",
        "actor1_country": "SAF",
        "actor2_name": None,
        "actor2_country": None,
        "goldstein_scale": -6.5,
        "avg_tone": -5.2,
        "num_mentions": 10,
        "num_sources": 3,
        "num_articles": 12,
        "source_url": "https://example.com/sa-news",
        "date_added": "2026-08-31T07:00:00Z",
    }

    response = client.get("/events/1320689300")
    assert response.status_code == 200
    data = response.json()
    assert data["global_event_id"] == 1320689300
    assert data["province_name"] == "Western Cape"


@patch("api.main.run_query")
def test_get_event_by_id_not_found(mock_run_query):
    mock_run_query.return_value = None

    response = client.get("/events/9999999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event 9999999999 not found"


def test_get_event_by_id_invalid_type():
    # If the user passes a string instead of an int in the path, FastAPI returns 422
    response = client.get("/events/not-a-number")
    assert response.status_code == 422