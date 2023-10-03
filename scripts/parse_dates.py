"""Script for adding resource metadata to transcript data using cached json data from API"""

# -*- coding: utf-8 -*-

import argparse
from dateparser.search import search_dates

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="", help="Filter query string; leave blank if no filter")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv", help="Output csv file; leave blank to update input file")
    parser.add_argument("-probe", dest="PROBE", action="store_true", help="Just output details; do not process data")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to parse and add dates to transcript data"""

    OUTPUT_FILE = a.OUTPUT_FILE if len(a.OUTPUT_FILE) > 0 else a.INPUT_FILE
    if not a.PROBE:
        # Make sure output dirs exist
        makeDirectories(OUTPUT_FILE)

    fieldnames, rows = readCsv(a.INPUT_FILE)
    rowCount = len(rows)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        rows = filterByQueryString(rows, a.FILTER)
    
    # Retrieve resource data for each row
    for i, row in enumerate(rows):
        transcriptDates = []
        startDate, endDate = getDateRange(row["Dates"])
        transcript = row["Transcription"]
        parsedDates = None
        try:
            parsedDates = search_dates(transcript, settings={'REQUIRE_PARTS': ['year'], 'PREFER_DAY_OF_MONTH': 'first'})
        except Exception:
            print(f"Error with parsing row {i+1}; skipping")
        if parsedDates is not None:
            for parsedText, parsedDate in parsedDates:
                parsedDate = parsedDate.replace(tzinfo=None)
                if startDate is None or endDate is None or startDate <= parsedDate <= endDate:
                    transcriptDates.append(parsedText)
        rows[i]["TranscriptDates"] = " | ".join(transcriptDates)
        printProgress(i+1, rowCount, "Progress: ")

    if a.PROBE:
        return

    # Add fields to new data
    fieldsToAdd = ["TranscriptDates"]
    for field in fieldsToAdd:
        if field not in fieldnames:
            fieldnames.append(field)

    # Write data to file
    writeCsv(OUTPUT_FILE, rows, fieldnames)

main(parseArgs())
