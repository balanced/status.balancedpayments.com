from __future__ import unicode_literals

from google.appengine.ext import db


class Tweet(db.Model):
    created_at = db.DateTimeProperty()
    message = db.StringProperty()
    status = db.StringProperty()
    service = db.StringProperty()
    tweet_id = db.StringProperty()

    @db.ComputedProperty
    def created_date(self):
        return self.created_at.date().strftime('%Y-%m-%d')


class Uptime(db.Model):
    start = db.DateTimeProperty()
    end = db.DateTimeProperty()
    data = db.StringProperty(multiline=True)

    @classmethod
    def get_by_dates(cls, start, end):
        result = cls.all().filter(
            'start = ', start
        ).filter(
            'end = ', end
        ).fetch(1)
        if result:
            return result
        return None

    @classmethod
    def latest(cls):
        result = cls.all().order('-end').fetch(1)
        if result:
            return result[0].end
        return None

    @classmethod
    def latest(cls):
        result = cls.all().order('-end').fetch(1)
        if result:
            return result[0].end
        return None


def kv_key(key=None):
    return db.Key.from_path('KV', key)


class KV(db.Model):
    k = db.StringProperty()
    value = db.StringProperty()

    @classmethod
    def generate_key(cls, key):
        return kv_key(key)

    @classmethod
    def get(cls, key):
        return db.get(cls.generate_key(key))
