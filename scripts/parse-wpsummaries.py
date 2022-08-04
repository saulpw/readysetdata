#!/usr/bin/env python3

import fileinput
import json
import spacy

from readysetdata import wikipedia, parse_jsonl

nlp = spacy.load("en_core_web_sm")

for row in parse_jsonl(fileinput.input()):
    if row.title.startswith("List of "):
        # Exclude "List" articles
        continue

    text = row.revision.text['#text']
    d = wikipedia.get_first_paragraph(text)
    out = dict(wp_title=row.title, shard=row.title[0].lower())
    out.update(d)

    if "first_paragraph" in out and out["first_paragraph"] is not None:
        nlp_result = nlp(out["first_paragraph"])
        if nlp_result:
            sentences = list(nlp_result.sents)
            if sentences:
                out["first_sentence"] = str(sentences[0])
            else:
                out["first_sentence"] = out["first_paragraph"]
            print(json.dumps(out))
