from itertools import chain
import re
import fileinput
import json

import mwparserfromhell as mwp
import dateutil.parser
import spacy

from readysetdata import parse_jsonl, AttrDict

__all__ = ['parse_infoboxes', 'parse_summary']

nlp = spacy.load("en_core_web_sm")

def parse_infoboxes(text):
    for t in mwp.parse(clean_wptext(text), skip_style_tags=True).filter_templates(recursive=False):
        name = t.name.lower()
        if name.startswith('infobox'):
            yield from infobox_to_dicts(t)


def parse_summary(text):
    t = mwp.parse(text).strip_code()
    t = re.sub(r' \([^a-z]*\)', '', t)
    t = re.sub(r'\([ ,;]*', '(', t)

    paragraphs = filter(lambda line: line.strip() and ('|' not in line.split()[0]),
                          t.split('\n'))


    first_para = next(paragraphs, '')
    r = nlp(first_para)

    return AttrDict(
               first_paragraph=first_para,
               first_sentence=str(next(r.sents, first_para)) if r else first_para
              )


def itervalues(n):
    if isinstance(n, mwp.nodes.template.Template):
        name = ''.join(x for x in n.name.lower().strip() if x not in ' -_')
        if name in ('break', 'brk', 'br', 'crlf', 'endflatlist', 'sup', 'thinsp'):
            pass

        elif 'list' in name or name.startswith('ubl') or name in ('nowrap', 'csv'):
            # in ('grid list', 'gridlist', 'plainlist', 'hlist', 'tree list', 'flatlist', 'unbulleted list', 'ublist', 'ubl', 'plain list', 'flat list', 'bulleted list', 'cslist', 'unbulleted_list'):
            for p in n.params:
                for x in mwp.parse(str(p), skip_style_tags=True).filter(recursive=False):
                    yield from itervalues(x)

        elif 'year' in name or name in ('bda', 'dda', 'bya', 'dya', 'birthdeathage', 'circa', 'c.',
                'deathdateandage', 'birthdateandage', 'birthdate', 'deathdate', 'startdate'):
            ymd = [x for x in n.params if '=' not in x]
            try:
                y, m, d = list(map(int, map(str, ymd[:3])))
                yield f'{y:04d}-{m:02d}-{d:02d}'
            except ValueError:
                if ymd:
                    try:
                        yield dateutil.parser.parse(ymd[0])
                    except Exception:
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


def infobox_to_dicts(t):
    r = AttrDict(infobox_type=t.name[8:].strip())
    ret = [r]
    for x in t.params:
        k = str(x.name).strip()
        v = []
        for n in x.value.nodes:
            if isinstance(n, mwp.nodes.template.Template) and n.name.lower().strip().startswith('infobox'):
                ret.extend(infobox_to_dicts(n))
            else:
                v.extend(itervalues(n))

        if len(v) == 1:
            v = v[0]

        if v:
            r[k] = v

    return ret


def linktext(m):
    s = m.group(1)
    ret = s.split("|")[-1]

    if s.startswith("File:"): # image link
        ret = f' {ret} '  # spaces on either side for niceness

    return ret


def clean_wptext(t):
    t = re.sub(r'<!--.*?-->', '', t, flags=re.DOTALL)  # HTML comments
    t = re.sub(r'<ref[^<]+?/>', '', t, flags=re.DOTALL)
    t = re.sub(r'<\s*ref.*?<\s*/ref>', '', t, flags=re.DOTALL)
    t = re.sub(r'<\s*span>(.*?)<\s*/span>', r'\1', t, flags=re.DOTALL)

    t = re.sub(r'\[\[(.*?)\]\]', linktext, t)   # delinkify links
    t = re.sub(r"'''?", '', t)
    t = re.sub(r'−|\u2212|\u2013|&minus;|&ndash;', '-', t)
    t = re.sub(r'&nbsp;', ' ', t)

    # from https://github.com/dijs/infobox-parser/blob/master/util/cleanSource.js

    t = re.sub(r'\|display=inline', '', t)
    t = re.sub(r'<sup>', '^', t)
    t = re.sub(r'<\/sup>', '', t)
    t = re.sub(r'\{\{sfn\|([^\}\}]+)\}\}', '', t) # Remove shortened footnote templates
    t = re.sub(r'\{\{efn\|([^\}\}]+)\}\}', '', t) # Remove explanatory footnotes
    t = re.sub(r'\{\{\s*nowrap\s*\|([^\n\}]+)\}\}', r'\1', t, flags=re.IGNORECASE) # Replace nowrap template with its content
    t = t.replace("|''See list''", '')
    t = t.replace('|class=nowrap', '')
    t = re.sub(r'|list_style=[^|}]*', '', t)

    return t
