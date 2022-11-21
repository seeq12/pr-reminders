import datetime
import json
import os
import requests
from typing import List, NewType

Username = NewType('Username', str)


class PrData:
    def __init__(self,
                 updated_at: datetime.datetime,
                 title: str,
                 body: str,
                 html_url: str,
                 is_draft: bool,
                 reviewers: List[Username]):
        self.updated_at = updated_at
        self.title = title
        self.body = body
        self.html_url = html_url
        self.is_draft = is_draft
        self.reviewers = reviewers

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.title}, {self.html_url}>'


def _extract_reviewers(github_usernames: List[str], pull_request: dict) -> List[Username]:
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


class GithubApi:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def _fetch_graphql(self, request: dict):
        headers = {'Authorization': f'bearer {self.access_token}'}
        endpoint = 'https://api.github.com/graphql'
        response = requests.post(
            endpoint, headers=headers, data=json.dumps(request))
        response.raise_for_status()
        return response.json()

    def _fetch_open_pull_requests(self, repo_ids: List[str]) -> dict:
        """
        repo_node_ids can be found via: View the page source, Search the page source and look for
        octolytics-dimension-repository_id.
        You should find something that looks like:
        <command-palette-page-stack data-default-scope-id="MDEwOlJlcG9zaXRvcnkyNTU2NzQ4ODQ="
        """
        with open('pull_requests.graphql') as query_file:
            return self._fetch_graphql({
                'variables': {'repo_ids': repo_ids},
                'query': query_file.read()
            })

    def fetch_prs_needing_review(self, github_usernames: List[str], repo_node_ids: List[str]) -> List[PrData]:
        result = self._fetch_open_pull_requests(repo_node_ids)
        prs = [pr for repo in result['data']['nodes']
               for pr in repo['pullRequests']['nodes']
               if pr['reviews']['totalCount'] == 0 and pr['reviewRequests']['totalCount'] > 0 and len(
            _extract_reviewers(github_usernames, pr)) > 0]
        return [
            PrData(
                datetime.datetime.strptime(
                    pr['updatedAt'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc),
                pr['title'],
                pr['body'],
                pr['url'],
                pr['isDraft'],
                _extract_reviewers(github_usernames, pr)
            )
            for pr in prs
        ]

    def fetch_all_prs_for_squad(self, github_usernames: List[str], repo_node_ids: List[str]) -> List[PrData]:
        result = self._fetch_open_pull_requests(repo_node_ids)
        prs = [pr for repo in result['data']['nodes']
               for pr in repo['pullRequests']['nodes']
               if len(_extract_reviewers(github_usernames, pr)) > 0]
        return [
            PrData(
                datetime.datetime.strptime(
                    pr['updatedAt'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc),
                pr['title'],
                pr['body'],
                pr['url'],
                pr['isDraft'],
                _extract_reviewers(github_usernames, pr)
            )
            for pr in prs
        ]
