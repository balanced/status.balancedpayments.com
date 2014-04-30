#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import base64
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import os
import time

import webapp2
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from twilio.rest import TwilioException

import encoding
import json
import settings
import tweeter
import models
import mailer
import sms
import subscription
from uptime import graphite
from uptime import librato


LOGGER = logging.getLogger(__name__)


def cache(method, seconds=60 * 60 * 24):
    """ A basic caching wrapper that will generate a key based off of the URL
    of the request """
    #@functools.wraps
    def wrapped(handler, *a, **kw):
        key = (handler.request.path.replace('/', '') +
               handler.request.query_string)

        # This is absolutely required, to normalize memcached keys
        # from /twitter/post and /uptime/post
        if "post" in key:
            key = key.replace("post", '')

        data = memcache.get(key)
        if not data:
            LOGGER.info('CACHE miss')
            data = method(handler, *a, **kw)
            if not memcache.add(key=key, value=data, time=seconds):
                LOGGER.error('Failed to set cache ' + key)
        return data
    return wrapped


class TwitterBaseController(webapp2.RequestHandler):

    def __init__(self, *a, **kw):
        super(TwitterBaseController, self).__init__(*a, **kw)
        self.tweet_manager = tweeter.TwitterStatusProcessor(
            **settings.TWITTER['AUTH']
        )


class TwitterHandler(TwitterBaseController):

    def get(self, service=None, **_):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(self._get(service))

    @cache
    def _get(self, service):
        tweets = []
        services = [service] if service else tweeter.SERVICES
        for service in services:
            tweets += self.tweet_manager.get(service)

        return encoding.to_json({
            'messages': [encoding.to_dict(m) for m in tweets]
        })

    def post(self):
        self.tweet_manager.run()

        keys = [
            'twitter',
            'twittermessages',
            'twittermessageslatest',
        ]

        for key in keys:
            memcache.delete(key)

        # Send notifications on tweet
        for service in tweeter.SERVICES:
            latest_tweet = self.tweet_manager.get_last_message(service)

            # Notified must be set, False, and created within the last 10
            # minutes
            if (latest_tweet and hasattr(latest_tweet, 'notified') and
               not latest_tweet.notified
               and latest_tweet.created_at > datetime.utcnow() - timedelta(minutes=10)):

                self.tweet_manager._set_notified(latest_tweet.tweet_id)

                subscription.send_emails(service=service,
                                         request_url=self.request.url,
                                         current_state=latest_tweet.status,
                                         twitter_tweet=latest_tweet.message)

                subscription.send_smses(service=service,
                                        current_state=latest_tweet.status,
                                        twitter_tweet=latest_tweet.message)

        self.get()


class TwitterPostHandler(webapp2.RequestHandler):

    def get(self):
        th = TwitterHandler(self.request, self.response)
        th.post()


class TwitterMessageHandler(TwitterBaseController):

    def get(self, *a, **kw):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(self._get())

    @cache
    def _get(self):
        offset = int(self.request.get('offset', 0))
        max_date = datetime.utcnow() - timedelta(days=offset)
        min_date = max_date - timedelta(days=30)
        messages = defaultdict(list)   # messages by service
        messages['min'] = time.mktime(min_date.timetuple())
        messages['max'] = time.mktime(max_date.timetuple())

        for service in tweeter.SERVICES:
            tweets = self.tweet_manager.get_by_dates(
                service,
                max_date=max_date,
                min_date=min_date,
            )
            tweets = [t for t in tweets]
            messages[service] = [encoding.to_dict(m)
                                 for m in reversed(tweets)]

        return encoding.to_json({
            'messages': messages,
        })


class TwitterLatestMessageHandler(TwitterBaseController):

    """
    Mounted at /twitter/messages/latest
    GET returns a dictionary of messages by service
    {
        'DASH': message1,
        'API': message1,
        'JS': message1,
    }
    """

    def get(self, *a, **kw):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(self._get())

    @cache
    def _get(self):
        messages = {}   # messages by date + service

        for service in tweeter.SERVICES:
            tweet = self.tweet_manager.get_last_message(service)
            if tweet:
                if tweet.created_at < datetime.utcnow() - timedelta(days=1):
                    tweet = None
            messages[service] = encoding.to_dict(
                tweet,
            ) if tweet else None

        return encoding.to_json({
            'messages': messages,
        })


class UptimeHandler(TwitterBaseController):

    """
    Mounted at /uptime
    GET returns a dictionary of uptime for the various services
    POST deletes cached results, the subsequent GET will re-populate the cache
    """

    def __init__(self, request, response):
        super(UptimeHandler, self).__init__(request, response)
        self.uptime_managers = [
            graphite.Calculator(**settings.UPTIME),
            librato.Calculator(**settings.LIBRATO_UPTIME)
        ]

    def get(self, *a, **kw):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(self._get())

    @cache
    def _get(self):
        uptimes = []
        for manager in self.uptime_managers:
            uptimes.extend(manager.refresh())
        raw = {
            'uptime': dict(uptimes)
        }

        for service in tweeter.SERVICES:
            # if a service is UP and a tweet says it's down, then the down
            # takes precedence
            _s = raw['uptime'][service]

            if _s['status'] == 'UP':
                tweet_state = self.tweet_manager.get_latest_state(
                    service
                )

                _s['status'] = tweet_state or _s['status']

            subscription.should_notify(service, _s['status'], self.request.url)

        return encoding.to_json(raw)

    def post(self):
        memcache.delete('uptime')
        self.get()


class UptimePostHandler(webapp2.RequestHandler):

    def get(self):
        uh = UptimeHandler(self.request, self.response)
        uh.post()


class MainHandler(webapp2.RequestHandler):

    """
    Serves the index.html, that's it.
    """

    def get(self, *a, **kw):
        path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'index.html')
        self.response.out.write(template.render(path, {}))


class SubscribeEmailHandler(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'application/json'

        email = self.request.get('email')
        services = self.request.get('services').rstrip(',')

        query = db.GqlQuery(
            "SELECT * FROM EmailSubscriber WHERE email = :1",
            email)

        number_rows = query.count()

        if number_rows > 0:
            self.response.status = 409
            self.response.out.write(json.dumps({
                "error": email + " is already subscribed."
            }))
            return

        mail = mailer.Mail()
        mail.send(email,
                  "Successfully subscribed to Balanced " +
                  services + " incidents",
                  "You successfully subscribed to Balanced " +
                  services + " incidents.",
                  self.request.url)

        s = models.EmailSubscriber(email=email,
                                   services=services.split(','))

        s.put()

        self.response.out.write(json.dumps({
            "subscribed": "email",
            "services": services.split(',')
        }))


class SubscribeSMSHandler(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'application/json'

        phone = self.request.get('phone')
        services = self.request.get('services').rstrip(',')

        query = db.GqlQuery(
            "SELECT * FROM SMSSubscriber WHERE phone = :1",
            phone)

        number_rows = query.count()

        if number_rows > 0:
            self.response.status = 409
            self.response.out.write(json.dumps({
                "error": phone + " is already subscribed."
            }))
            return

        txt = sms.SMS()
        try:
            txt.send(phone,
                     "Successfully subscribed to Balanced "
                     + services +
                     " incidents. Reply with STOP to unsubscribe.")

        except TwilioException, e:
            LOGGER.error("Failed to send SMS via Twilio - " + e.msg)
            self.response.status = 400
            self.response.out.write(json.dumps({
                "error": e.msg
            }))
            return

        s = models.SMSSubscriber(phone=phone,
                                 services=services.split(','))

        s.put()

        self.response.out.write(json.dumps({
            "subscribed": "sms",
            "services": services.split(',')
        }))


class UnsubscribeEmailHandler(webapp2.RequestHandler):

    def get(self, base64email):
        if not base64email:
            self.redirect("/")

        email = base64.urlsafe_b64decode(base64email)

        if email:
            email_subscriber = models.EmailSubscriber.all()
            email_subscriber.filter('email =', email)

            for es in email_subscriber:
                es.delete()

        # ToDo: show a nice pretty notification that e-mail is subscribed
        self.redirect("/")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/uptime', UptimeHandler),
    ('/uptime/post', UptimePostHandler),
    ('/twitter', TwitterHandler),
    ('/twitter/post', TwitterPostHandler),
    ('/twitter/messages', TwitterMessageHandler),
    ('/twitter/messages/latest', TwitterLatestMessageHandler),
    ('/twitter/(.*)', TwitterHandler),
    ('/subscriptions/email', SubscribeEmailHandler),
    ('/subscriptions/email/(.*)', UnsubscribeEmailHandler),
    ('/subscriptions/sms', SubscribeSMSHandler)
], debug=settings.DEBUG)
