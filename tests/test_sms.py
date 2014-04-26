import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('./situation'))
sys.path.insert(0, os.path.abspath('./'))

from situation import sms
from twilio.rest import TwilioException
from google.appengine.ext import testbed


class TestSMS(unittest.TestCase):

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

    # Assert that trying to send a SMS over 160 characters gets truncated
    # before attempting to send with Twilio
    @unittest.skip("Skipped for now (needs authentication)")
    def test_sms_max_length(self):
        response = None
        try:
            twilio = sms.SMS()
            response = twilio.send(
                '+15005550000',
                'This is a super duper long sms message that is over ' +
                'one hundred and sixty characters, but should be auto ' +
                'truncated by the SMS class before attempting to  ' +
                'send via Twilio.')
        except TwilioException:
            pass

        self.assertIsNotNone(response, 'Failed to send SMS message over 160 characters with Twilio')
