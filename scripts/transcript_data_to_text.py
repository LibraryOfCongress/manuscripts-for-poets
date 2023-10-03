"""Script exporting transcript data as raw text"""

# -*- coding: utf-8 -*-

import argparse

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="TRANSCRIPT_INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_correspondence.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="", help="Filter query string; leave blank if no filter")
    parser.add_argument("-sort", dest="SORT", default="", help="Sort query string; leave blank if no sort")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="", help="Output text file")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to output transcript data as raw text"""

    outputFile = a.OUTPUT_FILE.strip()
    if len(outputFile) <= 0:
        outputFile = replaceExtension(a.TRANSCRIPT_INPUT_FILE, ".txt")

    # Make sure output dirs exist
    makeDirectories(outputFile)

    # Read data from .csv file
    fieldnames, pages = readCsv(a.TRANSCRIPT_INPUT_FILE)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        pages = filterByQueryString(pages, a.FILTER)

     # Sort data if necessary
    if len(a.SORT) > 0:
        pages = sortByQueryString(pages, a.SORT)

    # Retrieve data from each page and build output string
    output = ""
    for page in pages:
        output += f"Item: {page['Item']} ({page['ItemAssetIndex']} of {page['ItemAssetCount']})\n"
        output += f"URL: {page['ResourceURL']}\n\n"
        output += f"{page['Transcription']}\n"
        output += "==========================================\n"

    print('Writing to file...')
    writeText(outputFile, output)

main(parseArgs())
