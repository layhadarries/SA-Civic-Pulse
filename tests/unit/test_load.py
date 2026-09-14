import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from pipeline import load


@pytest.fixture
def mock_pd_connect():
    pd_connect = MagicMock()
    cursor = MagicMock()
    pd_connect.cursor.return_value.__enter__.return_value = cursor
    return pd_connect, cursor


@pytest.fixture
def example_df():
    data = [
        {
            "global_event_id": 1001,
            "sql_date": "2026-08-31",
            "year": 2026,
            "month": 8,
            "adm1_code": "SF11",
            "action_geo_full_name": "Cape Town",
            "event_root_code": "14",
            "event_base_code": "140",
            "quad_class": 3,
            "category_label": "Protest",
            "actor1_name": "Protesters",
            "actor1_country": "SF",
            "actor2_name": None,
            "actor2_country": None,
            "goldstein_scale": -5.0,
            "avg_tone": -2.5,
            "num_mentions": 10,
            "num_sources": 2,
            "num_articles": 10,
            "source_url": "https://example.com/za-protest",
            "date_added": "2026-08-31 08:30:00",
        },
        {
            "global_event_id": 1002,
            "sql_date": "2026-08-31",  # duplicate date to verify deduplication
            "year": 2026,
            "month": 8,
            "adm1_code": None,        # null adm1 to test fallback to 'SF'
            "action_geo_full_name": "South Africa",
            "event_root_code": "01",
            "event_base_code": "010",
            "quad_class": 1,
            "category_label": "Make Public Statement",
            "actor1_name": "Spokesperson",
            "actor1_country": "SF",
            "actor2_name": "Public",
            "actor2_country": "SF",
            "goldstein_scale": 3.0,
            "avg_tone": 1.5,
            "num_mentions": 5,
            "num_sources": 1,
            "num_articles": 5,
            "source_url": "https://example.com/za-statement",
            "date_added": "2026-08-31 09:00:00",
        }
    ]
    return pd.DataFrame(data)

# functions:
# > load_event_time
#    - calculates date_key integer from sql_date
#    - deduplicates repeated dates
@patch("pipeline.load.execute_values")
def test_load_event_time_deduplicates_and_creates_date_key(
    mock_execute_values, 
    mock_pd_connect, 
    example_df):

    pd_connect, cursor = mock_pd_connect

    load.load_event_time(pd_connect, example_df)

    assert mock_execute_values.call_count == 1
    _, _, values = mock_execute_values.call_args[0]

    # both sample rows have date "2026-08-31"
    # so only 1 deduplicated record should be inserted
    assert len(values) == 1
    date_key, sql_date, year, month = values[0]

    assert date_key == 20260831
    assert year == 2026
    assert month == 8
    pd_connect.commit.assert_called_once()

# > load_event_location
#    - extracts unique adm1_code values
#    - enriches with provincial names from PROVINCES
#    - always injects fallback 'SF'
@patch("pipeline.load.execute_values")
def test_load_event_location_maps_provinces_and_includes_fallback(
    mock_execute_values, 
    mock_pd_connect, 
    example_df):

    pd_connect, cursor = mock_pd_connect

    load.load_event_location(pd_connect, example_df)

    assert mock_execute_values.call_count == 1
    _, _, values = mock_execute_values.call_args[0]

    # must contain SF11 and the fallback SF
    adm1_codes = {v[0] for v in values}
    assert "SF11" in adm1_codes
    assert "SF" in adm1_codes

    # verify Western Cape mapping from PROVINCES dict
    sf11_row = next(v for v in values if v[0] == "SF11")
    assert sf11_row == ("SF11", "Western Cape", "SF")

# > load_event_action_type
#    - extracts distinct (cameo_root_code, cameo_base_code, quad_class, category_label)
@patch("pipeline.load.execute_values")
def test_load_event_action_type_distinct_cameo(
    mock_execute_values, 
    mock_pd_connect, 
    example_df):

    pd_connect, cursor = mock_pd_connect

    load.load_event_aciton_type(pd_connect, example_df)

    assert mock_execute_values.call_count == 1
    _, _, values = mock_execute_values.call_args[0]

    assert len(values) == 2
    expected_tuples = {
        ("14", "140", 3, "Protest"),
        ("01", "010", 1, "Make Public Statement"),
    }
    assert set(values) == expected_tuples

# > fetch_location_ids/fetch_event_type_ids
#    - maps query result sets into reverse lookup dictionaries: 
#               adm1_code -> id and (root, base, quad) -> id
def test_fetch_location_ids(mock_pd_connect):
    pd_connect, cursor = mock_pd_connect
    # db returns (location_id, adm1_code)
    cursor.fetchall.return_value = [(1, "SF"), (2, "SF11")]

    result = load.fetch_location_ids(pd_connect)

    assert result == {"SF": 1, "SF11": 2}


def test_fetch_event_type_ids(mock_pd_connect):
    pd_connect, cursor = mock_pd_connect
    # db returns (event_type_id, root, base, quad)
    cursor.fetchall.return_value = [(10, "14", "140", 3)]

    result = load.fetch_event_type_ids(pd_connect)

    assert result == {("14", "140", 3): 10}

# > load_event_Fact
#    - maps adm1_code to location_id (fallback 'SF' when null)
#    - maps CAMEO triplet to surrogate event_type_id
#    - converts NaN to None (SQL NULL)
@patch("pipeline.load.execute_values")
def test_load_event_fact(
    mock_execute_values, 
    mock_pd_connect, 
    example_df):

    pd_connect, cursor = mock_pd_connect

    location_id_map = {"SF11": 50, "SF": 1}
    event_type_id_map = {
        ("14", "140", 3): 101,
        ("01", "010", 1): 102
    }

    load.load_event_fact(pd_connect, example_df, location_id_map, event_type_id_map)

    assert mock_execute_values.call_count == 1
    _, sql_query, values = mock_execute_values.call_args[0]

    assert "INSERT INTO event_fact" in sql_query
    assert len(values) == 2

    # Row 1: adm1_code SF11 -> location_id 50, CAMEO -> 101
    row_1 = values[0]
    assert row_1[0] == 1001         # global_event_id
    assert row_1[1] == 20260831     # date_key
    assert row_1[2] == 50           # location_id
    assert row_1[3] == 101          # event_type_id
    assert row_1[6] is None         # actor2_name (None preserves SQL NULL)

    # Row 2: adm1_code is None -> fallback to "SF" -> location_id 1
    row_2 = values[1]
    assert row_2[0] == 1002
    assert row_2[2] == 1            # fallback location_id
    assert row_2[3] == 102          # event_type_id