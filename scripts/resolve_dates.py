"""Script for making the best estimation of date of document"""

# -*- coding: utf-8 -*-

import argparse
import dateparser

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
    
    prevResourceId = None
    prevEstimatedDateStart = ""
    prevEstimatedDateEnd = ""

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
        estimatedDateStart = ""
        estimatedDateEnd = ""
        estimatedDateConfidence = 0

        if dateIsDay:
            estimatedDateStart = startDate.strftime(dateFormat)
            estimatedDateEnd = endDate.strftime(dateFormat)
            estimatedDateConfidence = 99

        else:
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
                    estimatedDateStart = transcriptDate.strftime(dateFormat)
                    transcriptDateEnd = transcriptDate + datetime.timedelta(days=1)
                    estimatedDateEnd = transcriptDateEnd.strftime(dateFormat)
                    estimatedDateConfidence = 75

                # parsed a year and the date metadata is a specific year or within a year
                elif dateIsWithinYear or dateIsYear:
                    estimatedDateStart = startDate.strftime(dateFormat)
                    estimatedDateEnd = endDate.strftime(dateFormat)
                    estimatedDateConfidence = 90

                # parsed a year
                else:
                    estimatedDateStart = transcriptDate.strftime(dateFormat)
                    transcriptDateEnd = datetime.datetime(transcriptDate.year + 1, transcriptDate.month, transcriptDate.day)
                    estimatedDateEnd = transcriptDateEnd.strftime(dateFormat)
                    estimatedDateConfidence = 50

            # if date range is greater than a year and not first in sequence, inheret the previous date
            elif (startDate is None or endDate is None or dateIsYearRange) and not firstInSequence:
                estimatedDateStart = prevEstimatedDateStart
                estimatedDateEnd = prevEstimatedDateEnd
                estimatedDateConfidence = 25

            # No date is available, defer to metadata date
            elif startDate is not None or endDate is not None:
                estimatedDateStart = startDate.strftime(dateFormat)
                estimatedDateEnd = endDate.strftime(dateFormat)
                estimatedDateConfidence = 90

        prevEstimatedDateStart = estimatedDateStart
        prevEstimatedDateEnd = estimatedDateEnd

        rows[i]["EstimatedDateStart"] = estimatedDateStart
        rows[i]["EstimatedDateEnd"] = estimatedDateEnd
        rows[i]["EstimatedDateConfidence"] = estimatedDateConfidence
        
        printProgress(i+1, rowCount, "Progress: ")

    if a.PROBE:
        return

    # Add fields to new data
    fieldsToAdd = ["EstimatedDateStart", "EstimatedDateEnd", "EstimatedDateConfidence"]
    for field in fieldsToAdd:
        if field not in fieldnames:
            fieldnames.append(field)

    # Write data to file
    writeCsv(OUTPUT_FILE, rows, fieldnames)

main(parseArgs())
