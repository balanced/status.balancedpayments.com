from twilio.rest import TwilioRestClient
import settings


class SMS(object):
    def __init__(self):
        self.client = TwilioRestClient(
            settings.TWILIO['account_sid'],
            settings.TWILIO['auth_token'],
        )

    def send(self, phone_number, message):
        if not phone_number or not message:
            return False

        # Cleanup phone number, strip spaces, dashes, ( and )
        phone_number = phone_number.replace(' ', '').replace(
            '-', '').replace('(', '').replace(')', '')

        # Limit message to 160 characters, enforced by Twilio
        message = message[:160]

        return self.client.sms.messages.create(
            to=phone_number,
            from_=settings.TWILIO['from_number'],
            body=message,
        )
