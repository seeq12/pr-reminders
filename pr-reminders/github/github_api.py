from dataclasses import dataclass
import datetime
import requests
from typing import List, NewType

import github.queries as queries

Username = NewType('Username', str)


@dataclass
class PrData:
    updated_at: datetime.datetime
    title: str
    body: str
    html_url: str
    is_draft: bool
    reviewers: List[Username]
    review_requests_count: int
    reviews_count: int
    author: Username
    assignees: List[Username]


def parse_prs(github_usernames: List[str], query_response: dict) -> List[PrData]:
    try:
        return [
            PrData(
                datetime.datetime.strptime(
                    pr['updatedAt'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc),
                pr['title'],
                pr['body'],
                pr['url'],
                pr['isDraft'],
                _extract_reviewers(github_usernames, pr),
                pr['reviewRequests']['totalCount'],
                pr['reviews']['totalCount'],
                pr['author']['login'],
                _extract_assignees(pr['assignees']['nodes'])
            )
            for pr in query_response['data']['repository']['pullRequests']['nodes']
        ]
    except KeyError as e:
        raise RuntimeError(
            f"Could not parse PR data from response data: {query_response}"
        ) from e


def _extract_reviewers(github_usernames: List[str], pull_request: dict) -> List[Username]:
    if pull_request['reviewRequests']['totalCount'] == 0:
        return []
    review_requests = pull_request['reviewRequests']['nodes']
    teams = [review_request['requestedReviewer']['members']['nodes']
             for review_request in review_requests
             if 'members' in review_request['requestedReviewer']]
    team_usernames = {Username(member['login'])
                      for team in teams for member in team}
    user_usernames = {Username(review_request['requestedReviewer']['login'])
                      for review_request in review_requests
                      if 'members' not in review_request['requestedReviewer']}
    return [member for member in list(team_usernames | user_usernames) if member in github_usernames]


def _extract_assignees(assignees_nodes: List[dict]) -> List[Username]:
    return [Username(assignee['login']) for assignee in assignees_nodes]


class GithubApi:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def fetch(self, query_request: queries.QueryRequest) -> dict:
        headers = {'Authorization': f'bearer {self.access_token}'}
        endpoint = 'https://api.github.com/graphql'
        response = requests.post(
            endpoint, headers=headers, json=query_request)
        response.raise_for_status()
        return response.json()
