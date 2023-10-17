"""Script for doing parsing sentences from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import spacy
from tabulate import tabulate

from utilities import *

# Arguments
def parseArgs():
    """Function to parse script arguments"""

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", dest="TEXT", default="A text string")
    args = parser.parse_args()
    return args

def main(a):
    """Main function to print text details"""

    # Morph details: https://universaldependencies.org/u/feat/index.html
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(a.TEXT)
    headers = ["text", "pos", "morph", "shape", "ent", "entPart"]
            #     print(f"{token.text}\tLEMMA:{token.lemma_}\tPOS:{token.pos_}\tTAG:{token.tag_}\tMORPH:${token.morph}\tSHAPE:{token.shape_}\tENT:{token.ent_type_}\tENT_PART:{token.ent_iob_}")

    rows = []
    for token in doc:
        rows.append([token.text, token.pos_, token.morph, token.shape_, token.ent_type_, token.ent_iob_])
    print(tabulate(rows, headers=headers))
    
main(parseArgs())
