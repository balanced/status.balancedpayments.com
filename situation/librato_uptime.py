from __future__ import unicode_literals
import logging
import urllib
import urllib2
import time
import json


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
        self.opener = urllib2.build_opener(authhandler)

    def _construct_url(
        self,
        metrics,
        source,
        start_time,
        end_time,
        resolution=60,
    ):
        return '{}{}?{}'.format(
            self.root_uri,
            metrics,
            urllib.urlencode(dict(
                source=source,
                start_time=int(start_time),
                end_time=int(end_time),
                resolution=resolution,
                summarize_time=1,
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
        # we need the biggest window to move along time line for reducing
        # requests to a reasonable number. Oterwise, there is 43,200 minutes
        # in a month, if we are using 1 minutes resolution, librato's
        # request limitation is 100 data points per request, so we need
        # 43,200 / 100 which is 432 requests to get sum of all data points
        # in a month. With 3600 seconds (60 minutes or 1 hour) resolution,
        # we only need 43,200 / (60 * 100) = 7 requests. This still sucks,
        # but at least it is not a thousand requests. Oh, by the way, by
        # setting the resolution to an hour, it's not so accurate. Looks
        # like some data points are dropped
        resolution = 60
        if minutes_ago > 3600 / 60:
            resolution = 3600
        end_time = int(time.time())
        start_time = end_time - (minutes_ago * 60)
        for metrics in targets[key]:
            while True:
                url = self._construct_url(
                    metrics,
                    targets['SOURCE'],
                    start_time=start_time,
                    end_time=end_time,
                    resolution=resolution,
                )
                logger.debug('Fetching %s', url)
                response = json.loads(self.opener.open(url).read())
                count += self._calculate_data(response['measurements'])
                if response.get('query', {}).get('next_time'):
                    start_time = response['query']['next_time']
                else:
                    break
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
            ok_count, error_count, percentage * 100,
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
