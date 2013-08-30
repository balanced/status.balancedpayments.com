from __future__ import unicode_literals

from google.appengine.ext import db

class Tweet(db.Model):
    created_at = db.DateTimeProperty()
    message = db.StringProperty()
    status = db.StringProperty()
    service = db.StringProperty()
    tweet_id = db.StringProperty()
    notified = db.BooleanProperty()

    @db.ComputedProperty
    def created_date(self):
        return self.created_at.date().strftime('%Y-%m-%d')

    def setNotified(self):
        self.notified = True
        self.put()


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


class EmailSubscriber(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True)
    email = db.EmailProperty(required=True)
    services = db.StringListProperty(required=True)


class SMSSubscriber(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True)
    phone = db.StringProperty(required=True)
    services = db.StringListProperty(required=True)


class ServiceStatus(db.Model):
    service = db.StringProperty(required=True,
                                choices=('API', 'DASHBOARD', 'JS'))

    current = db.StringProperty(required=True,
                                choices=('UP', 'ISSUE', 'DOWN'))

    down_count = db.IntegerProperty(required=True,
                                    default=0)

    UP = "UP"
    DOWN = "DOWN"
    ISSUE = "ISSUE"
    NOTIFY_DOWN = "NOTIFY_DOWN"
    NOTIFY_UP = "NOTIFY_UP"

    def _on_down(self):
        self.down_count += 1
        self.put()
        if self.down_count == 1:
            return self.NOTIFY_DOWN

        return None

    def _on_up(self):
        if self.down_count > 0:
            self.down_count = 0
            self.put()
            return self.NOTIFY_UP

        return None

    _dfa = {
        UP: {
            ISSUE: None,
            DOWN: _on_down,
            UP: None
        },
        ISSUE: {
            UP: _on_up,
            DOWN: _on_down,
            ISSUE: None
        },
        DOWN: {
            UP: _on_up,
            ISSUE: None,
            DOWN: None,
        }
    }

    def change(self, new_state):
        action = self._dfa[self.current][new_state]

        self.current = new_state
        self.put()

        if action is not None:
            return action(self)
