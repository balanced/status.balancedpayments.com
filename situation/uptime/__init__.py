from __future__ import unicode_literals


def determine_status(uptime):
    """Determine status of service by given uptime and return

    """
    # also exists in status.js
    if uptime >= 99:
        return 'UP'
    if uptime >= 90:
        return 'ISSUE'
    return 'DOWN'
