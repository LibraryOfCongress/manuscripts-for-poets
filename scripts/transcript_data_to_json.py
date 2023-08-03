"""Script for downloading item metadata from transcript data"""

# -*- coding: utf-8 -*-

# Example usage:
#   python scripts/transcript_data_to_json.py 
#       -transcript "data/2021387726/resources/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv"
#       -filter "Project=Letters between friends, allies, and others"
#       -out "public/data/mary-church-terrell-correspondence/transcripts.json"

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

    fieldnames, rows = readCsv(a.TRANSCRIPT_INPUT_FILE)

main(parseArgs())
