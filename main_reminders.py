from datetime import datetime, timedelta, timezone
from string import Template
from github_api import GithubApi, PrData
import slack
import squad
import os

NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME = 'NOTIFY_REVIEWERS_SLACK_CHANNEL'


def notify_reviewers_of_prs_needing_review():
    gh_api = GithubApi()
    prs_needing_review = sorted(gh_api.fetch_prs_needing_review(), key=lambda pr: pr.updated_at)
    _slackbot_notify(
        'The following PRs have review requests and zero reviews - please take a look!',
        prs_needing_review)


def notify_reviewers_of_prs_without_primary():
    gh_api = GithubApi()
    all_prs_of_squad = sorted(gh_api.fetch_all_prs_for_squad(), key=lambda pr: pr.updated_at)
    prs_without_primary = [pr for pr in all_prs_of_squad if _no_primary(pr)]
    _slackbot_notify(
        'The following PRs have have no primary reviewer - please take a look!',
        prs_without_primary)


def notify_reviewers_of_sleeping_prs():
    past = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=3)
    gh_api = GithubApi()
    all_prs_of_squad = sorted(gh_api.fetch_all_prs_for_squad(), key=lambda pr: pr.updated_at)
    sleeping_prs = [pr for pr in all_prs_of_squad if pr.updated_at < past]
    _slackbot_notify(
        'The following PRs are sleeping (no update in the last 3 days) - please take a look!',
        sleeping_prs)


def _no_primary(pr: PrData) -> bool:
    primary = _extract_primary(pr).lower()
    return primary.find('replace this with a @mention') >= 0 or primary.find('volunt') >= 0


def _slackbot_notify(notification_text: str, prs: list[PrData]):
    reviewer_emails = _reviewers_for_prs(prs)
    slackbot = slack.Bot()
    pr_messages = [_build_pr_message(pr) for pr in prs]
    message_template = Template(notification_text + '\n\n '
                                + '\n'.join(pr_messages)
                                + '\n\n$users')
    slackbot.send_message_with_user_mentions(_notify_reviewers_channel(), message_template, reviewer_emails)


def _notify_reviewers_channel():
    if NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME not in os.environ:
        raise RuntimeError(f'{NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME} must be set as an environment variable')

    return os.environ.get(NOTIFY_REVIEWERS_SLACK_CHANNEL_VAR_NAME)


def _extract_primary(pr: PrData) -> str:
    after_marker1 = pr.body.find('**Primary reviewer**') + len('**Primary reviewer**')
    marker2 = pr.body.find('**Knowledge base**')
    if after_marker1 < 0 or marker2 < after_marker1:
        return ''
    return pr.body[after_marker1: marker2].strip()


def _reviewers_for_prs(prs_needing_review):
    all_reviewer_squad_members = list({
        squad.github_username_lookup[reviewer]
        for pr in prs_needing_review
        for reviewer in pr.reviewers
        if reviewer in squad.github_username_lookup
    })
    reviewer_emails = [member.email for member in all_reviewer_squad_members]
    return reviewer_emails


def _build_pr_message(pr: PrData):
    updated_at_timestamp = int(pr.updated_at.timestamp())
    updated_at_text = pr.updated_at.strftime('%B %d')
    # https://api.slack.com/reference/surfaces/formatting#date-formatting
    return f'* <{pr.html_url}|{pr.title}> ' \
           f'<!date^{updated_at_timestamp}^(Waiting since {{date_short_pretty}} at {{time}})|{updated_at_text}>'


if __name__ == '__main__':
    notify_reviewers_of_prs_needing_review()
    notify_reviewers_of_prs_without_primary()
    notify_reviewers_of_sleeping_prs()
