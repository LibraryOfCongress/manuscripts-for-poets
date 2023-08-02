"""Utility functions to support all scripts"""

import csv
import glob
import json
import os
import re
import shutil
import zipfile

import requests

def copyFile(src, dst):
    """Function copying file from src to dst."""
    shutil.copyfile(src, dst)

def download(url, filename, overwrite=False):
    """Function for downloading an arbitrary file as binary file."""
    if os.path.isfile(filename) and not overwrite:
        print(f"{filename} already exists.")
        return
    r = requests.get(url, stream=True, timeout=30)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    print(f"Downloaded {filename}.")

def emptyDirectory(dirname):
    """Function for emptying a directory"""
    dirname = dirname.strip("/")
    files = f"{dirname}/*"
    removeFiles(files)

def filterByQuery(arr, ors, delimeter="|", caseSensitive=False):
    """Filters a list given a set of rules"""
    if isinstance(ors, tuple):
        ors = [[ors]]

    if len(ors) < 1:
        return arr

    results = []
    for item in arr:
        for ands in ors:
            andValid = True
            for key, comparator, value in ands:
                value = str(value)
                itemValue = str(item[key])
                if not caseSensitive:
                    value = value.lower()
                    itemValue = itemValue.lower()
                if comparator not in ["CONTAINS", "EXCLUDES", "CONTAINS LIST", "EXCLUDES LIST", "IN LIST", "NOT IN LIST"]:
                    value = parseNumber(value)
                    itemValue = parseNumber(itemValue)
                if comparator in ["IN LIST", "NOT IN LIST", "CONTAINS LIST", "EXCLUDES LIST"]:
                    value = [v.strip() for v in value.split(delimeter)]
                if comparator == "<=" and itemValue > value:
                    andValid = False
                    break
                elif comparator == ">=" and itemValue < value:
                    andValid = False
                    break
                elif comparator == "<" and itemValue >= value:
                    andValid = False
                    break
                elif comparator == ">" and itemValue <= value:
                    andValid = False
                    break
                elif comparator == "IN LIST" and itemValue not in value:
                    andValid = False
                    break
                elif comparator == "NOT IN LIST" and itemValue in value:
                    andValid = False
                    break
                elif comparator == "CONTAINS LIST":
                    andValid = False
                    for v in value:
                        if v in itemValue:
                            andValid = True
                            break
                    break
                elif comparator == "EXCLUDES LIST":
                    for v in value:
                        if v in itemValue:
                            andValid = False
                            break
                    break
                elif comparator == "CONTAINS" and value not in itemValue:
                    andValid = False
                    break
                elif comparator == "EXCLUDES" and value in itemValue:
                    andValid = False
                    break
                elif comparator == "!=" and itemValue == value:
                    andValid = False
                    break
                elif comparator == "=" and itemValue != value:
                    andValid = False
                    break
            if andValid:
                results.append(item)
                break
    return results

def filterByQueryString(arr, str):
    """Filters a list given a query string"""
    queries = [parseQueryString(str) for str in str.split(" | ")]
    filteredArr = arr[:]
    for query in queries:
        filteredArr = filterByQuery(filteredArr, query)
    return filteredArr

def getFilenames(fileString, verbose=False):
    """Function for retrieve a list of files given a string."""
    files = []
    if "**" in fileString:
        files = glob.glob(fileString, recursive=True)
    if "*" in fileString:
        files = glob.glob(fileString)
    else:
        files = [fileString]
    fileCount = len(files)
    files = sorted(files)
    if verbose:
        print(f"Found {fileCount} files")
    return files

def makeDirectories(filenames):
    """Function for creating directories if they do not exist."""
    if not isinstance(filenames, list):
        filenames = [filenames]
    for filename in filenames:
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

def parseNumber(string, alwaysFloat=False):
    """Given a string, attempts to parse a number"""
    if isinstance(string, list):
         return string
    try:
        num = float(string)
        if "." not in str(string) and "e" not in str(string) and not alwaysFloat:
            num = int(string)
        return num
    except ValueError:
        return string
    except TypeError:
        return ""

def parseQueryString(str):
    """Function for parsing a query string"""
    if len(str) <= 0:
        return []
    comparators = ["<=", ">=", " NOT IN LIST ", " IN LIST ", " EXCLUDES LIST ", " CONTAINS LIST ", " EXCLUDES ", " CONTAINS ", "!=", ">", "<", "="]
    orStrings = str.split(" OR ")
    ors = []
    for orString in orStrings:
        andStrings = orString.split(" AND ")
        ands = []
        for andString in andStrings:
            for comparator in comparators:
                if comparator in andString:
                    parts = [part.strip() for part in andString.split(comparator)]
                    ands.append(tuple([parts[0], comparator.strip(), parts[1]]))
                    break
        ors.append(ands)
    return ors

def readCsv(filename, skipLines=0, encoding="utf-8-sig", readDict=True, verbose=True):
    """Function for reading a csv file given a filename string."""
    rows = []
    fieldnames = []
    if os.path.isfile(filename):
        lines = []
        with open(filename, 'r', encoding=encoding, errors="replace") as f:
            lines = list(f)
        if skipLines > 0:
            lines = lines[skipLines:]
        if readDict:
            reader = csv.DictReader(lines, skipinitialspace=True)
            fieldnames = list(reader.fieldnames)
        else:
            reader = csv.reader(lines, skipinitialspace=True)
        rows = list(reader)
        if verbose:
            print(f"Read {len(rows)} rows from {filename}")
    return (fieldnames, rows)

def readJSON(filename):
    """Function for reading a json file given a filename string."""
    data = {}
    if os.path.isfile(filename):
        with open(filename, encoding="utf8") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                data = {}
    return data

def removeDir(path):
    """Function for removing a directory given path string."""
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)

def removeFiles(listOrString):
    """Function for removing a list of files given a string or list."""
    filenames = listOrString
    if not isinstance(listOrString, list) and "*" in listOrString:
        filenames = glob.glob(listOrString)
    elif not isinstance(listOrString, list):
        filenames = [listOrString]
    print(f"Removing {len(filenames)} files")
    for fn in filenames:
        if os.path.isfile(fn):
            os.remove(fn)

def stringToFilename(string):
    """Function to convert an arbitrary string to a valid filename string."""
    string = str(string)

    # normalize whitespace
    string = string.replace("-", " ")
    string = string.replace("_", " ")
    string = " ".join(string.split())

    # Replace spaces with dashes
    string = re.sub(r"\s+", "-", string).strip()

    # Remove invalid characters
    string = re.sub(r"[^0-9a-zA-Z\-]", "", string)

    # Remove leading characters until we find a letter or number
    string = re.sub(r"^[^0-9a-zA-Z]+", "", string)

    return string

def unique(arr):
    """Function for turning a list of values into a list of unique values"""
    return list(set(arr))

def unzipFile(filename, targetDir=False):
    """Function for unzipping a zipped file."""
    if targetDir is False:
        targetDir = filename[:-4] # assuming the filepath ends with .zip
    with zipfile.ZipFile(filename, "r") as r:
        r.extractall(targetDir)
