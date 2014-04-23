from __future__ import unicode_literals
import logging
import urllib
import urllib2

import encoding


logger = logging.getLogger(__name__)


def determine_status(uptime):
    """Determine status of service by given uptime and return

    """
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
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)

    def _construct_uri(self, metrics, source, minutes_ago=5):
        return '{}{}?{}'.format(
            self.root_uri,
            metrics,
            urllib.urlencode(dict(
                source=source,
                count=minutes_ago,
                resolution=60,
            ))
        )

    def _calculate_data(self, stats):
        count = 0
        for _, values in stats.iteritems():
            for item in values:
                count += item['count']
        return count

    def _get_targets_sum(self, key, targets, minutes_ago):
        """Get all count sum in given targets during minutes ago to now period
        and return

        """
        count = 0
        for metrics in targets[key]:
            url = self._construct_uri(metrics, targets['SOURCE'], minutes_ago)
            response = encoding.json.loads(urllib2.urlopen(url).read())
            count += self._calculate_data(response['measurements'])
        return count

    def _for_service(self, targets, minutes_ago):
        ok_count = self._get_targets_sum('OK_TARGETS', targets, minutes_ago)
        error_count = self._get_targets_sum('ERROR_TARGETS', targets, minutes_ago)
        total_count = ok_count + error_count

        if total_count:
            percentage = (total_count - float(error_count)) / total_count
        else:
            percentage = 1

        logger.info(
            'OK=%s, ERROR=%s, PERCENTAGE=%s',
            ok_count, error_count, percentage,
        )

        return percentage * 100

    def refresh(self):
        for service, targets in self.services.iteritems():
            # 5 minutes
            five_min_percentage = self._for_service(targets, 5)
            # 60 minutes (1 hour) * 24 (hours) * 30 (days)
            thirty_day_percentage = self._for_service(targets, 60 * 24 * 30)
            status = determine_status(five_min_percentage)

            logger.info(
                'Service %s, 30 days percentage: %s, status: %s',
                service, thirty_day_percentage, status,
            )
            yield service, {
                'uptime': thirty_day_percentage,
                'status': status,
            }
