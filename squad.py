from typing import List

from squad_member import SquadMember


def build_github_username_lookup(users: List[SquadMember]) -> dict[str, SquadMember]:
    return {user.github_username: user for user in users}
