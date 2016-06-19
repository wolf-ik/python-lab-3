import json

from flask import request

from myapp import app as flask_app
from logic import get_urls_for_words
from logic import get_indexed_urls
from logic import index_urls


@flask_app.route('/')
def route_base_page():
    valid_urls = (
        '/admin',
        '/urls',
        '/search?search=word1 word2',
        '/index?url=url1 url2',
    )
    return 'use:<br>' + '<br>'.join(valid_urls)


@flask_app.route('/favicon.ico')
def route_favicon():
    return 'fu!'


@flask_app.route('/search')
def route_search():
    search_words = request.args.get('search')
    if search_words is None:
        return 'Nothing'
    urls = get_urls_for_words(search_words.split())
    return json.dumps(urls)


@flask_app.route('/urls')
def route_indexed_urls():
    return json.dumps(get_indexed_urls())


@flask_app.route('/index')
def route_index():
    urls = request.args.get('url')
    if urls is None:
        return 'Can\'t index nothing :('
    index_urls(urls.split())
    return 'Ok. Your request now in the queue.<br>' + \
           '<a href="/">click me</a>'
