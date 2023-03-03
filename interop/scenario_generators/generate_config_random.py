from group import *
import random as rnd
import sys

'''
`NUM_CYCLES` times, executes a number A of adds, R of removes and U of updates, followed by
a commit from a random member. A, R and U are chosen s.t. the group size N is always
`MIN_GROUP_SIZE <= N < MAX_GROUP_SIZE`.
'''
MAX_GROUP_SIZE = 10000
MIN_GROUP_SIZE = 1
INIT_GROUP_SIZE = 100

NUM_CYCLES = 30

MAX_NUM_OPS = 1000
RATIO_ADDS = .3
RATIO_REMS = .3
RATIO_UPDS = .3

seed = rnd.randint(0, sys.maxsize)
#seed = 1170625869743070381
print("Starting random tests with rand seed {}".format(seed))
rnd.seed(seed)

def random_updates():
    g = Group(INIT_GROUP_SIZE,  "Random Updates, Adds, Removes")
    for _ in range(NUM_CYCLES):
        actors = g.get_nonempty_actors()
        a, r, u = get_num_ops(len(actors))
        rnd.shuffle(actors)
        committer = actors[0]
        # TODO remove by random meber??
        proposals = [ ('remove', committer, actors[i]) for i in range(1, r + 1) ]
        proposals.extend( ('add', committer, None) for _ in range(a) )
        proposals.extend( ('update', actors[i], None) for i in range(r + 1, r + u + 1) )
        g.propose_and_commit(committer, proposals)
    return g
    
def get_num_ops(group_size):
    for _ in range(10000):
        a = rnd.randint(0, int(RATIO_ADDS * MAX_NUM_OPS))
        r = rnd.randint(0, int(RATIO_REMS * MAX_NUM_OPS))
        u = rnd.randint(0, int(RATIO_UPDS * MAX_NUM_OPS))
        if MIN_GROUP_SIZE <= group_size + a - r and group_size + a - r < MAX_GROUP_SIZE and u < group_size - r:
            return a, r, u
    raise "Fail"

with open('config.json', 'w') as f:
    f.write(get_json([random_updates()]))