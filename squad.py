from squad_member import SquadMember

# TODO: Extract this in a csv file so that the utility can be used for other squads

nikhila = SquadMember('nikhila.albert@seeq.com', 'totallyna')
chris = SquadMember('chris.herrera@seeq.com', 'cherrera2001')
james = SquadMember('james.demarco@seeq.com', 'DJamesP')
mariuso = SquadMember('marius.oancea@seeq.com', 'mar1u50')
rianflynn = SquadMember('rian.flynn@seeq.com', 'rianflynn')
winner = SquadMember('winner.bolorunduro@seeq.com', 'bolorundurowb-sq')
andrerigon = SquadMember('andre.rigon@seeq.com', 'andre-rigon')
alberto = SquadMember('alberto.rivas@seeq.com', 'monstrorivas')
hiro = SquadMember('hiroito.watanabe@seeq.com', '1hirow')

members = [
    nikhila,
    chris,
    james,
    mariuso,
    rianflynn,
    winner,
    andrerigon,
    alberto,
    hiro
]

members_github_usernames = [member.github_username for member in members]
github_username_lookup = {member.github_username: member for member in members}
