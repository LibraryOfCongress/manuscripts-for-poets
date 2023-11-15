"""Script for making the best estimation of date of document"""

# -*- coding: utf-8 -*-

import argparse
import dateparser
import datetime
import re

from utilities import *

def isSpecificDate(date):
    if date is None:
        return False
    return date.month > 1 or date.day > 1

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv", help="A BtP dataset file that has been run through: add_resource_data_to_transcript_data.py and parse_dates.py")
    parser.add_argument("-filter", dest="FILTER", default="", help="Filter query string; leave blank if no filter")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="", help="Output csv file; leave blank to update input file")
    parser.add_argument("-probe", dest="PROBE", action="store_true", help="Just output details; do not process data")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to make the best estimation of date of document"""

    OUTPUT_FILE = a.OUTPUT_FILE if len(a.OUTPUT_FILE) > 0 else a.INPUT_FILE
    if not a.PROBE:
        # Make sure output dirs exist
        makeDirectories(OUTPUT_FILE)

    fieldnames, rows = readCsv(a.INPUT_FILE)
    rowCount = len(rows)
    dateFormat = "%Y-%m-%d"

    # Filter data if necessary
    if len(a.FILTER) > 0:
        rows = filterByQueryString(rows, a.FILTER)
        rowCount = len(rows)
    
    prevResourceId = None
    prevEstimatedDateStart = None
    prevEstimatedDateEnd = None
    datesFromMetadataUsed = 0
    datesFromTranscriptsUsed = 0
    estimatedDatesUsed = 0

    # Retrieve resource data for each row
    for i, row in enumerate(rows):
        transcriptDates = []
        dates = row["Dates"]

        resourceID = row["ResourceID"]
        firstInSequence = resourceID != prevResourceId
        prevResourceId = resourceID

        startDate, endDate = getDateRange(dates)
        deltaDays = 0
        if startDate is not None and endDate is not None:
            deltaDays = (endDate - startDate).days
        dateIsDay = 0 < deltaDays < 2
        dateIsWithinYear = 1 < deltaDays < 365
        dateIsYear = 365 <= deltaDays <= 366
        dateIsYearRange = deltaDays > 366
        estimatedDateStart = None
        estimatedDateEnd = None
        estimatedDateConfidence = 0

        # Exact year is already set in data
        if dateIsDay:
            estimatedDateStart = startDate
            estimatedDateEnd = endDate
            estimatedDateConfidence = 99
            datesFromMetadataUsed += 1

        # Check to see if it's in the title
        if estimatedDateStart is None or estimatedDateEnd is None:
            title = row["Item"]
            # check for circa specific year, e.g. circa 1903
            pattern = re.compile(r".*circa (1[0-9][0-9][0-9]) .*")
            matches = pattern.match(title)
            if matches:
                estimatedDateStart = datetime.datetime(int(matches.group(1)), 1, 1)
                estimatedDateEnd = datetime.datetime(int(matches.group(1))+1, 1, 1)
                estimatedDateConfidence = 80
                dateIsDay = True
                datesFromMetadataUsed += 1

            # check for circa specific range, e.g. circa 1880-1884
            else:
                pattern = re.compile(r".*circa (1[0-9][0-9][0-9])\-(1[0-9][0-9][0-9]).*")
                matches = pattern.match(title)
                if matches:
                    startDate = datetime.datetime(int(matches.group(1)), 1, 1)
                    endDate = datetime.datetime(int(matches.group(2)), 1, 1)
                    deltaDays = (endDate - startDate).days
                    dateIsDay = 0 < deltaDays < 2
                    dateIsWithinYear = 1 < deltaDays < 365
                    dateIsYear = 365 <= deltaDays <= 366
                    dateIsYearRange = deltaDays > 366
            
        if not dateIsDay:
            transcriptDate = None
            transcriptDates = [dateparser.parse(d, settings={'REQUIRE_PARTS': ['year'], 'PREFER_DAY_OF_MONTH': 'first'}) for d in row["TranscriptDates"].split(" | ")]
            if len(transcriptDates) > 0:
                # choose the first date that is within the metadata date range
                for date in transcriptDates:
                    if date is None:
                        continue
                    date = date.replace(tzinfo=None)
                    if startDate is None or endDate is None or startDate <= date <= endDate:
                        transcriptDate = date
                        break
            
            if startDate is not None and endDate is not None and transcriptDate is not None:
                # parsed a specific date
                if isSpecificDate(transcriptDate):
                    estimatedDateStart = transcriptDate
                    estimatedDateEnd = transcriptDate + datetime.timedelta(days=1)
                    estimatedDateConfidence = 75

                # parsed a year and the date metadata is a specific year or within a year
                elif dateIsWithinYear or dateIsYear:
                    estimatedDateStart = startDate
                    estimatedDateEnd = endDate
                    estimatedDateConfidence = 90

                # parsed a year
                else:
                    estimatedDateStart = transcriptDate
                    estimatedDateEnd = datetime.datetime(transcriptDate.year + 1, transcriptDate.month, transcriptDate.day)
                    estimatedDateConfidence = 50

                datesFromTranscriptsUsed += 1

            # if date range is greater than a year and not first in sequence, inheret the previous date
            elif (startDate is None or endDate is None or dateIsYearRange) and not firstInSequence:
                estimatedDateStart = prevEstimatedDateStart
                estimatedDateEnd = prevEstimatedDateEnd
                estimatedDateConfidence = 25
                estimatedDatesUsed += 1

            # No date is available, defer to metadata date
            elif startDate is not None or endDate is not None:
                estimatedDateStart = startDate
                estimatedDateEnd = endDate
                estimatedDateConfidence = 90

        prevEstimatedDateStart = estimatedDateStart
        prevEstimatedDateEnd = estimatedDateEnd

        rows[i]["EstimatedDateStart"] = estimatedDateStart.strftime(dateFormat) if estimatedDateStart is not None else ""
        rows[i]["EstimatedDateEnd"] = estimatedDateEnd.strftime(dateFormat) if estimatedDateEnd is not None else ""
        rows[i]["EstimatedDateConfidence"] = estimatedDateConfidence

        deltaDays = (estimatedDateEnd - estimatedDateStart).days
        # If range under 10 years, take the middle
        if deltaDays < (365 * 10):
            deltaYears = 0.5 * (estimatedDateEnd.year - estimatedDateStart.year)
            rows[i]["EstimatedYear"] = estimatedDateStart.year + int(deltaYears)
        
        printProgress(i+1, rowCount, "Progress: ")

    if a.PROBE:
        print(f"{datesFromMetadataUsed} dates from metadata used ({1.0*datesFromMetadataUsed/rowCount*100}% of total)")
        print(f"{datesFromTranscriptsUsed} dates from transcripts used ({1.0*datesFromTranscriptsUsed/rowCount*100}% of total)")
        print(f"{datesFromTranscriptsUsed+estimatedDatesUsed} dates used if we use proximity estimation ({1.0*(datesFromTranscriptsUsed+estimatedDatesUsed)/rowCount*100}% of total)")
        
        return

    # Add fields to new data
    fieldsToAdd = ["EstimatedDateStart", "EstimatedDateEnd", "EstimatedDateConfidence", "EstimatedYear"]
    for field in fieldsToAdd:
        if field not in fieldnames:
            fieldnames.append(field)

    # Write data to file
    writeCsv(OUTPUT_FILE, rows, fieldnames)

main(parseArgs())
