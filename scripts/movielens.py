#!/usr/bin/env python3

import sys
import re

from readysetdata import parse_jsonl, download, unzip_url, output

URL='https://files.grouplens.org/datasets/tag-genome-2021/genome_2021.zip'

def split_names(s):
    if not s:
        return []
    return re.split(r',(?!\s?Jr.,)\s*', s)


data = unzip_url(URL)

def lens_raw(rawtblname):
    return parse_jsonl(data.open_text(f'*{rawtblname}.json'))

movie_ids = {}  # movielens.item_id -> imdb_id

def parse_movie(d):
    r = {
        'imdb_id': d['imdbId'],
        'title': d['title'].replace('\u00a0', ' '),
        'year': None,
        'directed_by:As': split_names(d['directedBy']),
        'starring:As': split_names(d['starring']),
        'avg_rating:f': d['avgRating']
    }

    m = re.match(r'(.*?)\s*\((\d+)\)\s*$', r['title'])
    if m:
        r['title'], r['year'] = m.groups()

    movie_ids[d['item_id']] = r['imdb_id']
    return r


output('movielens', 'movies', (parse_movie(d) for d in lens_raw('metadata')))

tags = {d['id']: d['tag'] for d in lens_raw('tags')}

def movie_id(item_id):
    return movie_ids.get(item_id, 'LENS'+str(item_id))

output('movielens', 'ratings', ({
            'imdb_id': movie_id(d.item_id),
            'rating:b': int(d.rating*2)
         } for d in lens_raw('ratings')))

output('movielens', 'tags', ({
            'imdb_id': movie_id(d.item_id),
            'user_id:i': d.user_id,
            'tag': tags[d.tag_id],
            'score:f': d.score
        } for d in lens_raw('survey_answers')))

# output('movielens', 'reviews', (dict(imdb_id=movie_id(d['item_id']), review_text=d.get('txt', '')) for d in lens_raw('ratings')))
