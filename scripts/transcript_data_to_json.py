"""Script for downloading item metadata from transcript data"""

# -*- coding: utf-8 -*-

import argparse

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-transcript", dest="TRANSCRIPT_INPUT_FILE", default="data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="Project=Letters between friends, allies, and others AND AssetStatus=completed", help="Filter query string; leave blank if no filter")
    parser.add_argument("-fields", dest="FIELDS", default="ItemId,Item,DownloadUrl,Transcription", help="Comma-separated list of fields to output")
    parser.add_argument("-group", dest="GROUP_FIELDS", default="ItemId,Item", help="Comma-separated list of fields that we should try to group together in the output b/c they have non-unique values")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="public/data/mary-church-terrell-correspondence/transcripts.json", help="Output JSON file")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to output transcript data as JSON"""

    # Make sure output dirs exist
    makeDirectories(a.OUTPUT_FILE)

    # Read data from .csv file
    fieldnames, pages = readCsv(a.TRANSCRIPT_INPUT_FILE)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        pages = filterByQueryString(pages, a.FILTER)

    # Parse columns and groups
    cols = [field.strip() for field in a.FIELDS.split(",")]
    cols = [field for field in cols if field in fieldnames]
    colGroups = [field.strip() for field in a.GROUP_FIELDS.split(",")]
    colGroups = [field for field in colGroups if field in fieldnames]
    groups = {}
    for field in colGroups:
        groups[field] = []

    # Retrieve data from each page
    rows = []
    for page in pages:
        row = []
        for col in cols:
            value = page[col]
            # check if we should group this value to reduce redudancy and save file size
            if col in colGroups:
                groupValues = groups[col]
                if value not in groupValues:
                    groupValues.append(value)
                value = groupValues.index(value)
            row.append(value)
        rows.append(row)

    # Write JSON to file
    jsonOut = {
        "cols": cols,
        "rows": rows,
        "groups": groups
    }
    writeJSON(a.OUTPUT_FILE, jsonOut)

main(parseArgs())
