"""Utility functions to support all scripts"""

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

def unzipFile(filename, targetDir=False):
    """Function for unzipping a zipped file."""
    if targetDir is False:
        targetDir = filename[:-4] # assuming the filepath ends with .zip
    with zipfile.ZipFile(filename, "r") as r:
        r.extractall(targetDir)
