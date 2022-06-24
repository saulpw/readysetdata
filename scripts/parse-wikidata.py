#!/usr/bin/env python3

import fileinput
import json

from readysetdata import parse_jsonl, AttrDict, output1


def getattrdeep(obj, attr, *default, getter=getattr):
    try:
        'Return dotted attr (like "a.b.c") from obj, or default if any of the components are missing.'
        if not isinstance(attr, str):
            return getter(obj, attr, *default)

        try:  # if attribute exists, return toplevel value, even if dotted
            if attr in obj:
                return getter(obj, attr)
        except Exception as e:
            pass

        attrs = attr.split('.')
        for a in attrs[:-1]:
            obj = getter(obj, a)

        return getter(obj, attrs[-1])
    except Exception as e:
        if not default: raise
        return default[0]


def getitem(o, k, default=None):
    return default if o is None else o[k]

def getitemdeep(obj, k, *default):
    return getattrdeep(obj, k, *default, getter=getitem)

def intfloat(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def wdvalue(v):
    if v['type'] == 'string':
        return v['value']
    elif v['type'] == 'quantity':
        return intfloat(v['value']['amount']) # * int(v['value']['unit'])
    elif v['type'] == 'time':
        return v['value']['time']
    elif v['type'] == 'wikibase-entityid':
        return v['value']['id']
    else:
        return v

def snakvalue(snak):
    t = snak.get('snaktype', None)
    if t == 'value':
        return wdvalue(snak['datavalue'])
#    elif t == 'novalue':
#        return None
#    elif t == 'somevalue':
#        return prop(snak['property'])
#    else:
#        return snak


properties = {}
def prop(p):
    return p+' '+properties.get(p, p)

def propkeyval(propid, q):
    k = prop(propid)
    if k.endswith(' ID'):
        return None, None

    v = snakvalue(q)
    if v is None:
        return None, None

    if propid in ('P585 P580 P582 P577 P7588 P8555 P8554 P1326 P1319 P576 P7124 P7125 P6949 P569 P9905 P570 P2960 P5017'.split()):  # time/date
        assert 'T' in v, (k, v)
        v, tm = v.split('T')
        assert tm == '00:00:00Z'
        if v.endswith('-00-00'):
            v = v[:-6]
        return 'date', v
    return k, v


def getquals(d):
    r = {}
    for qs in d.values():
        for q in qs:
            k, v = propkeyval(q['property'], q)
            if not k:
                continue

            if k[0] != 'P':  # known property
                r[k] = v
#            else:
#                if 'qualifiers' not in r:
#                    r['qualifiers'] = {}
#                r['qualifiers'][k] = v

    return r

def main():
    properties.update({
        row.wd_propid:row.label
            for row in parse_jsonl(open('wd_properties.jsonl'))
    })

    entities= {}
    x = ''
    for row in parse_jsonl(fileinput.input()):
        try:
            d = {
                'wd_id': row.id,
                'label': getitemdeep(row, 'labels.en.value', None),
                'description': getitemdeep(row, 'descriptions.en.value', None),
                'aliases:As': [r['value'] for r in getitemdeep(row, 'aliases.en', []) or []] or None,
            }
            x = d
            entities[row.id] = d['label']

            output1('wikidata', 'entities', d)

            for propid, values in row.get('claims', {}).items():
                for c in values:
                    if c['rank'] == 'deprecated':
                        continue
                    k, v = propkeyval(q['property'], q)
                    if not k:
                        continue
                    x = {
                        'entity_wdid': row.id,
                        'entity': entities.get(row.id, row.id),
                        'property': k,
                        'value': v,
                    }
                    x.update(getquals(c.get('qualifiers', {})))
                    output1('wikidata', 'claims', x)
        except Exception:
            raise Exception(x)


main()
