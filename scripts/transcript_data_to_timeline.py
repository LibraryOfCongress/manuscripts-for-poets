"""Script exporting transcript data to timeline interface"""

# -*- coding: utf-8 -*-

import argparse
import collections
from pprint import pprint

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv", help="A BtP dataset file that has been run through: add_resource_data_to_transcript_data.py and parse_dates.py and resolve_dates.py")
    parser.add_argument("-notes", dest="ANNOTATION_FILE", default="data/mary-church-terrell-biographical-notes.csv", help="A .csv with annotations to the timeline")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="public/data/mary-church-terrell/timeline.json", help="Output JSON file")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to output transcript data to timeline interface"""

    # Make sure output dirs exist
    makeDirectories(a.OUTPUT_FILE)

    # Read data from .csv file
    pFields, docs = readCsv(a.INPUT_FILE)
    nFields, notes = readCsv(a.ANNOTATION_FILE)

    # Parse docs
    for i, doc in enumerate(docs):
        docs[i]["Index"] = int(doc["Index"])
        docs[i]["EstimatedYear"] = int(doc["EstimatedYear"]) if doc["EstimatedYear"] != "" else None
    docs = [d for d in docs if d["EstimatedYear"] is not None]
    validYears = [d["EstimatedYear"] for d in docs]
    print(f"{len(validYears)} docs with valid years")
    startYear, endYear = (min(validYears), max(validYears))
    print(f"Year range: {startYear} - {endYear}")

    containersNames = unique([d["Project"] for d in docs])
    print(f"{len(containersNames)} containers: {containersNames}")

    # Build containers for the timeline
    print("Building timeline...")
    containers = []
    counts = []
    for containerName in containersNames:
        containerYears = []
        for year in range(startYear, endYear + 1):
            matches = [d["Index"] for d in docs if d["EstimatedYear"] == year and d["Project"] == containerName]
            count = len(matches)
            containerYear = {
               "year": year,
               "count": count,
               "docs": matches
            }
            counts.append(count)
            containerYears.append(containerYear)
        container = {
            "title": containerName,
            "years": containerYears
        }
        containers.append(container)

    # Add normalized counts
    maxCount = max(counts)
    for i, container in enumerate(containers):
        for j, containerYear in enumerate(container["years"]):
            countN = 1.0 * containerYear["count"] / maxCount
            containers[i]["years"][j]["countN"] = round(countN, 3)
            containers[i]["years"][j]["color"] = valueToColor(lerp((0.2, 1), countN))
    print("Writing files to disk...")

    for i, note in enumerate(notes):
        notes[i]["dateStart"] = int(note["dateStart"])
        notes[i]["dateEnd"] = int(note["dateEnd"]) if note["dateEnd"] != "" else notes[i]["dateStart"]

    dataOut = {
        "collections": containers,
        "range": [startYear, endYear],
        "annotations": notes
    }
    writeJSON(a.OUTPUT_FILE, dataOut)

main(parseArgs())
