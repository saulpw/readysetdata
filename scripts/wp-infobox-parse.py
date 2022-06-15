#!/usr/bin/env python3

import fileinput
import json

from dxd.utils import Progress


def add_attr(d, oldkey, line):
    try:
        line = line.lstrip('| ')
        i = line.index('=')
        key = line[:i].strip()
        val = line[i+1:].strip()
        if val:
            d[key] = val
        return key
    except ValueError as e:  # no = in line
        if oldkey:
            d[oldkey] = d.get(oldkey, '') + line
        return oldkey


def parse_infobox(s):
    infoboxes = [] # a stack of (key, infobox, opens), since infoboxes can be nested

    key = None
    infobox = None
    opens = 0

    assert s.startswith('{{Infobox'), s
    assert s.endswith('}}')

    for line in s.splitlines():
        opens += line.count('{') - line.count('}')

        line = line.strip()
        if '{{Infobox' in line:
            i = line.index('{{Infobox')
            infobox_line = line[i:]
            if line.count('{') - line.count('}') < 0:
                continue
            cat, *rest = infobox_line[10:].split('|')
            d = dict(category=cat)
            for x in rest:
                add_attr(d, None, x)

            if '=' in line[:i]:  # pre-infobox line
                key = add_attr(d, key, line[:i])

            if infobox is None:
                assert key is None
                infobox = d
            else:
                infobox.setdefault('info_'+key, []).append(d)
                newopens = infobox_line[i:].count('{') - infobox_line[i:].count('}')
                infoboxes.append((key, infobox, opens-newopens))
                infobox = d
                opens = newopens

        elif line.startswith('|'):
            key = add_attr(infobox, key, line[1:])
        elif infobox and key:
            line = line.rstrip('} ')
            if line:
                infobox[key] = infobox.get(key, '')
        # else outside infobox, ignore it

        if opens == 0:
            if infoboxes:
                key, infobox, opens = infoboxes.pop(-1)
            else:
                return infobox


def annotate_braces(text):
    opens = 0  # number of open {{ remaining to be closed
    infobox = '' # current infobox string
    for line in text.splitlines():
        yield opens, line
        if infobox:
            line = html.unescape(line)
            opens += line.count('{') - line.count('}')

            infobox += line + '\n'

            if opens <= 0:
                infobox = ''
                opens = 0

        else:
            if '{{Infobox' in line:
                i = line.index('{{Infobox')
                line = line[i:]
                opens = line.count('{') - line.count('}')
                if opens == 0:
                    pass
                else:
                    infobox = line + '\n'
            # otherwise ignore it


def main():
    for text in Progress(fileinput.input()):
        row = json.loads(text)
        for box in row['infoboxes']:
            print(json.dumps(parse_infobox(box)))


main()
