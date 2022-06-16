import tree_math
from utils import *

with open('config.json', 'w') as f:
    g = Group(5)
    g.propose_and_commit(
        0,
        [
            ('add', 1, None),
            ('remove', 1, 2),
            ('update', 1, None),
            ('update', 1, None),
            ('update', 2, None),
            #('externalPSK', 4, b64string(b'the PskId')),
        ]
    )
    g.propose_and_commit(
        0,
        [
            ('add', 0, None),
        ]
    )
    print(g)
    f.write(g.get_json())