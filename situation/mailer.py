from google.appengine.api import mail
import settings
import base64
from urlparse import urlparse

class Mail(object):
    def __init__(self):
        self.sender = settings.EMAIL['sender']

    def send(self, email_address, subject, message, request_url=None):
        if not email_address or not subject or not message:
            return False

        if request_url:
            request_url = urlparse(request_url)

            # Add unsubscribe footer to e-emails
            message = message + "\n\n" + \
            "Click the following link below at any time to unsubscribe.\n" + \
            request_url.scheme + "://" + request_url.netloc + \
            "/subscriptions/email/" + base64.urlsafe_b64encode(email_address)

        return mail.send_mail(self.sender, email_address, subject, message)