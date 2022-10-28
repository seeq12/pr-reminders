from string import Template
from github_api import GithubApi, PrData
import slack
import squad
import os

NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME = 'NOTIFY_REVIEWERS_SLACK_CHANNEL'

def build_pr_message(pr: PrData):
    updated_at_timestamp = int(pr.updated_at.timestamp())
    updated_at_text = pr.updated_at.strftime('%B %d')
    # https://api.slack.com/reference/surfaces/formatting#date-formatting
    return f'* <{pr.html_url}|{pr.title}> ' \
           f'<!date^{updated_at_timestamp}^(Waiting since {{date_short_pretty}} at {{time}})|{updated_at_text}>'


def notify_reviewers_of_prs_needing_review():
    if NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME not in os.environ:
        raise RuntimeError(f'{NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME} must be set as an environment variable')

    notify_reviewers_channel = os.environ.get(NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME)

    gh_api = GithubApi()
    prs_needing_review = sorted(gh_api.fetch_prs_needing_review(), key=lambda pr: pr.updated_at)
    pr_messages = [build_pr_message(pr) for pr in prs_needing_review]
    all_reviewer_squad_members = list({
        squad.github_username_lookup[reviewer]
        for pr in prs_needing_review
        for reviewer in pr.reviewers
        if reviewer in squad.github_username_lookup
    })
    reviewer_emails = [member.email for member in all_reviewer_squad_members]

    slackbot = slack.Bot()
    message_template = Template(f'The following PRs have review requests and zero reviews - please take a look!\n\n'
                                + '\n'.join(pr_messages)
                                + '\n\n$users')
    slackbot.send_message_with_user_mentions(notify_reviewers_channel, message_template, reviewer_emails)


if __name__ == '__main__':
    notify_reviewers_of_prs_needing_review()
    # TODO: add PRs without activity in last 3 days