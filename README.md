# Introduction
The tool will 
* notify the reviewers of PRs needing review on a Slack channel (PRs with 0 reviews and number of review requests > 0 
having at least one reviewer from the Team)
* notify the reviewers of sleeping PRs on a Slack channel (PRs with no activity in tha last 3 days)
* notify the reviewers of PRs with no primary reviewer on a Slack channel

# Configuration of the tool
## Environment variables
* GITHUB_ACCESS_TOKEN - Github access token to be used to call the Github API to find out open PRs
* NOTIFY_REVIEWERS_SLACK_CHANNEL - Slack channel where the Bot will send the reminders
* SLACK_BOT_ACCESS_TOKEN - Slack access token to be used to send the reminders
* SQUAD_CSV_FILENAME - The name of a CSV file containing the mapping between user email and github user

## Structure of the csv file given by SQUAD_CSV_FILENAME
The tool needs to know for each member the email address (to be able to interact with Slack) and github user account 
(to interact with Github).

The csv defining the mapping between emails and github users has to have 2 columns:
- Email - the email of the team member 
- GithubUser - the github user of the team member

Example csv file:
```
Email,GithubUser
your.name@seeq.com,yourGithubUser
another.user@seeq.com,anotherGithubUser
```
