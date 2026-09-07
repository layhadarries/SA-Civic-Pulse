"""
extract.py
Reads masterfilelist.txt, filters it down to:
  - only .export.CSV.zip files (not .gkg. or .mentions.)
  - only files within our date range (Sep 2025 - Aug 2026)
Then downloads each one into data/raw/, skipping files already downloaded.
 
"""

import os
import requests
import zipfile
import io

# ---> Constants <--- 
MASTERLIST_FILE = "masterfilelist.txt"
 
# Sept 2025 to Aug 2026
START_DATE = "20250901000000"   # 2025-09-01 00:00:00
END_DATE = "20260831235959"     # 2026-08-31 23:59:59

OUTPUT_DIR = "data/raw"


def get_matching_urls():
    """
    Read masterfilelist.txt and return only the event-file URLs in our date range.
    """
    print("[1] getting masterfilelist dataaaaaaaaaaaaa")

    urls = []

    # [!] check if masterfilelist.txt exists
    if MASTERLIST_FILE not in os.listdir():
        raise FileNotFoundError("masterfilelist.txt not found.")


    with open(MASTERLIST_FILE, 'r', encoding='utf-8') as f:
        # eg file: 49632 21e76b9a06d5df228ee05efafc4348a6 http://data.gdeltproject.org/gdeltv2/20260831070000.export.CSV.zip
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

            # [!] check the timestamp is within time period
            if timestamp < START_DATE or timestamp > END_DATE:
                continue  # skip files outside our date range

            # [!] check if timestamp is not a digit
            if not timestamp.isdigit():
                continue  # skip malformed timestamps

            if START_DATE <= timestamp <= END_DATE:
                urls.append(url)

    return urls


def download_file(url):
    """
    Create OUTPUT_DIR if it doesn't exist, then download the file from the given URL into that directory,
    skipping it if already downloaded.

    eg --> http://data.gdeltproject.org/gdeltv2/20260831070000.export.CSV.zip
    """

    zip_filename = url.rsplit("/", 1)[-1]           # get the zip from the URL - [ 20260831070000.export.CSV.zip ]
    csv_filename = zip_filename.replace(".zip", "")  # get the csv from the URL - [ 20260831070000.export.CSV ]
    output_path = os.path.join(OUTPUT_DIR, csv_filename) # full path to save the downloaded file


    # [!] check if OUTPUT_DIR exists, if not create it
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)  # create the output directory if it doesn't exist


    # -----------------------------------------------------------------------------
    # download the data from the urls and save it to the output directory
    try:
        print(f"\n-- Downloading url from zip: {url} --")
        response = requests.get(url)
        response.raise_for_status()  # raise an error if the request was unsuccessful
                
    except requests.exceptions.RequestException as e:
        print(f"Failed to download: {url} -> {e}")
        return  # skip this file if there's an error


    # -----------------------------------------------------------------------------
    # open zip file
    try:
        print(f"\n-- Open Zip: {response} --")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:

            inner_file = z.namelist()[0]
            csv_bytes = z.read(inner_file) # eturns bytes (not an actual file)

    except zipfile.BadZipFile as e:
        print(f"Failed to find zip: {zip_filename} -> {e}")
        return  # skip this file if there's an error

    # save byte data to the file path
    with open(output_path, "wb") as f: # "wb" stands for write binary
        f.write(csv_bytes)

    return

    
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True) # make directory
    urls = get_matching_urls()


    print(f"-[STATS]- Found {len(urls)} files matching date range and file type.\n")
 
    counts = {"downloaded": 0, "skipped": 0, "failed": 0}
 
    for i, url in enumerate(urls, start=1):
        result = download_file(url)
        counts["downloaded"] += 1
 
        if i % 100 == 0 or i == len(urls):
            print(f"-[STATS]- Progress: {i}/{len(urls)}  "
                  f"(-[STATS]- downloaded: {counts['downloaded']}, "
                  f"-[STATS]- skipped: {counts['skipped']}, "
                  f"-[STATS]- failed: {counts['failed']})")
 
    print(f"\nCounts : {counts}")

if __name__ == "__main__":
    main()
