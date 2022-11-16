import logging
import os
from string import Template
from slack_sdk import WebClient
from typing import List

logging.basicConfig(level=logging.DEBUG)

# Visit the Legacy custom integrations page from your desktop at my.slack.com/apps/manage/custom-integrations.
# Click  Edit configuration next to the bot user you'd like to change.
# On the configuration page, click Regenerate below the current token. This is the new token you can use anywhere you need it.
SLACK_ACCESS_TOKEN_VAR = 'SLACK_BOT_ACCESS_TOKEN'

class Bot:
    def __init__(self, slack_bot_token: str = None):
        if slack_bot_token is None:
            if SLACK_ACCESS_TOKEN_VAR not in os.environ:
                raise RuntimeError(f'{SLACK_ACCESS_TOKEN_VAR} must be set as an environment variable')
            slack_bot_token = os.environ[SLACK_ACCESS_TOKEN_VAR]
        self.client = WebClient(slack_bot_token)

    def send_message(self, channel, message):
        response = self.client.chat_postMessage(
            channel=channel,
            text=message
        )
        return response

    def send_message_with_user_mention(self, channel, template: Template, user_email):
        user_response = self.client.users_lookupByEmail(email=user_email)
        user_id = user_response.data['user']['id']
        message = template.substitute(user=f'<@{user_id}>')
        return self.send_message(channel, message)

    def send_message_with_user_mentions(self, channel, template: Template, user_emails: List[str]):
        user_responses = [self.client.users_lookupByEmail(email=email) for email in user_emails]
        user_ids = [response.data['user']['id'] for response in user_responses]
        user_id_references = [f'<@{user_id}>' for user_id in user_ids]
        message = template.substitute(users=''.join(user_id_references))
        return self.send_message(channel, message)
