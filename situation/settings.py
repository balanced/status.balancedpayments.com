# Notice:
# If you are running this in production environment, generate
# these for your app at https://dev.twitter.com/apps/new
TWITTER = {
    'AUTH': {
        'consumer_key': 'XXXX',
        'consumer_secret': 'XXXX',
        'token': 'XXXX',
        'token_secret': 'XXXX',
     }
}


# We're pulling data from graphite to calculate the uptime. Each service has a
# list of counters that it uses to help calculate the % of successful / failed
# requests.
UPTIME = {
    'root_uri': 'http://graphite.balancedpayments.com/render/?',
    'username': 'username',
    'password': 'password',
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
        }
    }
}

# The e-mail address to send notifications from
EMAIL = {
    'sender': 'Balanced Status <noreply@balancedpayments.com>'
}

LIBRATO_UPTIME = {
    'root_uri': 'https://metrics-api.librato.com/v1/metrics/',
    'username': 'vendors@balancedpayments.com',
    'password': '14d624cde57cfba7cfa76baf0284d94c33de7f289db5ee4172f20c117234afff',
    'password': 'FIXME',
    'services': {
        'API': {
            'SOURCE': '*bapi-live*',
            'TOTAL_TARGETS': [
                'AWS.ELB.RequestCount',
            ],
            'ERROR_TARGETS': [
                'AWS.ELB.HTTPCode_Backend_5XX',
                'AWS.ELB.HTTPCode_ELB_5XX',
            ]
        },
    }
}

# TWILIO API credentials
TWILIO = {
    'account_sid': 'XXXX',
    'auth_token': 'XXXX',
    'from_number': 'XXXX'
}

DEBUG = True

# Currently DASHBOARD does not send out notifications
NOTIFY_SERVICES = ['API', 'JS']
