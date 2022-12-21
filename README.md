# Introduction
The tool will
* notify the reviewers of PRs needing review on a Slack channel (PRs with 0 reviews and number of review requests > 0
having at least one reviewer from the Team)
* notify the reviewers of sleeping PRs on a Slack channel (PRs with no activity in tha last 3 days)
* notify the reviewers of PRs with no primary reviewer on a Slack channel

# Configuration of the tool
## Environment variables
* GITHUB_ACCESS_TOKEN - Github access token to be used to call the Github API to find out open PRs
* SLACK_BOT_ACCESS_TOKEN - Slack access token to be used to send the reminders
* PR_REMINDERS_CONFIG_PATH - The json file specific to your squad. Example: config/connectability.json

# Python HTTP Function

Welcome to your new Python function project! The boilerplate function
code can be found in [`func.py`](./func.py). This function will respond
to incoming HTTP GET and POST requests.

## Endpoints

Running this function will expose three endpoints.

  * `/` The endpoint for your function.
  * `/health/readiness` The endpoint for a readiness health check
  * `/health/liveness` The endpoint for a liveness health check

The health checks can be accessed in your browser at
[http://localhost:8080/health/readiness]() and
[http://localhost:8080/health/liveness]().

You can use `func invoke` to send an HTTP request to the function endpoint.


## Testing

This function project includes a [unit test](./test_func.py). Update this
as you add business logic to your function in order to test its behavior.

```console
python test_func.py
```
