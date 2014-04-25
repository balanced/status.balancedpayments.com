from __future__ import unicode_literals
import logging
import urllib2

import encoding


LOGGER = logging.getLogger(__name__)


def calculate_uptime(uptime):
    # also exists in status.js
    if uptime >= 99:
        return 'UP'
    if uptime >= 90:
        return 'ISSUE'
    return 'DOWN'


class Calculator(object):

    def __init__(self, root_uri, username, password, services):
        self.root_uri = root_uri
        self.services = services
        self.username = username
        self.password = password

        self._create_opener_for_uri(self.root_uri)

    def _create_opener_for_uri(self, uri):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, uri, self.username, self.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        self.opener = urllib2.build_opener(authhandler)

    def _construct_uri(self, targets, minutes_ago=5):
        return '&'.join([
            self.root_uri,
            'from=-{}minute'.format(minutes_ago),
            'until=now',
            'format=json',
        ] + [
            'target={}'.format(
                self._summarize(t, minutes_ago)) for t in targets
        ])

    def _summarize(self, target, minutes_ago):
        return 'summarize({},\'{}minute\')'.format(target, minutes_ago)

    def _calculate_data(self, stats):
        count = 0
        for item in stats:
            datapoints = item['datapoints']
            count += sum(
                count for count, _ in datapoints if count
            )
        return count

    def _for_service(self, targets, minutes_ago):
        ok_uri = self._construct_uri(targets['OK_TARGETS'], minutes_ago)
        error_uri = self._construct_uri(targets['ERROR_TARGETS'], minutes_ago)

        ok_stats = encoding.json.loads(self.opener.open(ok_uri).read())
        error_stats = encoding.json.loads(self.opener.open(error_uri).read())

        error_counts = self._calculate_data(error_stats)
        ok_counts = self._calculate_data(ok_stats)
        total_counts = ok_counts + error_counts

        if total_counts:
            percentage = (total_counts - float(error_counts)) / total_counts
        else:
            percentage = 1

        return percentage * 100

    def refresh(self):
        for service, targets in self.services.iteritems():
            # 5 minutes
            five_min_percentage = self._for_service(targets, 5)
            # 60 minutes (1 hour) * 24 (hours) * 30 (days)
            thirty_day_percentage = self._for_service(targets, 60 * 24 * 30)

            yield service, {
                'uptime': thirty_day_percentage,
                'status': calculate_uptime(five_min_percentage)
            }
