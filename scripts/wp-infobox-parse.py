#!/usr/bin/env python3

import fileinput
import json
import sys
import re

from itertools import chain

import mwparserfromhell as mwp


def parse_infoboxes(s):
    for t in mwp.parse(s, skip_style_tags=True).filter_templates(recursive=False):
        name = t.name.lower()
        if name.startswith('infobox'):
            yield t

def iterparse(s):
    yield from mwp.parse(s, skip_style_tags=True).filter(recursive=False)

def itervalues(n):
            if isinstance(n, mwp.nodes.template.Template):
                name = ''.join(x for x in n.name.lower().strip() if x not in ' -_')
                if name in ('break', 'brk', 'br', 'crlf', 'endflatlist', 'sup', 'thinsp'):
                    pass
#                elif name == 'infobox':
#                    for x in iterparse(str(n)):
#                        yield from itervalues(x)
                elif 'list' in name or name.startswith('ubl') or name in ('nowrap', 'csv'):
                    # in ('grid list', 'gridlist', 'plainlist', 'hlist', 'tree list', 'flatlist', 'unbulleted list', 'ublist', 'ubl', 'plain list', 'flat list', 'bulleted list', 'cslist', 'unbulleted_list'):
                    for p in n.params:
                        for x in iterparse(str(p)):
                            yield from itervalues(x)
#                        if '=' in p: # FIXME
#                            continue
#                        for y in ' '.join(chain(*(itervalues(x) for x in iterparse(str(p))))).splitlines():
#                            r = y.strip('* \n')
#                            if r:
#                                yield r
                elif 'date' in name or 'year' in name or name in ('bda', 'dda', 'bya', 'dya', 'birthdeathage', 'circa', 'c.'):
                    ymd = [x for x in n.params if '=' not in x]
                    try:
                        y, m, d = list(map(int, map(str, ymd[:3])))
                        yield f'{y:04d}-{m:02d}-{d:02d}'
                    except ValueError:
                        if ymd:
                            yield ymd[0].strip()
                elif name in ('big', 'small', 'smaller', 'nowrap', 'nobold', 'url', 'marriage', 'married', 'website', 'center', 'awd'):
                    yield ':'.join(str(p).strip() for p in n.params if '=' not in p)
                else:
                    r = str(n).strip()
                    if r:
                        yield r
            elif isinstance(n, mwp.nodes.tag.Tag):
                if n.tag in ('li', 'i', 'b', 'br'):
                    yield from itervalues(n.contents)
                else:
                    r = f'<{n.tag}> {n}'.strip()
                    if r:
                        yield r

            else:
                r = str(n).strip()
                if r:
                    yield r


def infobox_to_dict(t):
    r = dict(infobox_type=t.name[8:].strip())
    more_infoboxes = []
    for x in t.params:
        k = str(x.name).strip()
        v = []
        for n in x.value.nodes:
            if isinstance(n, mwp.nodes.template.Template) and n.name.lower().strip().startswith('infobox'):
                more_infoboxes.append(n)
            else:
                v.extend(itervalues(n))

        if len(v) == 1:
            v = v[0]

        if v:
            r[k] = v
    return r, more_infoboxes


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


def main():
    for i, text in enumerate(fileinput.input()):
        row = json.loads(text)

        for box in parse_infoboxes(clean_wptext(row['text'])):

            if '--debug' in sys.argv:
                print(i, row['title'], file=sys.stderr)
                sys.stderr.flush()

            infoboxes = [box]
            while infoboxes:
                out = dict(title=row['title'])
                d, more = infobox_to_dict(infoboxes.pop())
                infoboxes.extend(more)
                out.update(d)

            print(json.dumps(out))

main()
