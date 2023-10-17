"""Script for doing parsing sentences from transcripts"""

# -*- coding: utf-8 -*-

import argparse
from pprint import pprint
import spacy

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_with-dates_selection.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="lang=en", help="Filter query string; leave blank if no filter")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_prompts.csv", help="Output csv file")
    parser.add_argument("-debug", dest="DEBUG", action="store_true", help="Debug?")
    args = parser.parse_args()
    return args

def isImperative(span):
    """Check if a span of text is imperative"""
    value = False
    for token in span:
        if token.pos_ == "VERB":
            # only include infinitive form of verbs
            verbForm = token.morph.get("VerbForm")
            if verbForm == "Inf" or "Inf" in verbForm:
                value = True
            break
        elif token.pos_ not in ("ADV", "CCONJ", "AUX", "PART"):
            break
    return value

def getWords(sent):
    """Retrieve a list of non-stop words from sentence"""
    words = []
    for token in sent:
        # skip stop words unless beginning of entity
        if token.is_stop and token.ent_iob_ != 'B':
            continue
        # skip non-alphanum unless beginning of entity
        if token.pos_ in ['PUNCT', 'SPACE', 'CCONJ', 'X', 'SYM', 'NUM'] and token.ent_iob_ != 'B':
            continue
        # skip ambiguous words unless beginning of entity
        if '?' in token.shape_ and token.ent_iob_ != 'B':
            continue
        words.append(token)
    return words

def getSentences(nlp, transcript, minWords=3, maxWords=60):
    """Retrieve a list of sentences from a text"""
    doc = nlp(transcript)
    types=["imperative"]
    sents = list(doc.sents)
    validSents = []
    for sent in sents:
        text = sent.as_doc().text.replace('\n', ' ').replace('\r', '').replace('  ', ' ')

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
            if token.shape_ == "," and token.pos_ == "PUNCT":
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
        for clause in clauses:
            if isImperative(clause):
                sentenceType = "imperative"
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
    rowCount = len(rows)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        rows = filterByQueryString(rows, a.FILTER)

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
        sentences += rowSentences
        printProgress(i+1, rowCount, "Progress: ")

    if a.DEBUG:
        return

    # Write data to file
    fieldnamesOut = ["text", "type", "doc", "ResourceURL"]
    writeCsv(a.OUTPUT_FILE, sentences, fieldnamesOut)

main(parseArgs())
