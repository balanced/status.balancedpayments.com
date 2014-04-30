import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('./situation'))
sys.path.insert(0, os.path.abspath('./'))

from situation import settings, tweeter
from situation.tweepy import TweepError
from google.appengine.ext import testbed
from . import skip_auth


class TestTwitter(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_logservice_stub()

    def tearDown(self):
        self.testbed.deactivate()

    # Assert that fetching timeline tweets from twitter does not throw an exception
    @skip_auth()
    def test_get_tweets(self):
        t = tweeter.TwitterStatusProcessor(**settings.TWITTER['AUTH'])

        tweets = []
        try:
            tweets = t._get_tweets(None)
        except TweepError:
            pass

        self.assertGreater(len(tweets), 0, 'Failed to fetch timeline tweets from twitter')
