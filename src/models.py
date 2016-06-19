from myapp import db


class Url(db.Model):
    __tablename__ = 'url'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000))

#    words = db.relationship('Word', secondary=Info,
#        backref=db.backref('words', lazy='dynamic'))

    def __init__(self, url):
        self.url = url

    def __unicode__(self):
        return unicode(self.url) + u'(' + unicode(self.id) + u')'


class Word(db.Model):
    __tablename__ = 'word'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100))

#    urls = db.relationship('Url', secondary=Info,
#        backref=db.backref('urls', lazy='dynamic'))

    def __init__(self, word):
        self.word = word

    def __unicode__(self):
        return unicode(self.word) + u'(' + unicode(self.id) + u')'


class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    count = db.Column(db.Float)

    url = db.relationship(Url, backref='infos')
    word = db.relationship(Word, backref='infos')

    def __init__(self, url=None, word=None, count=1):
        if url is not None:
            self.url = url
        if word is not None:
            self.word = word
        self.count = count

    def __unicode__(self):
        return unicode(self.id)


from sqlalchemy.ext.associationproxy import association_proxy
Word.urls = association_proxy('infos', 'word')
Url.words = association_proxy('infos', 'url')
