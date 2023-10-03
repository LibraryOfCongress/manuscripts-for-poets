"""Script for adding resource metadata to transcript data using cached json data from API"""

# -*- coding: utf-8 -*-

import argparse
import os

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="TRANSCRIPT", default="data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="AssetStatus=completed", help="Filter query string; leave blank if no filter")
    parser.add_argument("-items", dest="ITEM_DATA_DIR", default="data/items/", help="Directory of JSON files downloaded from scripts/get_item_data.py")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv", help="Output csv file")
    parser.add_argument("-probe", dest="PROBE", action="store_true", help="Just output details; do not process data")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to add resource data to transcript data"""

    if not a.PROBE:
        # Make sure output dirs exist
        makeDirectories(a.OUTPUT_FILE)

    fieldnames, rows = readCsv(a.TRANSCRIPT)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        rows = filterByQueryString(rows, a.FILTER)

    # Load metadata into memory
    itemIds = unique([row["ItemId"] for row in rows])
    itemCount = len(itemIds)
    print(f"Found {itemCount} unique items.")
    itemData = {}
    for itemId in itemIds:
        filename = f"{a.ITEM_DATA_DIR}{itemId}.json"
        itemData[itemId] = {
            "assetCount": len([row for row in rows if row["ItemId"] == itemId]),
            "apiData": readJSON(filename)
        }
        if not os.path.isfile(filename):
            print(f"Could not locate file {filename}")
            itemData[itemId]["apiData"] = None
        else:
            itemData[itemId]["apiData"] = readJSON(filename)

    if a.PROBE:
        return
    
    # Retrieve resource data for each row
    for i, row in enumerate(rows):
        data = itemData[row["ItemId"]]

        # Retrieve asset index and count
        rows[i]["ItemAssetCount"] = data["assetCount"]
        rows[i]["ItemAssetIndex"] = int(row["Asset"].split("-")[-1]) if "-" in row["Asset"] else 1

        # Retrieve data from API response
        apiData = data["apiData"]
        if apiData is None:
            continue
        resourceUrl = apiData["item"]["resources"][0]["url"]
        rows[i]["ResourceID"] = str(resourceUrl.strip("/").split("/")[-1])
        rows[i]["ResourceURL"] = f"https://www.loc.gov/resource/{rows[i]['ResourceID']}/?sp={rows[i]['ItemAssetIndex']}&st=text"
        rows[i]["Date"] = apiData["item"]["date"] if "date" in apiData["item"] else ""
        rows[i]["Undated"] = "yes" if "undated" in row["Item"].lower() else "no"
        dates = ""
        if "dates" in apiData["item"] and len(apiData["item"]["dates"]) > 0:
            for key in apiData["item"]["dates"][0]:
                dates = key
                break
        rows[i]["Dates"] = dates

    # Add fields to new data
    fieldsToAdd = ["ItemAssetCount", "ItemAssetIndex", "ResourceID", "ResourceURL", "Date", "Dates", "Undated"]
    for field in fieldsToAdd:
        if field not in fieldnames:
            fieldnames.append(field)

    # Write data to file
    writeCsv(a.OUTPUT_FILE, rows, fieldnames)

main(parseArgs())
