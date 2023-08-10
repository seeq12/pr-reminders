# Introduction
The tool will
* notify the reviewers of PRs needing review on a Slack channel (PRs with 0 reviews and number of review requests > 0
having at least one reviewer from the Team)
* notify the reviewers of sleeping PRs on a Slack channel (PRs with no activity in tha last 3 days)
* notify the reviewers of PRs with no primary reviewer on a Slack channel

# Configuration of the tool
## Environment variables
* GITHUB_ACCESS_TOKEN - Github access token to be used to call the Github API to find open PRs
* SLACK_BOT_ACCESS_TOKEN - Slack access token to be used to send the reminders
* PR_REMINDERS_CONFIG_PATH - The json file specific to your team. Example: example/config.json

# Contributing

Contributions to this repo are welcome!

To work on the code in this repo, you'll need a few things:

- A Slack account and bot token - see [Creating the Slack Bot](#creating-the-slack-bot)
- A GitHub account and access token - see [Configuring the GitHub Token](#configuring-the-github-token)
- A config file - see [Creating the Config File](#creating-the-config-file)
- A configured environment - see [Configuring the Environment](#configuring-the-environment)

Then, it's recommended to create a virtual environment using Python 3.11 (see [the venv documentation](https://docs.python.org/3/library/venv.html)):
```
python3 -m venv .venv
source .venv/bin/activate
```

Then, you're ready to install dependencies:
```
pip install -r requirements.txt
```

And finally, run the bot:
```
python main_reminders.py
```

## Creating the Slack Bot

Once you have a Slack account, you can create a Slack bot using the following steps.

1. Go to the Slack apps management page: https://api.slack.com/apps/
2. Click the “Create New App” button.
3. If this is your first time visiting this page, it should be very prominent.
4. Fill out the basic info for your “App” - this will include the name of your app (and bot user) in Slack.
5. Click on “OAuth & Permissions” in the left sidebar.
6. Scroll down to “Scopes.”
7. Under “Bot Token Scopes,” click “Add an OAuth Scope.”
8. Add the scopes you need for your bot. For this app, you'll need to read some basic user data (ID and email), join a channel, and send messages, so add:
    - `channels:join`
    - `chat:write`
    - `users:read`
    - `users:read.email`
9. Scroll back to the top of the page.
10. Click “Install to Workspace.”
11. Select your workspace.
12. You should now have a “Bot User OAuth Token” that you can use in your workspace as your bot.

## Configuring the GitHub Token

First, see [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for how to set up a personal access token.

The token will need the following permissions:
- `repo` (all permissions)
- `read:org` - to properly expand teams
- `read:user`
- `user:email`

## Creating the Config File

The configuration file has a specific schema - see [example/config.json](/example/config.json) for an example. See [config.py](/config.py) for more information on supported configuration.

## Configuring the Environment

You can configure your environment in the usual way (`.zshrc` etc.), or you can use the built-in [dotenv](https://pypi.org/project/python-dotenv/) support.

The environment variables you'll need to set are described in [Environment variables](#environment-variables).

## Test

# Python HTTP Function

There is a Knative function [`func.py`](./func.py) that can be used to deploy on Knative. You can also run the function locally using the [Knative func CLI](https://knative.dev/docs/functions/install-func/)'s `func run`.

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

This function project includes an [integration test](./test_func.py). It passes but it doesn't really test anything useful (yet). Please add tests if you have some time!

```console
python test_func.py
```
