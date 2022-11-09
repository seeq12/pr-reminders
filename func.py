from dataclasses import dataclass
import json

from parliament import Context
from flask import Request

from main_reminders import notify_reviewers_of_prs_needing_review, notify_reviewers_of_prs_without_primary, notify_reviewers_of_sleeping_prs


@dataclass
class Response:
  body: dict
  status: int = 200


def handle(req: Request) -> Response:
  if req.method == "GET":
    notify_reviewers_of_prs_needing_review()
    notify_reviewers_of_prs_without_primary()
    notify_reviewers_of_sleeping_prs()
    return Response({'data': 'Success!'})
  else:
    return Response({'data': 'Not found'}, 404)


def main(context: Context):
    """
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    """
    print("Received request", flush=True)

    if 'request' in context.keys():
        res = handle(context.request)
        return res.body, res.status
    else:
        print("Empty request", flush=True)
        return "{}", 404
