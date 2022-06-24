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

def wdvalue(x):
    t = x['type']
    v = x['value']
    if t == 'quantity':
        return {'amount:f':float(v['amount']), 'unit':v['unit']}
    elif t == 'time':
        v, tm = v['time'].split('T')
#        assert tm == '00:00:00Z'
        if v.endswith('-00-00'):
            v = v[:-6]
        if v.startswith('+'):
            v = v[1:]
        return dict(date=v)
    elif t == 'wikibase-entityid':
        return dict(entityid=v['id'])
    elif t == 'globecoordinate':
        return {'lat:f':v['latitude'], 'long:f':v['longitude']}
    elif t == 'string':
        pass
    elif 'text' in v:
        # should also base on property id
        lang = v.get('language').split('-')[0]
        if lang != 'en':
            return {}
        return {'text_'+lang: v['text']}
    return {t:v}


properties = {}
def prop(p):
    return p+' '+properties.get(p, p)

known_props = 'P585 P580 P582 P577 P7588 P8555 P8554 P1326 P1319 P576 P7124 P7125 P6949 P569 P9905 P570 P2960 P5017'.split() # time/dates

def propkeyval(propid, snak):
    k = prop(propid)
    if k.endswith(' ID'):
        return

    d = {}
    t = snak.get('snaktype', None)
    if t == 'wikibase-entityid':
        yield ('entityid', 'entityid', v['value']['id'])

    if t == 'value':
        d = wdvalue(snak['datavalue'])
#        t = snak['datavalue']['type']
#        if t == 'wikibase-entityid':
#            t = 'entityid'

    for k1, v in d.items():
        if not k1 or not v:
            continue

        yield k, k1, v


def getquals(d):
    r = {}
    for qs in d.values():
        for q in qs:
            for k, t, v in propkeyval(q['property'], q):
                if k not in r:  # take first qual of that type only
                    r['q_'+t] = v

    return r

claimfields='''
entityid
entity
property
v_string
v_text_en
v_date
v_amount:f
v_unit
v_entityid
v_lat:f
v_long:f
q_string
q_text_en
q_date
q_amount:f
q_unit
q_entityid
q_lat:f
q_long:f
'''.split()

def main():
    properties.update({
        row.wd_propid:row.label
            for row in parse_jsonl(open('wd_properties.jsonl'))
    })

    entities= {}
    x = ''
    for row in parse_jsonl(fileinput.input()):
        try:
            label = getitemdeep(row, 'labels.en.value', None)
            if not label:  # no english label
                continue
            d = {
                'wd_id': row.id,
                'label': label,
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
                    q = c['mainsnak']
                    x = dict((k, None) for k in claimfields)
                    x.update({
                        'entityid': row.id,
                        'entity': entities.get(row.id, row.id),
#                        'property': k,
                    })
                    for k, t, v in propkeyval(q['property'], q):
                        x['property'] = k
                        assert f'v_{t}' in x, (f'v_{t}', t, v, q)
                        x[f'v_{t}'] = v

                    if x['property'] is None:
                        continue

                    for k, v in getquals(c.get('qualifiers', {})).items():
                        assert k in x, k
                        x[k] = v

                    output1('wikidata', 'claims', x)
        except Exception:
            raise Exception(x)


main()
