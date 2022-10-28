# Introduction
The tool will notify the reviewers of PRs needing review on a Slack channel.

"Needing review" is defined as:
* PRs with 0 reviews and
* number of review requests > 0
* having at least one reviewer from the Team

# Configuration of the tool
## Environment variables
* GITHUB_ACCESS_TOKEN - Github access token to be used to call the Github API to find out open PRs.
* NOTIFY_REVIEWERS_SLACK_CHANNEL - Slack channel where the Bot will send the reminders
* SLACK_BOT_ACCESS_TOKEN - Slack access token to be used to send the reminders

## squad.py
`squad.py` needs to define the members of the squad. The tool needs to to know for each member the email address 
(to be able to interact with Slack) and github user account (to interact with Github).

