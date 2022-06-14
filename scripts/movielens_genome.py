#!/usr/bin/env python

import sys
import re

from dxd.utils import jsonl, download, unzip, output

def split_names(s):
    if not s:
        return []
    return re.split(r',(?!\s?Jr.,)\s*', s)


def main():
    data = unzip(download('https://files.grouplens.org/datasets/tag-genome-2021/genome_2021.zip'))

    def lens_raw(rawtblname):
        return jsonl(data.open(f'movie_dataset_public_final/raw/{rawtblname}.json'))

    movie_ids = {}  # movielens.item_id -> imdb_id
    def parse_movie(d):
        imdb_id = d['imdbId']
        title = d['title'].replace('\u00a0', ' ')
        year = None
        directed_by = split_names(d['directedBy'])
        starring = split_names(d['starring'])
        avg_rating = d['avgRating']

        m = re.match(r'(.*?)\s*\((\d+)\)\s*$', title)
        if m:
            title, year = m.groups()

        movie_ids[d['item_id']] = d['imdbId']
        return (imdb_id, title, year, directed_by, starring, avg_rating)


    output('movielens', 'movies', 'imdb_id title year directed_by:As starring:As avg_rating:f',
            (parse_movie(d) for d in lens_raw('metadata')))

    tags = {d['id']: d['tag'] for d in lens_raw('tags')}

    def movie_id(item_id):
        return movie_ids.get(item_id, 'LENS'+str(item_id))

    output('movielens', 'ratings', 'imdb_db rating:b',
            ((movie_id(d.item_id), int(d.rating*2))
                for d in lens_raw('ratings')))

    output('movielens', 'tags', 'imdb_id user_id:i tag score:f',
            ((movie_id(d.item_id), d.user_id, tags[d.tag_id], d.score)
                for d in lens_raw('survey_answers')))

#    output('movielens', 'reviews', [
#        dict(imdb_id=movie_id(d['item_id']),
#             review_text=d.get('txt', ''))
#        for d in lens_raw('ratings')
#    ])


main()
