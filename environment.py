from dataclasses import dataclass
import os
import pathlib

import lib


VAR_PARSERS = {
    'PR_REMINDERS_CONFIG_PATH': {
        'parse': pathlib.Path,
        'dest': 'config_file_path'
    },
    'GITHUB_ACCESS_TOKEN': {
        'parse': lib.identity,
        'dest': 'github_access_token'
    },
    'SLACK_BOT_ACCESS_TOKEN': {
        'parse': lib.identity,
        'dest': 'slack_access_token'
    }
}


@dataclass
class Environment:
    config_file_path: pathlib.Path
    github_access_token: str
    slack_access_token: str


def load_environment():
    return Environment(**parse_environment(os.environ, VAR_PARSERS))


def parse_environment(environment: dict, parsers: dict) -> dict:
    return {parser['dest']: parser['parse'](get_env_var(environment, var))
            for var, parser in parsers.items()}


def get_env_var(environment: dict, var: str) -> str:
    if var not in environment:
        raise RuntimeError(
            f'{var} must be set as an environment variable')
    return environment[var]
