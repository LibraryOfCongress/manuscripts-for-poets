"""Script for adding indices to transcript data"""

# -*- coding: utf-8 -*-

import argparse
import spacy
import spacy_fastlang

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="", help="Output csv file; leave blank to update input file")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to add indices to data"""

    OUTPUT_FILE = a.OUTPUT_FILE if len(a.OUTPUT_FILE) > 0 else a.INPUT_FILE

    # Make sure output dirs exist
    makeDirectories(OUTPUT_FILE)

    fieldnames, rows = readCsv(a.INPUT_FILE)
    rowCount = len(rows)
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe("language_detector")

    for i, row in enumerate(rows):
        transcript = row["Transcription"]
        doc = nlp(transcript)
        rows[i]["lang"] = doc._.language
        printProgress(i+1, rowCount, "Progress: ")

    if "lang" not in fieldnames:
        fieldnames += ["lang"]

    # Write data to file
    writeCsv(OUTPUT_FILE, rows, fieldnames)

main(parseArgs())
