# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '2.1'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from situation.tweepy.models import Status, User, DirectMessage, Friendship, SavedSearch, SearchResults, ModelFactory, Category
from situation.tweepy.error import TweepError
from situation.tweepy.api import API
from situation.tweepy.cache import Cache, MemoryCache, FileCache
from situation.tweepy.auth import OAuthHandler
from situation.tweepy.streaming import Stream, StreamListener
from situation.tweepy.cursor import Cursor

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):

    import httplib
    httplib.HTTPConnection.debuglevel = level

