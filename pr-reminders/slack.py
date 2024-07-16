import logging
from string import Template
from slack_sdk import WebClient
from typing import List

logging.basicConfig(level=logging.DEBUG)


class Bot:
    def __init__(self, slack_bot_token: str):
        self.client = WebClient(slack_bot_token)

    def send_message(self, channel, message, header):
        response = self.client.chat_postMessage(
            channel=channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*_# {header}_*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
            ]
        )
        return response

    def send_message_with_user_mention(self, channel, template: Template, user_email,
                                       header):
        user_response = self.client.users_lookupByEmail(email=user_email)
        user_id = user_response['user']['id']
        message = template.substitute(user=f'<@{user_id}>')
        return self.send_message(channel, message, header)

    def send_message_with_user_mentions(self, channel, template: Template,
                                        user_emails: List[str], header):
        user_responses = [self.client.users_lookupByEmail(
            email=email) for email in user_emails]
        user_ids = [response['user']['id'] for response in user_responses]
        user_id_references = [f'<@{user_id}>' for user_id in user_ids]
        message = template.substitute(users=''.join(user_id_references))
        return self.send_message(channel, message, header)
