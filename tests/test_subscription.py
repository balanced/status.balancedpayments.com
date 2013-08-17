import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('./situation'))
sys.path.insert(0, os.path.abspath('./'))

from situation import subscription, models
from google.appengine.ext import testbed

class TestSubscription(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_logservice_stub()

        # Create default API ServiceStatus
        default_api = models.ServiceStatus(service='API', current='UP')
        default_api.put()

        # Create default DASHBOARD ServiceStatus
        default_dashboard = models.ServiceStatus(service='DASHBOARD', current='UP')
        default_dashboard.put()

        # Create default JS ServiceStatus
        default_js = models.ServiceStatus(service='JS', current='UP')
        default_js.put()

    def tearDown(self):
        self.testbed.deactivate()

    def _assert_expectations(self, tests):
        for index, (service, status, expected) in enumerate(tests, start=1):
            result = subscription.should_notify(service, status, None)
            self.assertEqual(result, expected,
                             'Assertion failed for case# {}'.format(index))

    def test_should_notify_api(self):
        tests = [
            ('API', 'DOWN', True),
            ('API', 'ISSUE', False),
            ('API', 'DOWN', False),
            ('API', 'ISSUE', False),
            ('API', 'UP', True),
            ('API', 'DOWN', True),
            ('API', 'UP', True),
            ('API', 'ISSUE', False),
            ('API', 'UP', False),
            ('API', 'UP', False),
            ('API', 'DOWN', True),
            ('API', 'DOWN', False),
            ('API', 'UP', True),
            ('API', 'ISSUE', False),
            ('API', 'DOWN', True)
        ]

        self._assert_expectations(tests)

    def test_should_notify_dashboard(self):
        tests = [
            ('DASHBOARD', 'DOWN', True),
            ('DASHBOARD', 'ISSUE', False),
            ('DASHBOARD', 'DOWN', False),
            ('DASHBOARD', 'ISSUE', False),
            ('DASHBOARD', 'UP', True),
            ('DASHBOARD', 'DOWN', True),
            ('DASHBOARD', 'UP', True),
            ('DASHBOARD', 'ISSUE', False),
            ('DASHBOARD', 'UP', False),
            ('DASHBOARD', 'UP', False),
            ('DASHBOARD', 'DOWN', True),
            ('DASHBOARD', 'DOWN', False),
            ('DASHBOARD', 'UP', True),
            ('DASHBOARD', 'ISSUE', False),
            ('DASHBOARD', 'DOWN', True)
        ]

        self._assert_expectations(tests)

    def test_should_notify_js(self):
        tests = [
            ('JS', 'DOWN', True),
            ('JS', 'ISSUE', False),
            ('JS', 'DOWN', False),
            ('JS', 'ISSUE', False),
            ('JS', 'UP', True),
            ('JS', 'DOWN', True),
            ('JS', 'UP', True),
            ('JS', 'ISSUE', False),
            ('JS', 'UP', False),
            ('JS', 'UP', False),
            ('JS', 'DOWN', True),
            ('JS', 'DOWN', False),
            ('JS', 'UP', True),
            ('JS', 'ISSUE', False),
            ('JS', 'DOWN', True)
        ]

        self._assert_expectations(tests)
