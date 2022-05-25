import tree_math
from utils import *


def blank_subtree(group, node_index):
    leftmost = node_index
    while leftmost & 1 == 1:
        leftmost = tree_math.left(leftmost)
    leftmost = leftmost >> 1

    rightmost = node_index
    while rightmost & 1 == 1:
        rightmost = tree_math.right(rightmost, group.size())
    rightmost = rightmost >> 1

    to_remove = list(range(leftmost, rightmost+1))

    # Committer is in the subtree of the sibling of node_index
    if tree_math.parent(node_index, group.size()) < node_index:
        committer = group.get_actor_in_range(2 * leftmost - rightmost - 1, leftmost)
    else:
        committer = group.get_actor_in_range(rightmost + 1, 2 * rightmost - leftmost + 2)

    group.remove_actors(committer, to_remove)

    return to_remove


with open('config.json', 'w') as f:
    g = Group(17)
    g.all_actors_commit()
    #blank_subtree(g, 5)
    blank_subtree(g, 11)
    blank_subtree(g, 19)
    g.all_actors_commit()
    g.add_actor()
    print(g)
    f.write(g.get_json())