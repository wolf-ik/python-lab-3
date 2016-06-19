#!/usr/bin/python
# coding: utf8

import urllib2
import urlparse
from collections import defaultdict
from math import sqrt
from math import log

from bs4 import BeautifulSoup

from text_analizer import get_words_from_raw_text
from text_analizer import normalize_words
from indexer import Indexer
from myapp import db
from models import Url
from models import Word
from models import Info
from myapp import celery_app


##############################################################################
# SEARCH WORDS
##############################################################################


def get_inverse_doc_frequency(word):
    urls_count = Url.query.count()
    urls_with_word_count = Info.query.outerjoin(Word, Info.word_id==Word.id)\
        .filter(Word.word==word).count()
    if urls_with_word_count == 0:
        return 0
    return log(float(urls_count) / urls_with_word_count)


def get_urls_for_word(word):
    word = unicode(word)
    infos = Info.query.outerjoin(Word,Info.word_id==Word.id).filter(Word.word==word).all()
    idf = get_inverse_doc_frequency(word)
    res_dict = dict()
    for info in infos:
        res_dict[info.url.url] = float(info.count) * idf
    return res_dict


def get_urls_for_words(words):
    res_dict = defaultdict(float)
    for word in normalize_words(words):
        tmp_dict = get_urls_for_word(word)
        for k, v in tmp_dict.items():
            res_dict[k] += v
    return res_dict


##############################################################################
# SHOW URLS
##############################################################################


def get_indexed_urls():
    res = Url.query.all()
    res = [x.url for x in res]
    return res


##############################################################################
# INDEX URLS
##############################################################################


def normalize_dict_words(dict_words):
    div_by = 0
    for word, count in dict_words.items():
        div_by += count ** 2
    div_by = sqrt(div_by)
    res = {k: v / div_by for k, v in dict_words.items()}
    return res


def get_dict_words(words):
    res = defaultdict(int)
    for word in words:
        res[word] += 1
    return normalize_dict_words(res)


def get_netloc(url):
    o = urlparse.urlparse(url)
    netloc = o.scheme + '://' + o.netloc + '/'
    return netloc


def parse_html(url, bs):
    print 'Start parse html from url: ' + str(url)
    body = bs.find('body')
    if body is None:
        return
    raw_text = body.get_text()
    words = get_words_from_raw_text(raw_text)
    dict_words = get_dict_words(words[:100])

    # print dict_words
    print 'Start Indexing url: ' + str(url)
    indexer = Indexer(url=url, words=dict_words)
    indexer.save()


@celery_app.task()
def crawler(url=None, depth=1):
    print 'Start url:' + str(url)
    if depth < 0:
        return
    if Url.query.filter(Url.url==url).count() != 0:
        return

    u = Url(url)
    db.session.add(u)
    db.session.commit()

    try:
        html = urllib2.urlopen(url).read().decode('utf8')
    except (ValueError, urllib2.HTTPError, UnicodeError):
        print 'ERROR: Can\'t get html from url'
        return

    print 'Parse links'
    bs = BeautifulSoup(html, 'html.parser')
    netloc = get_netloc(url)

    for link in bs.find_all('a', href=True):
        new_url = link['href']
        if not new_url.startswith('http'):
            new_url = urlparse.urljoin(url, new_url)
        if new_url.startswith(netloc):
            crawler.delay(new_url, depth=depth-1)

    parse_html(url, bs)


def index_urls(urls):
    for url in urls:
        crawler.delay(url)
