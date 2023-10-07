"""Script for doing natural language processing of transcripts"""

# -*- coding: utf-8 -*-

import argparse
import os
from pprint import pprint
import spacy
from spacy.tokens import Doc

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="", help="Filter query string; leave blank if no filter")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_lemmas.csv", help="Output csv file")
    parser.add_argument("-cache", dest="CACHE_DIR", default="tmp/nlp_transcripts/", help="Folder for caching document nlp")
    parser.add_argument("-debug", dest="DEBUG", action="store_true", help="Debug?")
    parser.add_argument("-clean", dest="CLEAN", action="store_true", help="Clear the cache before running?")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to perform natural language processing on transcript data"""

    # Make sure output dirs exist
    makeDirectories(a.OUTPUT_FILE)
    makeDirectories(a.CACHE_DIR)

    if a.CLEAN:
        emptyDirectory(a.CACHE_DIR)

    fieldnames, rows = readCsv(a.INPUT_FILE)
    rowCount = len(rows)

    # Filter data if necessary
    if len(a.FILTER) > 0:
        rows = filterByQueryString(rows, a.FILTER)

    lemmas = []
    lemmaIndex = []
    nlp = spacy.load("en_core_web_lg")
    
    # Retrieve resource data for each row
    for i, row in enumerate(rows):
        transcript = row["Transcription"]
        if a.DEBUG:
            transcript = ("Saturday,  Sept.  23,  1905 "
                            "Today is my birthday "
                            "Phyllis and I arose before "
                            "breakfast and went to Takoma  "
                            "Park to get eggs and "
                            "golden rod. Mrs. Brown "
                            "from whom we usually "
                            "buy eggs was not home. "
                            "Then we gathered golden "
                            "rod and came home for "
                            "breakfast. I ripped some for "
                            "Addie the seamstress who "
                            "is sewing here and then I began  "
                            "to write on my address. "
                            "After dinner I walked "
                            "down town bought some "
                            "gilt braid to put on P's red "
                            "coat and a basket of grapes. "
                            "Detective Lacey has been suspended "
                            "from the police force. "
                            "       Sunday,  Sept.  24,  1905 "
                            "Read the papers, wrote "
                            "some, went with Phyllis "
                            "and Mr. Terrell to call on "
                            "Dr. Langston and his "
                            "French wife from Hayte. "
                            "Spoke French Phyllis looked "
                            "beautiful in new white "
                            "dress I designed. Spoke at "
                            "People's Church for Prof. Moore "
                            "in evening on Club work of "
                            "Colored Women and was "
                            "really deeply affected, when I "
                            "spoke of sacrifices made by "
                            "Col women who are forced to "
                            "leave home to do public "
                            "work. Went from there to True "
                            "Reformers Hall to attend service "
                            "of a new sect- The Church of God "
                            "and Saints of Christ founded by "
                            "Colored man ten years ago now "
                            "has 60000 followers. His name is Crowdy") 
        
        tmpFile = f"{a.CACHE_DIR}doc-{row['Index']}.json"
        doc = None

        if a.DEBUG:
            doc = nlp(transcript)

        else:
            # Read document from cache if exists
            if os.path.isfile(tmpFile):
                doc_json = readJSON(tmpFile)
                doc = Doc(nlp.vocab).from_json(doc_json)

            # Otherwise, run NLP and cache the result
            else:
                doc = nlp(transcript)
                doc_json = doc.to_json()
                writeJSON(tmpFile, doc_json)

        tokenCount = len(doc)
        docLemmas = []
        for j, token in enumerate(doc):
            if a.DEBUG:
                print(f"{token.text}\tLEMMA:{token.lemma_}\tPOS:{token.pos_}\tSHAPE:{token.shape_}\tENT:{token.ent_type_}\tENT_PART:{token.ent_iob_}")
                continue
            # skip stop words unless beginning of entity
            if token.is_stop and token.ent_iob_ != 'B':
                continue
            # if entity, only include person, event, organization, or nationalities/religous/political groups (NORP), geo-political entities (GPE)
            if token.ent_iob_ == 'B' and token.ent_type_ not in ('PERSON', 'EVENT', 'NORP', 'ORG', 'GPE'):
                continue
            # skip non-alphanum unless beginning of entity
            if token.pos_ in ['PUNCT', 'SPACE', 'CCONJ', 'X', 'SYM', 'NUM'] and token.ent_iob_ != 'B':
                continue
            # skip ambiguous words unless beginning of entity
            if '?' in token.shape_ and token.ent_iob_ != 'B':
                continue
            # skip if within an entity, but not the first token
            if token.ent_iob_ == 'I':
                continue
            
            lemma = token.lemma_

            # check for beginning of entity
            isEntity = False
            if token.ent_iob_ == 'B':
                isEntity = True
                lemma = token.text
                # look ahead to get the rest of the entity
                forwardIndex = j + 1
                while forwardIndex < tokenCount and doc[forwardIndex].ent_iob_ == 'I':
                    lemma = f"{lemma} {doc[forwardIndex].text}"
                    forwardIndex += 1

            # make lowercase unless it is an entity or proper noun
            if not isEntity and token.pos_ != 'PROPN':
                lemma = lemma.lower()

            docLemmas.append({
                "lemma": lemma,
                "pos": token.pos_,
                "ent": token.ent_type_,
                "sentiment": token.sentiment
            })

        # collapse adjacent proper nouns and entities
        removeIndices = []
        for j, dlemma in enumerate(docLemmas):
            if dlemma["ent"] != "":
                # look backward for proper nouns
                lemma = dlemma["lemma"]
                backwardIndex = j - 1
                while backwardIndex >= 0 and docLemmas[backwardIndex]["pos"] == 'PROPN' and docLemmas[backwardIndex]["ent"] == "" and "deleted" not in docLemmas[backwardIndex]:
                    lemma = f"{docLemmas[backwardIndex]['lemma']} {lemma}"
                    removeIndices.append(backwardIndex)
                    docLemmas[backwardIndex]["deleted"] = True
                    backwardIndex -= 1
                docLemmas[j]["lemma"] = lemma
        for j, dlemma in enumerate(docLemmas):
            if dlemma["ent"] != "":
                # look forward for proper nouns
                lemma = dlemma["lemma"]
                forwardIndex = j + 1
                while forwardIndex < len(docLemmas) and docLemmas[forwardIndex]["pos"] == 'PROPN' and docLemmas[forwardIndex]["ent"] == "" and "deleted" not in docLemmas[forwardIndex]:
                    lemma = f"{lemma} {docLemmas[forwardIndex]['lemma']}"
                    removeIndices.append(forwardIndex)
                    docLemmas[forwardIndex]["deleted"] = True
                    forwardIndex += 1
                docLemmas[j]["lemma"] = lemma
        
        if len(removeIndices) > 0:
            removeIndices = sorted(removeIndices, reverse=True)
            for index in removeIndices:
                docLemmas.pop(index)

        # add document lemmas to overall list
        for dlemma in docLemmas:
            lemma = dlemma["lemma"]
            # check to see if lemma exists in our index
            lookupLemma = lemma.lower()
            index = len(lemmaIndex)
            if lookupLemma in lemmaIndex:
                index = lemmaIndex.index(lookupLemma)
            else:
                lemmaIndex.append(lookupLemma)
                lemmas.append({
                    "lemma": lemma,
                    "pos": dlemma["pos"],
                    "ent": dlemma["ent"],
                    "sentiment": dlemma["sentiment"],
                    "count": 0,
                    "docs": []
                })
            lemmas[index]["count"] += 1
            if row["Index"] not in lemmas[index]["docs"]:
                lemmas[index]["docs"].append(row["Index"])
        printProgress(i+1, rowCount, "Progress: ")
        if a.DEBUG:
            break

    if a.DEBUG:
        # pprint(lemmas)
        return
    
    # convert list to string and sort by count
    for i, lemma in enumerate(lemmas):
        lemmas[i]["docs"] = ";".join(lemma["docs"])
    lemmas = sorted(lemmas, key=lambda k: -k["count"])

    # Write data to file
    fielnamesOut = ["lemma", "pos", "ent", "count", "sentiment", "docs"]
    writeCsv(a.OUTPUT_FILE, lemmas, fielnamesOut)

main(parseArgs())
