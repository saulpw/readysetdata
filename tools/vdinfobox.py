#!/usr/bin/env python3

import json

import re
import visidata
from visidata import Sheet, VisiData, Column, ColumnItem

import mwparserfromhell as mwp

def linktext(m):
    s = m.group(1)
    ret = s.split("|")[-1]

    if s.startswith("File:"): # image link
        ret = f' {ret} '  # spaces on either side for niceness

    return ret

def clean_wptext(t):
        t = re.sub(r'<!--.*?-->', '', t, flags=re.DOTALL)
        t = re.sub(r'<ref[^<]+?/>', '', t, flags=re.DOTALL)
        t = re.sub(r'<\s*ref.*?<\s*/ref>', '', t, flags=re.DOTALL)
        t = re.sub(r'<\s*span>(.*?)<\s*/span>', r'\1', t, flags=re.DOTALL)

        t = re.sub(r'\[\[(.*?)\]\]', linktext, t)   # delinkify links

        return t


@VisiData.api
def open_infobox(vd, p):
    return InfoboxSheet(p.name, source=p)

VisiData.open_jsonl = VisiData.open_infobox

class InfoboxSheet(Sheet):
    # rowdef: [row, box]
    columns = [
        Column('title', getter=lambda c, r: r[0]['title']),
        Column('text', width=0, getter=lambda c, r: r[0]['text']),
        ColumnItem('box', 1, width=80),
    ]

    def iterload(self):
        for i, text in enumerate(self.source):
            row = json.loads(text)
            for t in mwp.parse(clean_wptext(row['text']), skip_style_tags=True).filter_templates(recursive=False):
                name = t.name.lower()
                if name.startswith('infobox'):
                    yield [row, t]


visidata.main.vd_cli()
