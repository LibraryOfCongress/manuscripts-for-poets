"""Script for creating a subset of an existing transcript data .csv file"""

# -*- coding: utf-8 -*-

import argparse
import os

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="TRANSCRIPT", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="", help="Filter query string; leave blank if no filter")
    parser.add_argument("-include", dest="INCLUDE_FIELDS", default="", help="Fields to include; leave blank if all")
    parser.add_argument("-exclude", dest="EXCLUDE_FIELDS", default="", help="Fields to exclude; leave blank if none")
    parser.add_argument("-sort", dest="SORT", default="", help="Sort query string; leave blank if no sort")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="", help="Output csv file")
    parser.add_argument("-probe", dest="PROBE", action="store_true", help="Just output details; do not process data")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to create subset of transcript data"""

    if not a.PROBE:
        # Make sure output dirs exist
        makeDirectories(a.OUTPUT_FILE)

    fieldnames, rows = readCsv(a.TRANSCRIPT)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        rows = filterByQueryString(rows, a.FILTER)

     # Sort data if necessary
    if len(a.SORT) > 0:
        rows = sortByQueryString(rows, a.SORT)

    includeFields = None
    if len(a.INCLUDE_FIELDS) > 0:
        includeFields = [field.strip() for field in a.INCLUDE_FIELDS.split(",")]

    excludeFields = None
    if len(a.EXCLUDE_FIELDS) > 0:
        excludeFields = [field.strip() for field in a.EXCLUDE_FIELDS.split(",")]  

    if includeFields is not None:
        fieldnames = includeFields

    if excludeFields is not None:
        fieldnames = [field for field in fieldnames if field not in excludeFields]

    if a.PROBE:
        print(f'Only including fields {fieldnames}')
        return

    # Write data to file
    writeCsv(a.OUTPUT_FILE, rows, fieldnames)

main(parseArgs())
