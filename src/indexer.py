from myapp import db
from models import Url
from models import Word
from models import Info


class Indexer(object):
    def __init__(self, url=None, words=None):
        """
        words = dict, where key - word, value - count (words in url)
        """
        self.url = self._get_or_create_url(url)
        self.words = words
        if url is None or words is None:
            raise ValueError('url or words is None :(')

    def _get_or_create_url(self, url):
        url_query = Url.query.filter(Url.url==url)
        if url_query.count() == 0:
            url = Url(url)
            db.session.add(url)
            db.session.commit()
        else:
            url = url_query[0]
        return url

    def _get_or_create_word(self, word):
        word_query = Word.query.filter(Word.word==word)
        if word_query.count() == 0:
            word = Word(word)
            db.session.add(word)
            db.session.commit()
        else:
            word = word_query[0]
        return word

    def _update_or_create_info(self, word, count):
        info_query = Info.query.filter(Info.url==self.url, Info.word==word)
        if info_query.count() == 0:
            info = Info(self.url, word, count)
            db.session.add(info)
        else:
            info = info_query[0]
            info.count = count
        db.session.commit()
        return info

    def save(self):
        for word, count in self.words.items():
            self._update_or_create_info(self._get_or_create_word(word), count)
            # url.words.append(self._get_or_create_word(word))
