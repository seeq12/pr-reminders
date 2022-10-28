import datetime
import json
import os
import requests
from typing import List, NewType

from squad import members_github_usernames

Username = NewType('Username', str)
GITHUB_ACCESS_TOKEN_VAR = 'GITHUB_ACCESS_TOKEN'
# These node IDs can be found via: View the page source, Search the page source and look for
# octolytics-dimension-repository_id.
# You should find something that looks like:
# <command-palette-page-stack data-default-scope-id="MDEwOlJlcG9zaXRvcnkyNTU2NzQ4ODQ="
REPO_NODE_IDS = ['MDEwOlJlcG9zaXRvcnkyNTU2NzQ4ODQ=']


class PrData:
    def __init__(self,
                 updated_at: datetime.datetime,
                 title: str,
                 html_url: str,
                 is_draft: bool,
                 reviewers: List[Username]):
        self.updated_at = updated_at
        self.title = title
        self.html_url = html_url
        self.is_draft = is_draft
        self.reviewers = reviewers

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.title}, {self.html_url}>'


def _extract_reviewers(pull_request: dict) -> List[Username]:
    review_requests = pull_request['reviewRequests']['nodes']
    teams = [review_request['requestedReviewer']['members']['nodes']
             for review_request in review_requests
             if 'members' in review_request['requestedReviewer']]
    team_usernames = {Username(member['login']) for team in teams for member in team}
    user_usernames = {Username(review_request['requestedReviewer']['login'])
                      for review_request in review_requests
                      if 'members' not in review_request['requestedReviewer']}
    return [member for member in list(team_usernames | user_usernames) if member in members_github_usernames]


class GithubApi:
    def __init__(self, access_token: str = None):
        if access_token is None:
            if GITHUB_ACCESS_TOKEN_VAR not in os.environ:
                raise RuntimeError(f'{GITHUB_ACCESS_TOKEN_VAR} must be set as an environment variable')
            access_token = os.environ[GITHUB_ACCESS_TOKEN_VAR]
        self.access_token = access_token

    def _fetch_graphql(self, request: dict):
        headers = {'Authorization': f'bearer {self.access_token}'}
        endpoint = 'https://api.github.com/graphql'
        response = requests.post(endpoint, headers=headers, data=json.dumps(request))
        response.raise_for_status()
        return response.json()

    def _fetch_open_pull_requests(self, repo_ids: List[str]) -> dict:
        return self._fetch_graphql({
            'variables': {'repo_ids': repo_ids},
            'query': """query($repo_ids:[ID!]!) {
                          nodes (ids: $repo_ids) {
                            ... on Repository {
                              name
                              pullRequests(states: OPEN, first: 100, orderBy: {field: UPDATED_AT, direction: ASC}) {
                                nodes {
                                  title
                                  updatedAt
                                  url
                                  isDraft

                                  reviews(states: [APPROVED, CHANGES_REQUESTED], first: 50) {
                                    totalCount
                                    nodes {
                                      state
                                      author {
                                        login
                                      }
                                    }
                                  }

                                  reviewRequests(first: 50) {
                                    totalCount
                                    nodes {
                                      requestedReviewer {
                                        ... on Team {
                                          members(first: 50) {
                                            nodes {
                                              login
                                            }
                                          }
                                        }
                                        ... on User {
                                          login
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
            """
        })

    def fetch_prs_needing_review(self) -> List[PrData]:
        result = self._fetch_open_pull_requests(REPO_NODE_IDS)
        prs = [pr for repo in result['data']['nodes']
               for pr in repo['pullRequests']['nodes']
               if pr['reviews']['totalCount'] == 0 and pr['reviewRequests']['totalCount'] > 0 and len(_extract_reviewers(pr)) > 0]
               #if pr['reviewRequests']['totalCount'] > 0 and len(_extract_reviewers(pr)) > 0]
        return [
            PrData(
                datetime.datetime.strptime(pr['updatedAt'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc),
                pr['title'],
                pr['url'],
                pr['isDraft'],
                _extract_reviewers(pr)
            )
            for pr in prs
        ]
