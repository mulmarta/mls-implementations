from group import *

N = 17

g = Group(N, "Basic Run")
# updates work
g.propose_and_commit(
    1,
    [
        ("update", N // 2, None),
        ("update", N-1, None),
    ]
)
# remove without truncate
g.propose_and_commit(
    2,
    [
        ("remove", N // 2, N-2),
    ]
)
# remove with truncate
g.propose_and_commit(
    2,
    [
        ("remove", N // 2, N-1),
    ]
)
# add without extend
g.propose_and_commit(
    3,
    [
        ("add", 4, None),
    ]
)
# add with extend
g.propose_and_commit(
    3,
    [
        ("add", 5, None),
    ]
)
# committing multiple proposals
g.propose_and_commit(
    12,
    [
        ("remove", 0, 1),
        ("remove", 2, 3),
        ("add", 0, None),
        ("update", 5, None),
        ("add", 5, None),
        ("add", 7, None),
    ]
)
# everyone can commit
g.all_actors_commit()


with open('config.json', 'w') as f:
    f.write(get_json([g]))