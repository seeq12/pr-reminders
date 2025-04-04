from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import itertools
from string import Template
from typing import List, TypedDict
import slack

import environment
import config as configuration
from github import queries, github_api
import squad
from squad_member import SquadMember


class PrReminder(TypedDict):
    message: str
    header: str
    prs: List[github_api.PrData]
    notify_reviewers: bool
    notify_author: bool
    notify_assignee: bool


def main():
    env = environment.load_environment()
    config = configuration.load_config(env.config_file_path)
    pr_query = queries.load_query('pull_requests.graphql')
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    repo_pr_queries = [queries.QueryRequest(query=pr_query, variables=repo)
                       for repo in config.repos]
    gh_api = github_api.GithubApi(env.github_access_token)

    query_responses = [gh_api.fetch(query_request)
                       for query_request in repo_pr_queries]

    github_usernames = [user.github_username for user in config.users]
    prs = itertools.chain.from_iterable(
        [github_api.parse_prs(github_usernames, query_response)
         for query_response in query_responses]
    )
    sorted_prs = sorted(_no_drafts(prs), key=lambda pr: pr.updated_at)
    reminders = [
        _needs_review_reminder(sorted_prs),
        _sleeping_reminder(now, sorted_prs),
        _no_primary_reminder(sorted_prs)
    ]

    slackbot = slack.Bot(env.slack_access_token)
    for reminder in reminders:
        _slackbot_notify(slackbot, config.slack_channel_id,
                         config.users, reminder['message'], reminder['prs'],
                         reminder['header'], reminder['notify_reviewers'],
                         reminder['notify_author'], reminder['notify_assignee'])


def _needs_review_reminder(prs: List[github_api.PrData]) -> PrReminder:
    prs_needing_review = [
        pr for pr in prs
        if pr.review_requests_count > 0 and pr.reviews_count == 0
    ]
    message = 'The following PRs have review requests and zero reviews - please take a look!' \
        if len(prs_needing_review) > 0 \
        else 'All PRs have at least one review :tada:! Great work team!'
    return PrReminder(
        prs=prs_needing_review,
        message=message,
        header='PRs with Review Requests and Zero Reviews',
        notify_reviewers=True,
        notify_author=True,
        notify_assignee=True
    )


def _sleeping_reminder(now: datetime, prs: List[github_api.PrData]) -> PrReminder:
    sleeping_prs = [
        pr for pr in prs
        if pr.updated_at < now - timedelta(days=3)
    ]
    message = 'The following PRs are sleeping (no update in the last 3 days) - please take a look!' \
        if len(sleeping_prs) > 0 \
        else 'All PRs are active. No PRs are sleeping :tada:! Great work team!'
    return PrReminder(
        prs=sleeping_prs,
        message=message,
        header='PRs Sleeping (No Update in the Last 3 Days)',
        notify_reviewers=False,
        notify_author=True,
        notify_assignee=True
    )


def _no_primary_reminder(prs: List[github_api.PrData]) -> PrReminder:
    prs_without_primary = [
        pr for pr in prs if _no_primary(pr)
    ]
    message = 'The following PRs have no primary reviewer - please take a look!' \
        if len(prs_without_primary) > 0 \
        else 'All PRs have a primary reviewer :tada:! Great work team!'
    return PrReminder(
        prs=prs_without_primary,
        message=message,
        header='PRs with No Primary Reviewer',
        notify_reviewers=True,
        notify_author=True,
        notify_assignee=True
    )


def _no_primary(pr: github_api.PrData) -> bool:
    primary = _extract_primary(pr).lower()
    return primary.find('replace this with a @mention') >= 0 or primary.find('volunt') >= 0


def _slackbot_notify(
        slackbot: slack.Bot,
        notify_reviewers_channel,
        users: List[SquadMember],
        notification_text: str,
        prs: list[github_api.PrData],
        message_header: str,
        notify_reviewers: bool,
        notify_author: bool,
        notify_assignee: bool) -> None:
    maybe_authors_emails = _authors_for_prs(users, prs) if notify_author else []
    maybe_assignee_emails = _assignees_for_prs(users, prs) if notify_assignee else []
    maybe_reviewer_emails = _reviewers_for_prs(users, prs) if notify_reviewers else []
    emails_to_notify = list(set(maybe_authors_emails + maybe_assignee_emails + maybe_reviewer_emails))
    pr_messages = [_build_pr_message(pr) for pr in prs]
    message_template = Template(notification_text + '\n\n '
                                + '\n'.join(pr_messages)
                                + '\n\n$users')
    slackbot.send_message_with_user_mentions(
        notify_reviewers_channel, message_template, emails_to_notify, message_header)


def _extract_primary(pr: github_api.PrData) -> str:
    after_marker1 = pr.body.find(
        '**Primary reviewer**') + len('**Primary reviewer**')
    marker2 = pr.body.find('**Knowledge base**')
    if after_marker1 < 0 or marker2 < after_marker1:
        return ''
    return pr.body[after_marker1: marker2].strip()


def _no_drafts(prs):
    exclude_title_keywords = ['[WIP]', '[DRAFT]']
    filtered_prs = [pr for pr in prs if
                    len(pr.reviewers) > 0 and
                    not pr.is_draft and
                    not any(keyword.lower() in pr.title.lower()
                            for keyword in exclude_title_keywords)]
    return filtered_prs


def _emails_for_prs(users: List[SquadMember], prs: List[github_api.PrData], extract_usernames) -> List[str]:
    github_username_lookup = squad.build_github_username_lookup(users)
    squad_members = list({
        github_username_lookup[username]
        for pr in prs
        for username in extract_usernames(pr)
        if username in github_username_lookup
    })
    return [member.email for member in squad_members]


def _reviewers_for_prs(users: List[SquadMember], prs: List[github_api.PrData]) -> List[str]:
    return _emails_for_prs(users, prs, lambda pr: pr.reviewers)


def _assignees_for_prs(users: List[SquadMember], prs: List[github_api.PrData]) -> List[str]:
    return _emails_for_prs(users, prs, lambda pr: pr.assignees)


def _authors_for_prs(users: List[SquadMember], prs: List[github_api.PrData]) -> List[str]:
    return _emails_for_prs(users, prs, lambda pr: [pr.author])


def _build_pr_message(pr: github_api.PrData) -> str:
    updated_at_timestamp = int(pr.updated_at.timestamp())
    updated_at_text = pr.updated_at.strftime('%B %d')
    # https://api.slack.com/reference/surfaces/formatting#date-formatting
    return f'- <{pr.html_url}|{pr.title}> ' \
           f'<!date^{updated_at_timestamp}^(Waiting since {{date_short_pretty}} at {{time}})|{updated_at_text}>'


if __name__ == '__main__':
    load_dotenv()
    main()
