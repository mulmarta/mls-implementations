from group import *

g = Group(1, "Basic Run")

g.propose_and_commit(0, [('add', 0, None) for _ in range(10000)])


with open('config.json', 'w') as f:
    f.write(get_json([g]))
