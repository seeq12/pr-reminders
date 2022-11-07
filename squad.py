import csv
import os

from squad_member import SquadMember


SQUAD_CSV_FILENAME_VAR = 'SQUAD_CSV_FILENAME'


def _read_from_csv() -> list[SquadMember]:
    if SQUAD_CSV_FILENAME_VAR not in os.environ:
        raise RuntimeError(f'{SQUAD_CSV_FILENAME_VAR} must be set as an environment variable')
    csv_name = os.environ[SQUAD_CSV_FILENAME_VAR]
    squad_members = []
    with open(csv_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            squad_members.append(SquadMember(row['Email'], row['GithubUser']))
    return squad_members


members = _read_from_csv()
members_github_usernames = [member.github_username for member in members]
github_username_lookup = {member.github_username: member for member in members}
