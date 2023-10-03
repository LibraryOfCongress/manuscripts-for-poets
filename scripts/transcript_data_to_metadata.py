"""Script for extracting new metadata fields from transcript data"""

# -*- coding: utf-8 -*-

import argparse
from pprint import pprint
import re

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="TRANSCRIPT_INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="", help="Filter query string; leave blank if no filter")
    parser.add_argument('-key', dest="COLUMN_KEY", default="Item", help="Column key to match against")
    parser.add_argument('-pattern', dest="PATTERN", default=".*; ([a-zA-Z\. ]+) \(([a-z\-]+)\)[;,].*", help="String pattern")
    parser.add_argument('-fields', dest="PATTERN_FIELDS", default="Correspondent,Relation", help="Fields that the pattern maps to")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="", help="Output csv file; leave blank if we should just update the input file")
    parser.add_argument("-probe", dest="PROBE", action="store_true", help="Just output details; do not output data")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to extract new metadata fields from transcript data"""

    outputFile = a.OUTPUT_FILE if a.OUTPUT_FILE != "" else a.TRANSCRIPT_INPUT_FILE
    newFields = [field.strip() for field in a.PATTERN_FIELDS.split(",")]
    pattern = re.compile(a.PATTERN)

    # Read data from .csv file
    fieldnames, pages = readCsv(a.TRANSCRIPT_INPUT_FILE)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        pages = filterByQueryString(pages, a.FILTER)

    # Go through each page and find matches
    matches = []
    noMatches = []
    for i, page in enumerate(pages):
        pageMatches = pattern.match(str(page[a.COLUMN_KEY]))

        if pageMatches:
            match = []
            for j, field in enumerate(newFields):
                value = pageMatches.group(j+1)
                pages[i][field] = value
                match.append(value)
            matches.append(", ".join(match))

        else:
            noMatches.append(page[a.COLUMN_KEY])

    if len(noMatches) > 0:
        noMatches = unique(noMatches)
        print("No matches found for:")
        pprint(noMatches)

    if a.PROBE:
        pprint(unique(matches))
        return
    
    for field in newFields:
        if field not in fieldnames:
            fieldnames.append(field)

    # Make sure output dirs exist
    makeDirectories(outputFile)

    # Write data to file
    writeCsv(outputFile, pages, fieldnames)

    print("Done.")

main(parseArgs())
