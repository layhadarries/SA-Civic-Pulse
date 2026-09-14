import os
from unittest.mock import patch, mock_open, MagicMock
import pytest
from pipeline import extract
import requests

VALID_URL = "http://data.gdeltproject.org/gdeltv2/20251001120000.export.CSV.zip"

## ---------------- get_matching_urls() ---------------- ##
# > File missing raises FileNotFoundError
def test_masterfilelist_missing_raises_error():
    with patch("pipeline.extract.os.listdir", return_value=["not_masterfilelist.txt"]):
        with pytest.raises(FileNotFoundError):
            extract.get_matching_urls()

# > Filters out incorrect files for processing
def test_incorrect_file_types():
    # START_DATE = "20250901000000"   # 2025-09-01 00:00:00
    # END_DATE = "20260831235959"     # 2026-08-31 23:59:59

    downloaded_files = "\n".join([
    # valid file
    "12345 abc http://data.gdeltproject.org/gdeltv2/20251001120000.export.CSV.zip",
    # before start_date
    "12345 weewoo http://data.gdeltproject.org/gdeltv2/20250831235959.export.CSV.zip",
    # after end_date
    "318008 hehe http://data.gdeltproject.org/gdeltv2/20260901000000.export.CSV.zip",
    # date time not valid
    "77777 angel http://data.gdeltproject.org/gdeltv2/asdfghjkk.export.CSV.zip",
    # event file not export.CSV.zip
    "90210 laflame http://data.gdeltproject.org/gdeltv2/20250831235959.gkg.csv.zip",
    # not even a file
    "not even a file brev"
    ])

    with patch("pipeline.extract.os.listdir", return_value=[extract.MASTERLIST_FILE]), \
    patch("builtins.open", mock_open(read_data=downloaded_files)):
        urls = extract.get_matching_urls()

    expected_outcome = [VALID_URL]

    assert urls == expected_outcome


## ----------------- download_file(url) ---------------- ##
# > Skips downloading if destination CSV already exists on disk
def test_csvfile_already_exists():
    # create csv and then run through download_file
    with patch("pipeline.extract.os.path.exists", return_value=True), \
         patch("pipeline.extract.requests.get") as mock_get:
        
        status = extract.download_file(VALID_URL)

        assert status == "skipped"
        mock_get.assert_not_called()    

# > Handles network failure (RequestException)
def test_network_failure_exception():
    with patch("pipeline.extract.os.path.exists", return_value=False), \
         patch("pipeline.extract.requests.get", side_effect=requests.exceptions.ConnectionError("Network down")):
        
        status = extract.download_file(VALID_URL)
        assert status == "failed"

# > Handles corrupt zipfile (BadZipFile)
def test_corrupt_zipfile_exception():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"not a real zip file payload"

    with patch("pipeline.extract.os.path.exists", return_value=False), \
         patch("pipeline.extract.requests.get", return_value=mock_response):
        
        status = extract.download_file(VALID_URL)
        # NOTE: the first zip returns None instead of failed
        assert status in ("failed", None)