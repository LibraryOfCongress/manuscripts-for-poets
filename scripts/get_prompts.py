"""Script for doing parsing sentences from transcripts"""

# -*- coding: utf-8 -*-

import argparse
from pprint import pprint
import re
import spacy

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="lang=en AND Project IN LIST Family letters|Speeches and writings|Diaries and journals: 1888-1951", help="Filter query string; leave blank if no filter")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_prompts.csv", help="Output csv file")
    parser.add_argument("-debug", dest="DEBUG", action="store_true", help="Debug?")
    args = parser.parse_args()
    return args

def checkVerb(nlp, token):
    """Test a verb by placing a You in front of it"""
    testText = f"You {token.text.lower()}"
    testDoc = nlp(testText)
    testToken = testDoc[1]
    return testToken

def getFirstValue(arr):
    """Get the first value of an array"""
    value = "None"
    if len(arr) > 0:
        value = arr[0]
    return value

def isImperative(nlp, span):
    """Check if a span of text is imperative"""
    value = None
    for i, token in enumerate(span):
        person = getFirstValue(token.morph.get("Person"))
        verbForm = getFirstValue(token.morph.get("VerbForm"))
        verbType = getFirstValue(token.morph.get("VerbType"))
        tense = getFirstValue(token.morph.get("Tense"))
        mood = getFirstValue(token.morph.get("Mood"))

        # Exclude if starts with noun or particle unless it is imperative
        if i == 0 and token.pos_ in ("NOUN", "PART") and mood != "Imp":
            value = False
            break

        # Only allow to start with 1st or 2nd person prounouns (I, you)
        if i == 0 and token.pos_ == "PRON":
            if person not in ("None", "1", "2"):
                value = False
                break
        
        # We hit a verb or verb-like word
        if token.pos_ == "VERB" or verbForm != "None" or verbType != "None":
            # only include infinitive form of verbs
            if verbForm == "Inf":
                # Put "You" in front on verb and double check if it is in present tense
                testToken = checkVerb(nlp, token)
                testTense = getFirstValue(testToken.morph.get("Tense"))
                if testTense == "Pres":
                    value = True
                else:
                    value = False
            # # or if verb is in Present tense and is Finite, or if mood is Imperative
            # elif (tense == "Pres" and verbForm == "Fin" and person not in ("1", "3")) or mood == "Imp":
            #     # Put "You" in front on verb and double check if it is in present tense
            #     testToken = checkVerb(nlp, token)
            #     testTense = getFirstValue(testToken.morph.get("Tense"))
            #     if testTense == "Pres":
            #         print(f"{normalizeText(span.text)} -- {token.pos_} -- {token.morph}")
            #         value = True
            #     else:
            #         value = False
            else:
                value = False
            break
        # Adverbs, etc are allowed up until we hit a verb
        elif token.pos_ not in ("ADV", "CCONJ", "AUX", "PART"):
            break
    return value

def isQuestion(nlp, span):
    value = None

    return value

def getWords(sent):
    """Retrieve a list of words from sentence"""
    nonwords = ['PUNCT', 'SPACE', 'X', 'SYM', 'NUM']
    words = [token for token in sent if token.pos_ not in nonwords]
    return words

def normalizeText(text):
    """Normalize a block of text"""
    text = ' '.join(text.split()) # replace all whitespace with single space
    text = re.sub(r"^[^a-zA-Z0-9]+", "", text) # remove non-alpha from beginning of string
    text = re.sub(r"[^a-zA-Z0-9\.!?]+$", "", text) # remove non-alpha and punct from end of string
    return text

def getSentences(nlp, transcript, minWords=3, maxWords=24):
    """Retrieve a list of sentences from a text"""
    doc = nlp(transcript)
    types=["imperative"]
    sents = list(doc.sents)
    validSents = []
    for sent in sents:
        text = normalizeText(sent.text)
        # skip sentences that are empty or start with lowercase
        if len(text) <= 0 or text[0].islower():
            continue

        # skip sentences with too little or too many words
        tokenCount = len(sent)
        words = getWords(sent)
        wordCount = len(words)
        if wordCount < minWords or wordCount > maxWords:
            continue

        # split sentence into clauses
        clauses = []
        clauseStart = 0
        clauseEnd = 0
        for j, token in enumerate(sent):
            if token.shape_ in (",", ";") and token.pos_ == "PUNCT":
                if clauseEnd > clauseStart:
                    clauses.append(sent[clauseStart:clauseEnd])
                clauseStart = j + 1
                clauseEnd = clauseStart
                continue
            clauseEnd += 1
        if clauseStart < tokenCount:
            clauses.append(sent[clauseStart:tokenCount])

        # Retrieve sentence type and filter
        sentenceType = "unknown"
        for j, clause in enumerate(clauses):
            isImperativeValue = isImperative(nlp, clause)
            if isImperativeValue is True:
                sentenceType = "imperative"
                break
            # False value only applies to first clause
            elif isImperativeValue is False and j == 0:
                break
            # only check the first two clauses for imperative
            elif j >= 1:
                break
        if types is not False and sentenceType not in types:
            continue

        # skip sentences with entities
        hasEntities = False
        for token in sent:
            if token.ent_type_ != "":
                hasEntities = True
                break
        if hasEntities:
            continue

        # skip sentences with numbers
        hasNumbers = False
        for token in sent:
            if token.pos_ == "NUM":
                hasNumbers = True
                break
        if hasNumbers:
            continue

        # skip sentences with question marks within the sentence
        hasAmbiguous = False
        for j, token in enumerate(sent):
            if token.shape_ == "?" and j < (tokenCount-1):
                hasAmbiguous = True
                break
        if hasAmbiguous:
            continue
        
        validSents.append({
            "text": text,
            "type": sentenceType
        })

        # print('=================================')
        # print(sent.as_doc().text)
        # print('------------------')
        # for token in sent:
        #     print(f"{token.text}\tLEMMA:{token.lemma_}\tPOS:{token.pos_}\tTAG:{token.tag_}\tMORPH:${token.morph}\tSHAPE:{token.shape_}\tENT:{token.ent_type_}\tENT_PART:{token.ent_iob_}")
    return validSents

def main(a):
    """Main function to perform natural language processing on transcript data"""

    # Make sure output dirs exist
    makeDirectories(a.OUTPUT_FILE)

    fieldnames, rows = readCsv(a.INPUT_FILE)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        rows = filterByQueryString(rows, a.FILTER)

    rowCount = len(rows)

    nlp = spacy.load("en_core_web_lg")

    # transcript = ("White men are neither punished for "
    #                 "invading it, not lynched for violating"
    #                 "Colored women and girls.")
    # rowSentences = getSentences(nlp, transcript)

    # Retrieve resource data for each row
    sentences = []
    for i, row in enumerate(rows):
        transcript = row["Transcription"]
        rowSentences = getSentences(nlp, transcript)
        for j, sent in enumerate(rowSentences):
            # print(sent["text"])
            # print("----------------------------------")
            rowSentences[j]["doc"] = row["Index"]
            rowSentences[j]["ResourceURL"] = row["ResourceURL"]
            rowSentences[j]["Project"] = row["Project"]
            rowSentences[j]["EstimatedYear"] = row["EstimatedYear"]
        sentences += rowSentences
        printProgress(i+1, rowCount, "Progress: ")

    if a.DEBUG:
        return

    # Write data to file
    fieldnamesOut = ["text", "type", "doc", "ResourceURL", "Project", "EstimatedYear"]
    writeCsv(a.OUTPUT_FILE, sentences, fieldnamesOut)

main(parseArgs())
