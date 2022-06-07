import sys
import re

from utils import output_parquet, output_duckdb, JsonLines, require_file, unzip

output_table = output_duckdb


def main():
    data = unzip(require_file('https://files.grouplens.org/datasets/tag-genome-2021/genome_2021.zip'))

    def lens_raw(rawtblname):
        return JsonLines(data.open(f'movie_dataset_public_final/raw/{rawtblname}.json'))

    movie_ids = {}  # movielens.item_id -> imdb_id
    movies = []
    for d in lens_raw('metadata'):
        r = dict(
            imdb_id = d['imdbId'],
            title = d['title'].replace('\u00a0', ' '),
            year = None,
            directed_by = re.split(r',(?!\s?Jr.,)\s*', d['directedBy']),
            starring = re.split(r',(?!\s?Jr.,)\s*', d['starring']),
            avg_rating = d['avgRating'],
        )

        m = re.match(r'(.*)\((\d+)\)\s*$', r['title'])
        if m:
            r['title'], r['year'] = m.groups()

        movies.append(r)

        movie_ids[d['item_id']] = r['imdb_id']

    output_table('movielens', 'movies', movies)

    tags = {d['id']: d['tag'] for d in lens_raw('tags')}

    def movie_id(item_id):
        return movie_ids.get(item_id, 'LENS'+str(item_id))

    output_table('movielens', 'ratings', [
        dict(imdb_id=movie_id(d['item_id']),
             rating=int(d['rating']*2))
        for d in lens_raw('ratings')
    ])

    output_table('movielens', 'tags', [
        dict(imdb_id=movie_id(d['item_id']),
             user_id=d['user_id'],
             tag=tags[d['tag_id']],
             score=d['score'])
        for d in lens_raw('survey_answers')
    ])

    output_table('movielens', 'reviews', [
        dict(imdb_id=movie_id(d['item_id']),
             review_text=d.get('txt', ''))
        for d in lens_raw('ratings')
    ])


main()
