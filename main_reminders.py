from datetime import datetime, timedelta, timezone
from string import Template
from typing import List
import slack

import environment
import config as configuration
from github_api import GithubApi, PrData
import squad
from squad_member import SquadMember


def main():
    env = environment.load_environment()
    config = configuration.load_config(env.config_file_path)
    notify_reviewers_of_prs_needing_review(
        env.github_access_token,
        env.slack_access_token,
        config.slack_channel_id,
        config.users,
        config.repo_node_ids)
    notify_reviewers_of_prs_without_primary(
        env.github_access_token,
        env.slack_access_token,
        config.slack_channel_id,
        config.users,
        config.repo_node_ids)
    notify_reviewers_of_sleeping_prs(
        env.github_access_token,
        env.slack_access_token,
        config.slack_channel_id,
        config.users,
        config.repo_node_ids)


def notify_reviewers_of_prs_needing_review(
        github_access_token: str,
        slackbot_access_token: str,
        notify_reviewers_channel: str,
        users: List[SquadMember],
        repo_node_ids: List[str]):
    gh_api = GithubApi(github_access_token)
    prs_needing_review = sorted(
        gh_api.fetch_prs_needing_review(
            [user.github_username for user in users], repo_node_ids),
        key=lambda pr: pr.updated_at)
<<<<<<< HEAD
    if len(prs_needing_review) > 0:
        _slackbot_notify(
            slackbot_access_token,
            notify_reviewers_channel,
            users,
            'The following PRs have review requests and zero reviews - please take a look!',
            prs_needing_review)
    else:
        _slackbot_notify(slackbot_access_token, notify_reviewers_channel, users,
                         'All PRs have at least one review :tada:! Great work team!', prs_needing_review)
=======

    message = 'The following PRs have review requests and zero reviews - ' \
              'please take a look!' \
        if len(prs_needing_review) > 0 \
        else 'All PRs have at least one review :tada:! Great work team!'

    _slackbot_notify(
            slackbot_access_token,
            notify_reviewers_channel,
            users,
            message,
            prs_needing_review)
>>>>>>> origin/feature/sajo/knative-func


def notify_reviewers_of_prs_without_primary(
        github_access_token: str,
        slack_access_token: str,
        notify_reviewers_channel: str,
        users: List[SquadMember],
        repo_node_ids: List[str]):
    gh_api = GithubApi(github_access_token)
    all_prs_of_squad = sorted(
        gh_api.fetch_all_prs_for_squad(
            [user.github_username for user in users], repo_node_ids),
        key=lambda pr: pr.updated_at)
    prs_without_primary = [pr for pr in all_prs_of_squad if _no_primary(pr)]
<<<<<<< HEAD
    if len(prs_without_primary) > 0:
        _slackbot_notify(
            slack_access_token,
            notify_reviewers_channel,
            users,
            'The following PRs have have no primary reviewer - please take a look!',
            prs_without_primary)
    else:
        _slackbot_notify(
            slack_access_token,
            notify_reviewers_channel,
            users,
            'All PRs have a primary reviewer :tada:! Great work team!',
            prs_without_primary)
=======

    message = 'The following PRs have have no primary reviewer - please take a look!' \
        if len(prs_without_primary) > 0 \
        else 'All PRs have a primary reviewer :tada:! Great work team!'

    _slackbot_notify(
        slack_access_token,
        notify_reviewers_channel,
        users,
        message,
        prs_without_primary)
>>>>>>> origin/feature/sajo/knative-func


def notify_reviewers_of_sleeping_prs(
        github_access_token: str,
        slack_access_token: str,
        notify_reviewers_channel: str,
        users: List[SquadMember],
        repo_node_ids: List[str]):
    past = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=3)
    gh_api = GithubApi(github_access_token)
    all_prs_of_squad = sorted(
        gh_api.fetch_all_prs_for_squad(
            [user.github_username for user in users], repo_node_ids),
        key=lambda pr: pr.updated_at)
    sleeping_prs = [pr for pr in all_prs_of_squad if pr.updated_at < past]
<<<<<<< HEAD
    if len(sleeping_prs) > 0:
        _slackbot_notify(
            slack_access_token,
            notify_reviewers_channel,
            users,
            'The following PRs are sleeping (no update in the last 3 days) - please take a look!',
            sleeping_prs)
    else:
        _slackbot_notify(
            slack_access_token,
            notify_reviewers_channel,
            users,
            'All PRs are active. No PR is sleeping :tada:! Great work team!',
            sleeping_prs)
=======

    message = 'The following PRs are sleeping (no update in the last 3 days) - ' \
              'please take a look!' \
        if len(sleeping_prs) > 0 \
        else 'All PRs are active. No PR is sleeping :tada:! Great work team!'

    _slackbot_notify(
        slack_access_token,
        notify_reviewers_channel,
        users,
        message,
        sleeping_prs)
>>>>>>> origin/feature/sajo/knative-func


def _no_primary(pr: PrData) -> bool:
    primary = _extract_primary(pr).lower()
    return primary.find('replace this with a @mention') >= 0 or primary.find('volunt') >= 0


def _slackbot_notify(
        slackbot_access_token: str,
        notify_reviewers_channel,
        users: List[SquadMember],
        notification_text: str,
        prs: list[PrData]):
    reviewer_emails = _reviewers_for_prs(users, prs)
    slackbot = slack.Bot(slackbot_access_token)
    pr_messages = [_build_pr_message(pr) for pr in prs]
    message_template = Template(notification_text + '\n\n '
                                + '\n'.join(pr_messages)
                                + '\n\n$users')
    slackbot.send_message_with_user_mentions(
        notify_reviewers_channel, message_template, reviewer_emails)


def _extract_primary(pr: PrData) -> str:
    after_marker1 = pr.body.find(
        '**Primary reviewer**') + len('**Primary reviewer**')
    marker2 = pr.body.find('**Knowledge base**')
    if after_marker1 < 0 or marker2 < after_marker1:
        return ''
    return pr.body[after_marker1: marker2].strip()


def _reviewers_for_prs(users: List[SquadMember], prs_needing_review):
    github_username_lookup = squad.build_github_username_lookup(users)
    all_reviewer_squad_members = list({
        github_username_lookup[reviewer]
        for pr in prs_needing_review
        for reviewer in pr.reviewers
        if reviewer in github_username_lookup
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
    main()
