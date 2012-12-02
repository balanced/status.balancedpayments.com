from __future__ import unicode_literals


# Generate these for your app at https://dev.twitter.com/apps/new
TWITTER = {
    'AUTH': {
        'consumer_key': 'KEY',
        'consumer_secret': 'SECRET',
        'token': 'TOKEN',
        'token_secret': 'TOKEN_SECRET',
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
