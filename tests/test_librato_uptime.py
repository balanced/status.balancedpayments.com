import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath('./situation'))
sys.path.insert(0, os.path.abspath('./'))

from situation.uptime.librato import Calculator
from google.appengine.ext import testbed
import mock


UPTIME_CFG = {
    'root_uri': 'https://metrics-api.librato.com/v1/metrics/',
    'username': 'MOCK_USERNAME',
    'password': 'MOCK_PWD',
    'services': {
        'API': {
            'SOURCE': '*bapi-live*',
            'TOTAL_TARGETS': [
                'MOCK_TOTAL_TARGET_A',
                'MOCK_TOTAL_TARGET_B',
            ],
            'ERROR_TARGETS': [
                'MOCK_ERROR_TARGET_A',
                'MOCK_ERROR_TARGET_B',
                'MOCK_ERROR_TARGET_C',
            ]
        },
    }
}


class TestLibratoUptime(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def test_service_uptime(self):
        index = [0]
        resps = [
            # TOTAL A
            dict(
                measurements=dict(
                    foobar=[dict(count=1), dict(count=7788), dict(count=123)],
                ),
                query=dict(next_time=999),
            ),
            dict(
                measurements=dict(
                    foobar=[dict(count=888)],
                ),
            ),
            # TOTAL B
            dict(
                measurements=dict(
                    foobar=[dict(count=3), dict(count=4)],
                )
            ),
            # ERROR A
            dict(
                measurements=dict(
                    foobar=[dict(count=5)],
                    barfoo=[dict(count=78)],
                )
            ),
            # ERROR B
            dict(
                measurements=dict(
                    foobar=[dict(count=6)],
                    barfoo=[dict(count=78)],
                )
            ),
            # ERROR C
            dict(
                measurements=dict(
                    foobar=[dict(count=0)],
                )
            ),
        ]

        def read():
            result = resps[index[0]]
            index[0] += 1
            return json.dumps(result)

        calculator = Calculator(**UPTIME_CFG)
        calculator.opener = mock.Mock()
        calculator.opener.open.return_value = mock.Mock()
        calculator.opener.open.return_value.read.side_effect = read

        result = calculator._for_service(calculator.services['API'], 5)
        total_number = (
            (1 + 7788 + 123) +
            (888) +
            (3 + 4)
        )
        error_number = (
            (5 + 78) +
            (6 + 78) +
            (0)
        )
        expected_result = ((total_number - float(error_number)) / total_number) * 100
        self.assertEqual(result, expected_result)
