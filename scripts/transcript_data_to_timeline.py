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
    parser.add_argument("-lemma", dest="LEMMA_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_lemmas.csv", help="A lemma .csv file generated via nlp_transcripts.py")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="public/data/mary-church-terrell/timeline.json", help="Output JSON file")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to output transcript data to timeline interface"""

    # Make sure output dirs exist
    makeDirectories(a.OUTPUT_FILE)

    # Read data from .csv file
    pFields, docs = readCsv(a.INPUT_FILE)
    lFields, lemmas = readCsv(a.LEMMA_FILE)

    # Parse docs
    for i, doc in enumerate(docs):
        docs[i]["Index"] = int(doc["Index"])
        docs[i]["EstimatedYear"] = int(doc["EstimatedYear"]) if doc["EstimatedYear"] != "" else None
        docs[i]["Lemmas"] = []
    validYears = [d["EstimatedYear"] for d in docs if d["EstimatedYear"] is not None]
    print(f"{len(validYears)} docs with valid years")
    startYear, endYear = (min(validYears), max(validYears))
    print(f"Year range: {startYear} - {endYear}")

    # Parse lemmas
    for i, lemma in enumerate(lemmas):
        lemmaDocs = [int(dindex) for dindex in lemma["docs"].split(";")]
        for docIndex in lemmaDocs:
            docs[docIndex]["Lemmas"].append(lemma["lemma"])
        lemmas[i]["docs"] = lemmaDocs
    print(f"POS: {unique([l['pos'] for l in lemmas])}")

    containersNames = unique([d["Project"] for d in docs])
    print(f"{len(containersNames)} containers: {containersNames}")

    # Build containers for the timeline
    print("Building timeline...")
    containers = []
    lemmasOut = []
    for containerName in containersNames:
        containerYears = []
        for year in range(startYear, endYear + 1):
            matches = [d["Index"] for d in docs if d["EstimatedYear"] == year and d["Project"] == containerName]
            containerYearLemmas = []
            for docIndex in matches:
                containerYearLemmas += docs[docIndex]["Lemmas"]
            containerYearLemmas = sorted(containerYearLemmas)
            counter = collections.Counter(containerYearLemmas)
            frequencies = counter.most_common(100)
            containerYears.append({
                "year": year,
                "count": len(matches),
                "lemmas": frequencies
            })
            lemmasOut += [lemma for lemma, count in frequencies]
        container = {
            "title": containerName,
            "years": containerYears
        }
        containers.append(container)

    print("Prepping data for output")
    lemmasOut = unique(lemmasOut)
    print(f"{len(lemmasOut)} lemmas matched for interface")
    # Replace words with word indices
    for i, container in enumerate(containers):
        for j, year in enumerate(container["years"]):
            updatedLemmas = []
            for lemmaText, count in year["lemmas"]:
                lemmaIndex = lemmasOut.index(lemmaText)
                updatedLemmas.append((lemmaIndex, count))
            containers[i]["years"][j]["lemmas"] = updatedLemmas

    # expand lemmas
    lemmasOut = [next(l for l in lemmas if l["lemma"] == lemma) for lemma in lemmasOut]

    docCols = ["ResourceID", "Project", "DownloadUrl", "Transcription", "ItemAssetIndex", "EstimatedYear"]
    for i, doc in enumerate(docs):
        if doc["EstimatedYear"] is None:
            for col in docCols:
                docs[i][col] = ""
    docRows, docGroups = unzipList(docs, docCols, ["ResourceID", "Project"])
    lemmaCols = ["lemma", "pos", "ent"]
    lemmaRows, lemmaGroups = unzipList(lemmasOut, lemmaCols, ["pos", "ent"])

    docFilename = appendToFilename(a.OUTPUT_FILE, "-transcripts")
    lemmaFilename = appendToFilename(a.OUTPUT_FILE, "-words")
    timelineFilename = a.OUTPUT_FILE

    print("Writing files to disk...")
    # Write JSON to file
    writeJSON(docFilename, {
        "cols": docCols,
        "rows": docRows,
        "groups": docGroups
    })
    writeJSON(lemmaFilename, {
        "cols": lemmaCols,
        "rows": lemmaRows,
        "groups": lemmaGroups
    })
    writeJSON(timelineFilename, containers)

main(parseArgs())
