from dataclasses import dataclass

from parliament import Context  # type: ignore
from flask import Request

import main_reminders


@dataclass
class Response:
  body: dict
  status: int = 200


def handle(req: Request) -> Response:
  try:
    main_reminders.main()
    return Response({'data': 'Success!'})
  except RuntimeError as e:
    return Response({'data': str(e)}, 500)


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
