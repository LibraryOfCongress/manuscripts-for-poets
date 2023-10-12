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
    parser.add_argument("-out", dest="OUTPUT_FILE", default="public/data/mary-church-terrell/cloud.json", help="Output JSON file")
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
        lemmas[i]["Index"] = i
        lemmaDocs = [int(dindex) for dindex in lemma["docs"].split(";")]
        for docIndex in lemmaDocs:
            docs[docIndex]["Lemmas"].append(i)
        lemmas[i]["docs"] = lemmaDocs

    containersNames = unique([d["Project"] for d in docs])
    print(f"{len(containersNames)} containers: {containersNames}")

    # Build buckets for the wordcloud
    print("Building wordcloud...")
    buckets = []
    for i, containerName in enumerate(containersNames):
        for year in range(startYear, endYear + 1):
            matches = [d["Index"] for d in docs if d["EstimatedYear"] == year and d["Project"] == containerName]
            containerYearLemmas = []
            for docIndex in matches:
                containerYearLemmas += docs[docIndex]["Lemmas"]
            counter = collections.Counter(containerYearLemmas)
            frequencies = counter.most_common(1000)
            for lemmaIndex, count in frequencies:
                buckets.append({
                    "_lemmaIndex": lemmaIndex,
                    "subcollectionIndex": i,
                    "year": year,
                    "count": count
                })

    print("Prepping lemmas for output")
    lemmaIndices = unique([b["_lemmaIndex"] for b in buckets])
    lemmaCount = len(lemmaIndices)
    lemmasOut = []
    docLemmasOut = []
    lemmaMap = {}
    for i, lemmaIndex in enumerate(lemmaIndices):
        lemmaMap[lemmaIndex] = i
        lemma = lemmas[lemmaIndex]
        if lemma["ent"] != "":
            lemma["pos"] = "ENTITY"
        lemma["Index"] = i
        lemma["sentiment"] = 0
        docIndices = lemma["docs"]
        for docIndex in docIndices:
            docLemmasOut.append((i, docIndex))
        lemmasOut.append(lemma)
        printProgress(i+1, lemmaCount)
    print(f"{lemmaCount} lemmas matched for interface")
    partsOfSpeech = sorted(unique([l['pos'] for l in lemmasOut]))
    print(f"POS: {partsOfSpeech}")

    print('Re-mapping lemma indices...')
    for i, bucket in enumerate(buckets):
        buckets[i]["wordIndex"] = lemmaMap[bucket["_lemmaIndex"]]

    lemmaCols = ["lemma", "pos", "sentiment"]
    lemmaRows, lemmaGroups = unzipList(lemmasOut, lemmaCols, ["pos"])

    bucketCols = ["wordIndex", "subcollectionIndex", "year", "count"]
    bucketRows, bucketGroups = unzipList(buckets, bucketCols, [])

    jsonOut = {
        "words": {
            "cols": lemmaCols,
            "rows": flattenList(lemmaRows),
            "groups": lemmaGroups
        },
        "wordDocs": flattenList(docLemmasOut),
        "wordBuckets": {
            "cols": bucketCols,
            "rows": flattenList(bucketRows),
            "groups": bucketGroups
        },
        "subCollections": containersNames,
        "partsOfSpeech": partsOfSpeech
    }

    print("Writing files to disk...")
    writeJSON(a.OUTPUT_FILE, jsonOut)

main(parseArgs())
