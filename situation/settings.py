from __future__ import unicode_literals


# Notice:
# Following Twitter API keys are for testing or development only
# (not the ones of real balanced status twitter account)
# If you are running this in production environment, you can
# generate these for your app at https://dev.twitter.com/apps/new
TWITTER = {
    'AUTH': {
        'consumer_key': 'rym1JOQ7Z8s6uRLAMDBQQ',
        'consumer_secret': 'NRtIvPoW9c5rJQAnEpJ3WIUWGZGxGZlcUP0eeCbX5s',
        'token': '584021415-rw1qpbslAtP7gDM6M8V0FaYnozDdlnH5XQakQetZ',
        'token_secret': '7kUDLx4VcXecqZsfVGmbTcqd7kd5fSNNyJFxvrlszGg',
    },
}


# We're pulling data from graphite to calculate the uptime. Each service has a
# list of counters that it uses to help calculate the % of successful / failed
# requests.
UPTIME = {
    'root_uri': 'http://graphite.balancedpayments.com/render/?',
    'username': 'USERNAME',
    'password': 'PASSWORD',
    'services': {
        'DASH': {
            'OK_TARGETS': [
                'stats_counts.status.dashboard.2xx',
                'stats_counts.status.dashboard.3xx',
                'stats_counts.status.dashboard.4xx',
            ],
            'ERROR_TARGETS': [
                'stats_counts.status.dashboard.5xx',
                'stats_counts.status.dashboard.timeout',
            ]
        },
        'JS': {
            'OK_TARGETS': [
                'stats_counts.status.balanced-js.2xx',
                'stats_counts.status.balanced-js.3xx',
                'stats_counts.status.balanced-js.4xx',
            ],
            'ERROR_TARGETS': [
                'stats_counts.status.balanced-js.5xx',
                'stats_counts.status.balanced-js.timeout',
            ]
        },
        'API': {
            'OK_TARGETS': [
                'stats_counts.status.balanced-api.2xx',
                'stats_counts.status.balanced-api.3xx',
                'stats_counts.status.balanced-api.4xx',
            ],
            'ERROR_TARGETS': [
                'stats_counts.status.balanced-api.5xx',
                'stats_counts.status.balanced-api.timeout',
            ]
        },
    }
}


# We're using a basic username and password to keep the boogie man out
HTTP_AUTH = ('username', 'password')


DEBUG = True
