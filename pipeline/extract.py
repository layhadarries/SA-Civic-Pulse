"""
extract.py — Raw Ingestion Layer for SA Civic Pulse

Parses the GDELT 2.0 master file list, identifies export events matching
the configured timestamp range, and extracts decompressed CSVs into data/raw/.

Input:  masterfilelist.txt
Output: data/raw/<timestamp>.export.CSV
Core Responsibilities:
1. Scan masterfilelist.txt for valid GDELT 2.0 event URLs (.export.CSV.zip).
2. Filter entries within START_DATE and END_DATE boundary.
3. Stream, decompress in memory, and persist raw event CSVs to OUTPUT_DIR.
4. Provide idempotent execution by skipping files already present on disk.
"""

import os
import requests
import zipfile
import io

from datetime import datetime


MASTERLIST_FILE = "masterfilelist.txt"
 
# Sept 2025 to Aug 2026
START_DATE = "20250901000000"   # 2025-09-01 00:00:00
END_DATE = "20260831235959"     # 2026-08-31 23:59:59


OUTPUT_DIR = "data/raw"

def get_matching_urls():
    """
    Read masterfilelist.txt and return only the event-file URLs in our date range.
    """

    urls = []

    # [!] check if masterfilelist.txt exists
    if MASTERLIST_FILE not in os.listdir():
        raise FileNotFoundError("-- [!] masterfilelist.txt not found.")


    with open(MASTERLIST_FILE, 'r', encoding='utf-8') as f:
        # eg file: 49632 21e.. http://data.gdeltproject.org/gdeltv2/20260831070000.export.CSV.zip
        for line in f:
            parts = line.strip().split(" ")

            # [!] check if correct amount of parts
            if len(parts) != 3:
                continue  # skip malformed lines

            _, _, url = parts

            # [!] check if url ends with .export.CSV.zip
            if not url.endswith(".export.CSV.zip"):
                continue  # skip non-event files

            timestamp = url.split("/")[-1].split(".")[0]  # extract timestamp from URL

            # [!] check if timestamp is not a digit
            if not timestamp.isdigit():
                continue  # skip malformed timestamps

            # [!] check the timestamp is within time period
            if timestamp < START_DATE or timestamp > END_DATE:
                continue  # skip files outside our date range

            urls.append(url)

    return urls


def download_file(url):
    """
    Download and extract the CSV from the given URL into OUTPUT_DIR.
    Skips if the destination file already exists.
    Returns: "downloaded", "skipped", or "failed"
    """
    # eg url = http://data.gdeltproject.org/gdeltv2/20260831070000.export.CSV.zip

    # get the zip from the URL - [ 20260831070000.export.CSV.zip ]
    zip_filename = url.rsplit("/", 1)[-1]

    # get the csv from the URL - [ 20260831070000.export.CSV ]
    csv_filename = zip_filename.replace(".zip", "")

    # full path to save the downloaded file
    output_path = os.path.join(OUTPUT_DIR, csv_filename)

    csv_filename = zip_filename.replace(".zip", "")
    # output_path is: "data/raw/20250901000000.export.CSV"
    csv_path = os.path.join(OUTPUT_DIR, csv_filename)

    # [!] check if CSV path exists when iterating through. If so, skip
    if os.path.exists(csv_path):
        return "skipped"

    # -----------------------------------------------------------------------------
    # download the data from the urls and save it to the output directory
    # [!] check request failed 
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # raise an error if the request was unsuccessful
                
    except requests.exceptions.RequestException as e:
        print(f"-- [!] Failed to download: {url} -> {e}")
        return "failed"

    # -----------------------------------------------------------------------------
    # [!] check if zip failed to be found
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            inner_file = z.namelist()[0]
            csv_bytes = z.read(inner_file) # eturns bytes (not an actual file)

    except zipfile.BadZipFile as e:
        print(f"-- [!] Failed to find zip: {zip_filename} -> {e}")
        return  # skip this file if there's an error

    # [!] check if zip failed to extract
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            inner_file = z.namelist()[0]
            csv_bytes = z.read(inner_file)
    except (zipfile.BadZipFile, IndexError) as e:
        print(f"-- [!] Failed to extract zip from {url} -> {e}")
        return "failed"

    # -----------------------------------------------------------------------------
 
    # save byte data to the file path
    # write CSV to disk
    try:
        with open(output_path, "wb") as f: # "wb" stands for write binary
            f.write(csv_bytes)
    except OSError as e:
        print(f"-- [!] Failed to write file: {output_path} -> {e}")
        return "failed"

    return "downloaded"

    
def main():

    now = datetime.now()
    readable_string = now.strftime("%A, %B %d, %Y at %I:%M %p")

    print(f"""
======================================
 SA Civic Pulse — Pipeline Run
 Started: {readable_string}
======================================

[1/3] EXTRACT — downloading GDELT files
""")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True) # make directory
    urls = get_matching_urls()

    print(f" Found {len(urls)} files matching date range and file type.")
 
    counts = {"downloaded": 0, "skipped": 0, "failed": 0}
 
    for i, url in enumerate(urls, start=1):
        result = download_file(url)
        counts[result] += 1

    print(f" Progress: {len(urls)}/{len(urls)}")
    print(f" ✓ {counts['downloaded']} downloaded, {counts['skipped']} skipped, {counts['failed']} failed\n") # add time taken eg  (2m 41s)

if __name__ == "__main__":
    main()
