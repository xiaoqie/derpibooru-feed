"""
Generate atom feed for derpibooru.abs

Usage:
import derpibooru_feed.py

derpibooru_feed.get_atom('safe', min_votes=100)
"""
from feedgen.feed import FeedGenerator
import urllib.request
import json
from aiohttp import web
import time
import datetime

cached = {}


def generate(query, min_votes):
    with urllib.request.urlopen("https://derpibooru.org/search.json?q=upvotes.gte:%d,%s" % (min_votes, query)) as conn:
        content = conn.read().decode("utf-8")
        result = json.loads(content)

    fg = FeedGenerator()
    fg.id('https://derpibooru.org/search?q=upvotes.gte:%d,%s' % (min_votes, query))
    fg.title('Derpibooru (%s with at least %d upvotes)' % (query.replace('+', ' '), min_votes))
    fg.link(href='https://derpibooru.org/', rel='alternate')
    fg.logo('https://derpibooru.org/favicon.ico')
    fg.language('en')

    for image in result['search']:
        fe = fg.add_entry()
        fe.link(href='https://derpibooru.org/%d' %
                image['id'], rel='alternate')
        fe.guid('https://derpibooru.org/%d' % image['id'])
        fe.pubdate(datetime.datetime.fromtimestamp(time.mktime(time.strptime(
            image['created_at'].split('.')[0], "%Y-%m-%dT%H:%M:%S")), tz=datetime.timezone.utc))
        fe.content('''<img alt="test_pic" src="https:%s" /> Upvotes: %d <br/>
            %s''' % (image['representations']['thumb'], image['upvotes'], image['description'].replace('[bq]', '<bq>').replace('[/bq]', '</bq>').replace('\n', '<br/>\n')), type='CDATA')
        artists = [tag[0:len('artists:')] for tag in image['tags'].split(
            ', ') if tag.startswith('artists:')]
        fe.author({'name': artist for artist in artists})
        fe.title(image['tags'])

    atomfeed = fg.atom_str(pretty=True)
    return atomfeed


def get_atom(query, min_votes):
    """Get Atom XML.
    
    Arguments:
        query {str} -- Search for tags, tags are splited by ',' without extra spaces. Spaces in tags are replaced with '+'.
        min_votes {int} -- minimum upvotes.
    
    Returns:
        str -- string contains Atom XML
    """
    key = "%s, %s" % (query, min_votes)
    if key in cached and (time.time() - cached[key]['time']) < 10 * 60:
        print('returned cache')
        return cached[key]['ret']

    print('generated new feed')
    ret = generate(query, min_votes).decode()
    cached[key] = {'time': time.time(), 'ret': ret}
    return ret


if __name__ == '__main__':
    (get_atom('safe', 100))
    (get_atom('safe', 100))
    time.sleep(11)
    (get_atom('safe', 100))
    (get_atom('safe', 100))
