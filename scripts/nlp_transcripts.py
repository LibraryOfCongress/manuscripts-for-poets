"""Script for doing natural language processing of transcripts"""

# -*- coding: utf-8 -*-

import argparse
import spacy

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="INPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20.csv", help="A BtP dataset file. You can download these via script `get_transcript_data.py`")
    parser.add_argument("-filter", dest="FILTER", default="", help="Filter query string; leave blank if no filter")
    parser.add_argument("-out", dest="OUTPUT_FILE", default="data/output/mary-church-terrell-advocate-for-african-americans-and-women_2023-01-20_lemmas.csv", help="Output csv file")
    parser.add_argument("-probe", dest="PROBE", action="store_true", help="Just output details; do not process data")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to perform natural language processing on transcript data"""

    if not a.PROBE:
        # Make sure output dirs exist
        makeDirectories(a.OUTPUT_FILE)

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
        doc = nlp(transcript)

        for token in doc:
            # skip stop words
            if token.is_stop:
                continue
            # skip non-alphanum
            if token.pos_ in ['PUNCT', 'SPACE', 'CCONJ', 'X', 'SYM', 'NUM']:
                continue
            # skip ambiguous words
            if '?' in token.shape_:
                continue
            lemma = token.lemma_.lower()
            print(f"{token.text}\t{lemma}\t{token.pos_}\t{token.ent_type_}\t{token.ent_iob_}")
            index = len(lemmaIndex)
            if lemma in lemmaIndex:
                index = lemmaIndex.index(lemma)
            else:
                lemmaIndex.append(lemma)
                lemmas.append({
                    "lemma": lemma,
                    "pos": token.pos_,
                    "ent": token.ent_type_,
                    "count": 0,
                    "docs": []
                })
            lemmas[index]["count"] += 1
            lemmas[index]["docs"].append(row["Index"])
        printProgress(i+1, rowCount, "Progress: ")
        break

    if a.PROBE:
        return
    
    for i, lemma in enumerate(lemmas):
        lemmas[i]["docs"] = ";".join(lemma["docs"])

    # Write data to file
    fielnamesOut = ["lemma", "pos", "ent", "count", "docs"]
    writeCsv(a.OUTPUT_FILE, lemmas, fielnamesOut)

main(parseArgs())
