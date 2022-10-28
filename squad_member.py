class SquadMember:
    def __init__(self, email: str, github_username: str):
        self.email = email
        self.github_username = github_username

    def __repr__(self):
        return f'<SquadMember: {self.email}, {self.github_username}>'
