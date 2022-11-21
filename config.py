from dataclasses import dataclass
import json
from pathlib import Path
from typing import List

from squad_member import SquadMember


@dataclass
class Config:
    users: List[SquadMember]
    reminders: List[str]
    repo_node_ids: List[str]
    slack_channel_id: str


def read_config_file(config_file_path: Path) -> dict:
    with open(config_file_path) as config_file:
        return json.load(config_file)


def parse_config(config_data: dict) -> Config:
    return Config(
        repo_node_ids=config_data['repo_node_ids'],
        reminders=config_data['reminders'],
        users=[SquadMember(user['email'], user['github_username'])
               for user in config_data['users']],
        slack_channel_id=config_data['slack_channel_id']
    )


def load_config(config_file_path: Path) -> Config:
    config_data = read_config_file(config_file_path)
    return parse_config(config_data)
