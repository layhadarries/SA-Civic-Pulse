'''
Test file for accessing GDELT masterfilelist.
    >> tail -1 masterfilelist.txt    <- get the last 1 line of the masterfilelist
    >> 1) get http from list, 
    >> 2) extract zip file, 
    >> 3) get csv file 
    >> 

'''

import requests
import zipfile # open zip file
import io
import pandas as pd

# [1] Get zip file line from masterfilelist.txt
def open_masterfilelist_file():
    with open('masterfilelist.txt', 'r', encoding='utf-8') as f:
        last_line = None
        for line in f:
            clean_line =  line.strip() 
            if clean_line.endswith('.export.CSV.zip'):
                last_line = clean_line

    return last_line

        # first_line = f.readline()
        # for _ in range(5):  # get the first 5 lines of the file
            # f.readline()
            # we might need to store (idk how many) in another txt file so that we can get the zip files
        # return first_line
        

# FILE_URL = open_masterfilelist_file()

# [2] columns from list(df.columns) in main()
COLUMN_NAMES = [
    "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode",
    "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code",
    "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
    "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code",
    "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass",
    "GoldsteinScale", "NumMentions", "NumSources", "NumArticles", "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat", "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat", "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL",
]

# ---------------------------------------------------------------

def main(FILE_URL):
    print(f"[3] Downloading url from zip: {FILE_URL}")
    response = requests.get(FILE_URL)
    response.raise_for_status()  # raise an error if the request was unsuccessful

    print()
    print("----------------------------------")
    print()

    print("[4] extract zip file")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:

        csv_file = z.namelist()[0]
        print(f"[5] Extracting CSV file: {csv_file}")
        with z.open(csv_file) as f:
            df = pd.read_csv(f, sep="\t", header=None, names=COLUMN_NAMES, low_memory=False)

    print()
    print("----------------------------------")
    print()

    print(f"Total rows in this file: {len(df)}") # Total rows in this file: 2271 lol
    print("\nFirst 5 rows:")
    print(df.head())

    print()
    print("----------------------------------")
    print()

    print("Column names, so you can see they're properly labelled now:")
    print(list(df.columns))

    print()
    print("----------------------------------")
    print()

    # Filter to South Africa (FIPS code 'SF', not ISO 'ZA')
    sa_rows = df[df["ActionGeo_CountryCode"] == "SF"]
    print(f"Rows about South Africa in this file: {len(sa_rows)}")

    if len(sa_rows) > 0:
        print("\nA sample of the South African rows:")
        print(sa_rows[["SQLDATE", "ActionGeo_FullName", "EventRootCode", "AvgTone"]].head())
    else:
        print("No South African rows in this particular file -- that's normal for "
              "a single 15-minute snapshot. Try a different file if you want to see one.")


    print()
    print("----------------------------------")
    print()



if __name__ == "__main__":
    target = open_masterfilelist_file()
    if target:
        FILE_URL = target.split()[2]
        main(FILE_URL)
    else:
        print("geh")