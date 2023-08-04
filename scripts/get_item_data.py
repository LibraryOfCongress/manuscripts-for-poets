"""Script for downloading item metadata from transcript data"""

# -*- coding: utf-8 -*-

import argparse
import os
import time

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-transcript", dest="TRANSCRIPT", default="data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-out", dest="ITEM_DATA_DIR", default="data/2021387726/items/", help="Output directory to store data files")
    parser.add_argument("-overwrite", dest="OVERWRITE", action="store_true", help="Overwrite existing data?")
    parser.add_argument("-probe", dest="PROBE", action="store_true", help="Just output details; do not process data")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to download item data from transcript data"""

    if not a.PROBE:
        # Make sure output dirs exist
        makeDirectories(a.ITEM_DATA_DIR)

        if a.OVERWRITE:
            emptyDirectory(a.ITEM_DATA_DIR)

    fieldnames, rows = readCsv(a.TRANSCRIPT)
    itemIds = unique([row["ItemId"] for row in rows])
    print(f"Found {len(itemIds)} unique items.")
    if a.PROBE:
        return

    # Download transcript resources from each url
    for itemId in itemIds:
        url = f"https://www.loc.gov/item/{itemId}/?fo=json"
        filename = f"{a.ITEM_DATA_DIR}{itemId}.json"
        download(url, filename, overwrite=False)
        time.sleep(2) # sleep to avoid rate limiting

main(parseArgs())
