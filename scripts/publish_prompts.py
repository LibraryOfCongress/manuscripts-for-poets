"""Script exporting transcript data to prompt interface"""

# -*- coding: utf-8 -*-

import argparse
from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv", help="A BtP dataset file that has been run through: add_resource_data_to_transcript_data.py and parse_dates.py and resolve_dates.py")
    parser.add_argument("-prompts", dest="PROMPT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_prompts.csv", help="A prompt .csv file generated via get_prompts.py")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="public/data/mary-church-terrell/prompts.json", help="Output JSON file")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to output prompt data to prompt interface"""

    # Make sure output dirs exist
    makeDirectories(a.OUTPUT_FILE)

    # Read data from .csv file
    dFields, docs = readCsv(a.INPUT_FILE)
    pFields, prompts = readCsv(a.PROMPT_FILE)

    # Parse docs
    for i, doc in enumerate(docs):
        docs[i]["Index"] = int(doc["Index"])
        docs[i]["EstimatedYear"] = int(doc["EstimatedYear"]) if doc["EstimatedYear"] != "" else "Undated"
        url = doc["DownloadUrl"]
        url = url.replace("http://tile.loc.gov/image-services/iiif/", "")
        url = url.replace("/full/pct:100/0/default.jpg", "")
        docs[i]["DownloadUrl"] = url
    docs = sorted(docs, key=lambda k: k["Index"])

    # Remove duplicate prompts
    promptGroups = groupList(prompts, "text")
    prompts = []
    for group in promptGroups:
        prompts.append(group["items"][0])

    # Add metadata to prompts
    for i, prompt in enumerate(prompts):
        docIndex = int(prompt["doc"])
        prompts[i]["doc"] = docIndex
        pdoc = docs[docIndex]
        for field in ["ItemAssetIndex", "ResourceID", "Item"]:
            prompts[i][field] = pdoc[field]

    # Retrieve matched docs
    docIndices = unique([p["doc"] for p in prompts])
    matchedDocs = []
    for i, index in enumerate(docIndices):
        doc = docs[index]
        doc["newIndex"] = i
        matchedDocs.append(doc)

    # Re-map doc indices
    for i, prompt in enumerate(prompts):
        doc = findInList(matchedDocs, "Index", prompt["doc"])
        prompts[i]["doc"] = doc["newIndex"]

    # Get date range
    validYears = [d["EstimatedYear"] for d in matchedDocs if d["EstimatedYear"] != "Undated"]
    print(f"{len(validYears)} docs with valid years")
    startYear, endYear = (min(validYears), max(validYears))
    print(f"Year range: {startYear} - {endYear}")

    # Get containers
    containersNames = unique([d["Project"] for d in matchedDocs])
    print(f"{len(containersNames)} containers: {containersNames}")

    # Write prompts
    promptCols = ["text", "type", "doc", "Project", "EstimatedYear", "ItemAssetIndex", "ResourceID", "Item"]
    promptGroups = ["type", "Project", "ResourceID", "Item"]
    promptRows, promptGroups = unzipList(prompts, promptCols, promptGroups)
    jsonOut = {
        "prompts": {
            "cols": promptCols,
            "rows": flattenList(promptRows),
            "groups": promptGroups
        },
        "subCollections": containersNames,
        "timeRange": [startYear, endYear]
    }
    writeJSON(a.OUTPUT_FILE, jsonOut)

    # Write docs
    docCols = ["ResourceID", "Item", "DownloadUrl", "Transcription", "ItemAssetIndex"]
    docGroups = ["ResourceID", "Item"]
    docRows, docGroups = unzipList(matchedDocs, docCols, docGroups)
    jsonOut = {
        "docs": {
            "cols": docCols,
            "rows": flattenList(docRows),
            "groups": docGroups
        }
    }
    writeJSON(appendToFilename(a.OUTPUT_FILE, "-docs"), jsonOut)

main(parseArgs())
