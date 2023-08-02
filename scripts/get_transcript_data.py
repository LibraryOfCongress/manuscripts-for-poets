"""Script for downloading transcript datasets given transcript URL(s)"""

# -*- coding: utf-8 -*-

# For a list of URLs, see:
#   https://www.loc.gov/search/?fa=contributor%3Aby+the+people+%28program%29&st=list&c=150
#
# Example usage:
#   python scripts/get_transcript_data.py -url "https://www.loc.gov/item/2020445590/,https://www.loc.gov/item/2021387726/"

import argparse
import os
import time

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", dest="URL", default="https://www.loc.gov/item/2021387726/", help="A URL to a BtP dataset page. Can be a comma-separated list of URLs. See full list at https://www.loc.gov/search/?fa=contributor%3Aby+the+people+%28program%29&st=list&c=150")
    parser.add_argument("-data", dest="DATA_DIR", default="data/", help="Output directory to store data files")
    parser.add_argument("-overwrite", dest="OVERWRITE", action="store_true", help="Overwrite existing data?")
    args = parser.parse_args()
    return args

def processUrl(url, a):
    """Function to process a single URL"""

    itemId = str(url.strip("/").split("/")[-1])
    itemDir = f"{a.DATA_DIR}{itemId}/"
    # Download item json data from loc.gov API
    filename = f"{itemDir}item.json"
    jsonUrl = f"{url}?fo=json"
    if a.OVERWRITE:
        removeDir(itemDir)
    makeDirectories(itemDir)
    print(f"Downloading {jsonUrl}...")
    download(jsonUrl, filename, overwrite=False)
    # Read the item json data
    data = readJSON(filename)
    if "resources" in data and "item" in data:
        fileFound = False
        if len(data["resources"]) > 0:
            resource = data["resources"][0]
            if "files" in resource and len(resource["files"]) > 0:
                # Retrieve file URL
                file = resource["files"][0][0]
                fileUrl = file["url"]
                # Build a filename for the downloaded file
                resouresFilename = f"{itemDir}resources.zip"
                resourcesDir = f"{itemDir}resources"
                # Download and unpack the file if necessary
                if not os.path.isdir(resourcesDir):
                    if not os.path.isfile(resouresFilename):
                        print(f"Downloading {fileUrl}...")
                        download(fileUrl, resouresFilename, overwrite=False)
                    print(f"Unzipping {resouresFilename}...")
                    unzipFile(resouresFilename, resourcesDir)
                    # remove zip file
                    removeFiles(resouresFilename)
                else:
                    print(f"{resourcesDir} already exists")
                fileFound = True
        if not fileFound:
            print(f"No valid file URL found in {url} json")

    else:
        print(f"Could not download valid data from {url}. May be a result of rate-limiting or the website being unavailable.")

def main(a):
    """Main function to process a list of one or more URLs"""

    # Make sure output dirs exist
    makeDirectories(a.DATA_DIR)

    # Convert URLs to list
    urls = [url.strip() for url in a.URL.strip(",").split(",")]

    # Download transcript resources from each url
    for url in urls:
        processUrl(url, a)
        time.sleep(1) # sleep to avoid rate limiting

main(parseArgs())
