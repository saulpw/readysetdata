#!/usr/bin/env python3

from dxd.utils import Progress


import fileinput
import html
import json
import re


def get_infoboxes(text):
    opens = 0  # number of open {{ remaining to be closed
    infobox = '' # current infobox string
    for line in text.splitlines():
        if infobox:
            line = html.unescape(line)
            opens += line.count('{') - line.count('}')

            infobox += line + '\n'

            if opens <= 0:
                yield infobox
                infobox = ''
                opens = 0

        else:
            while '{{Infobox' in line:
                i = line.index('{{Infobox')
                opens = 0
                for j, ch in enumerate(line[i:]):
                    if ch == '{':
                        opens += 1
                    elif ch == '}':
                        opens -= 1

                    if opens == 0:
                        yield line[i:i+j+1]
                        line = line[i+j+1:]
                        break

                if opens > 0:
                    infobox = line + '\n'


    if opens != 0:
        raise Exception('%d open braces leftover' % opens)

    assert not infobox, infobox


def main():
    for text in Progress(fileinput.input()):
        row = json.loads(text)
        t = row['text']
        t = re.sub(r'<!--.*?-->', '', t, flags=re.DOTALL)
        t = re.sub(r'<ref[^<]+?/>', '', t, flags=re.DOTALL)
        t = re.sub(r'<\s*ref.*?<\s*/ref', '', t, flags=re.DOTALL)
        row['cleaned_text'] = t
        row['infoboxes'] = list(get_infoboxes(t))
        print(json.dumps(row))


main()
