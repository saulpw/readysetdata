#!/usr/bin/env python3

import fileinput

from readysetdata import wikipedia, parse_jsonl, outputSingle, finish

for row in parse_jsonl(fileinput.input()):
    if row.title.startswith("List of "):
        # Exclude "List" articles
        continue

    body = row.revision.text['#text']

    for d in wikipedia.parse_infoboxes(body):
        outputSingle('wikipedia_infoboxes', d.infobox_type, dict(wp_title=row.title, **d), batch_size=1)

    if body.startswith("REDIRECT"):
        continue

    d = wikipedia.parse_summary(body)
    if d['first_paragraph'].startswith("REDIRECT"):
        continue

    outputSingle('wikipedia', 'article_summaries', dict(wp_title=row.title, **d), batch_size=1)


finish()
