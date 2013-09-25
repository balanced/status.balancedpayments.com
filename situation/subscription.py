import models
import settings
import logging
import mailer
import sms
from twilio.rest import TwilioException

LOGGER = logging.getLogger(__name__)


def should_notify(service, current_state, request_url):
     # This is filthy. Don't judge me bro
    if service == "DASH":
        service = "DASHBOARD"

    svc_status = models.ServiceStatus.all()
    svc_status.filter('service =', service)

    # No status object stored. Create it, and return
    if svc_status.count() == 0:
        ss = models.ServiceStatus(service=service, current=current_state)
        ss.put()
        return

    # Will always just run just once
    for ss in svc_status:
        result = ss.change(current_state)

        if result == "NOTIFY_UP" or result == "NOTIFY_DOWN":
            if settings.DEBUG:
                LOGGER.info("SERVICE [" + service + "] IS " + current_state)

            send_emails(service, request_url, current_state)
            send_smses(service, current_state)
            return True

    return False


def send_emails(service, request_url, current_state=None, twitter_tweet=None):
    # This is filthy. Don't judge me bro
    if service == "DASH":
        service = "DASHBOARD"

    email_subscribers = models.EmailSubscriber.gql("WHERE services IN (:1)", service)

    if settings.DEBUG:
        LOGGER.info(
            "SENDING NOTIFICATION TO [" + str(email_subscribers.count()) + "] EMAIL SUBSCRIBERS"
        )

    if service in settings.NOTIFY_SERVICES:
        mail = mailer.Mail()
        for email_subscriber in email_subscribers:
            # Tweet
            if(twitter_tweet):
                twitter_tweet = twitter_tweet.strip()

                mail.send(
                    email_subscriber.email,
                    "Tweet from @balancedstatus",
                    "{}".format(twitter_tweet) +
                    "\n\nThis is an automated notification from https://status.balancedpayments.com",
                    request_url)
            # UP/DOWN
            else:
                mail.send(
                    email_subscriber.email,
                    "Balanced {} is {}".format(
                        service, current_state),
                    "Balanced {} is {}.".format(service, current_state) +
                    "\n\nThis is an automated notification from https://status.balancedpayments.com",
                    request_url)


def send_smses(service, current_state=None, twitter_tweet=None):
    # This is filthy. Don't judge me bro
    if service == "DASH":
        service = "DASHBOARD"

    sms_subscribers = models.SMSSubscriber.gql("WHERE services IN (:1)", service)

    if settings.DEBUG:
        LOGGER.info(
            "SENDING NOTIFICATION TO [" + str(sms_subscribers.count()) + "] SMS SUBSCRIBERS"
        )

    if service in settings.NOTIFY_SERVICES:
        txt = sms.SMS()
        for sms_subscriber in sms_subscribers:
            try:
                # Tweet
                if(twitter_tweet):
                    twitter_tweet = twitter_tweet.strip()

                    txt.send(
                        sms_subscriber.phone,
                        "@balancedstatus: {} - {}".format(
                            service, twitter_tweet))
                # UP/DOWN
                else:
                    txt.send(
                        sms_subscriber.phone,
                        "Balanced {} is {}. Reply with STOP to unsubscribe.".format(
                        service, current_state))
            except TwilioException, e:
                LOGGER.error("Failed to send SMS via Twilio - " + e.msg)
                pass
