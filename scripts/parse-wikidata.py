#!/usr/bin/env python3

import fileinput
import sys
import json

from readysetdata import parse_jsonl, output, debug, get_optarg, OutputTable, getitemdeep, warning


LANGS=['en']

known_props = 'P585 P580 P582 P577 P7588 P8555 P8554 P1326 P1319 P576 P7124 P7125 P6949 P569 P9905 P570 P2960 P5017'.split() # time/dates

claimfields=list('''
entityid entity property
v_string v_date v_amount:f v_unit v_entityid v_lat:f v_long:f
q_string q_date q_amount:f q_unit q_entityid q_lat:f q_long:f
'''.split())

entity_labels = {}  # "Q##" -> "label"
property_labels = {}


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
        if lang not in LANGS:
            return {}
        return {'text_'+lang: v['text']}
    return {t:v}


def prop(p):
    return p+' '+property_labels.get(p, p)

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


def get_claims(row):
    for propid, values in row.get('claims', {}).items():
        for c in values:
            if c['rank'] == 'deprecated':
                continue
            q = c['mainsnak']
            x = dict((k, None) for k in claimfields)
            x.update({
                'entityid': row.id,
                'entity': entity_labels.get(row.id, row.id),
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

            yield x


def get_entity(row):
    ret = dict(entityid=row.id)

    n = 0
    for lang in LANGS:
        label = getitemdeep(row, f'labels.{lang}.value', None)
        ret[f'label_{lang}'] = label
        if label:
            n += 1

        aliases = getitemdeep(row, f'aliases.{lang}', []) or []
        ret[f'aliases_{lang}:As'] = [r['value'] for r in aliases] or None
        ret[f'description_{lang}'] = getitemdeep(row, f'descriptions.{lang}.value', None)

    if not n:  # no labels from LANGS for entity
        return

    return ret


def main():
    global LANGS
    global claimfields
    LANGS = list(get_optarg("-l", "LANGS", 'en').split(','))

    for lang in LANGS:
        claimfields.append(f'v_text_{lang}')
        claimfields.append(f'q_text_{lang}')

    try:
        property_rows = list(parse_jsonl(open('wd_properties.jsonl')))
        property_labels.update({
            row.wd_propid:row.label
                for row in property_rows
        })

        output('wikidata', 'properties', property_rows)
    except FileNotFoundError as e:
        warning(f'{e} no wd_properties.jsonl')
        if debug:
            raise

    with OutputTable('wikidata', 'claims') as claims, \
         OutputTable('wikidata', 'entities') as entities:
        for row in parse_jsonl(fileinput.input()):
            try:
                x = None
                x = get_entity(row)
                if not x:
                    continue

                entity_labels[row.id] = x[f'label_{LANGS[0]}']

                entities.output(x)

                claims.output(*get_claims(row))

            except Exception as e:
                warning(type(e), str(e), x)
                if debug:
                    raise


main()
