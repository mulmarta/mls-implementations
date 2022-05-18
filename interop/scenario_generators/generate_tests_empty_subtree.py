from itertools import chain
from platform import node
from venv import create
import tree_math

def commit_and_process(actions, actor_names, committer_name, proposals):
    actions.append('"action": "commit", "actor": "{}"'.format(committer_name))
    commit_index = len(actions) - 1
    actions.append('"action": "handlePendingCommit", "actor": "{}"'.format(committer_name))
    for actor in actor_names:
        if actor != committer_name:
            actions.append('"action": "handleCommit", "actor": "{}", "commit": {}, "byReference": {}'.format(actor, commit_index, proposals))
    return commit_index

def add_actor(actions, actor_names, new_actor_name):
    if actor_names == []:
        return
    actions.append('"action": "createKeyPackage", "actor": "{}"'.format(new_actor_name))
    actions.append('"action": "addProposal", "actor": "{}", "keyPackage": {}'.format(actor_names[0], len(actions)-1))
    proposal_index = len(actions) - 1
    commit_index = commit_and_process(actions, actor_names, actor_names[0], [proposal_index])
    actions.append('"action": "joinGroup", "actor": "{}", "welcome": {}'.format(new_actor_name, commit_index))

def all_actors_commit(actions, actor_names):
    for committer in actor_names:
        commit_and_process(actions, actor_names, committer, [])

def create_group(actor_names):
    if actor_names == []:
        return
    actions = ['"action": "createGroup", "actor": "{}"'.format(actor_names[0])]
    for i in range(1, len(actor_names)):
        add_actor(actions, actor_names[:i], actor_names[i])
    return actions

def remove_actors(actions, actor_names, removed_actor_indices, committer_name):
    proposal_indices = list(range(len(actions), len(actions) + len(removed_actor_indices)))
    for index in removed_actor_indices:
        actions.append('"action": "removeProposal", "actor": "{}", "removedLeafIndex": {}'.format(committer_name, index))
    commit_and_process(actions, actor_names, committer_name, proposal_indices)

def blank_subtree(actions, actor_names, node_index, tree_size):
    leftmost = node_index
    while leftmost & 1 == 1:
        leftmost = tree_math.left(leftmost)
    leftmost = leftmost >> 1

    rightmost = node_index
    while rightmost & 1 == 1:
        rightmost = tree_math.right(rightmost, tree_size)
    rightmost = rightmost >> 1

    # Committer is in the subtree of the sibling of node_index
    if tree_math.parent(node_index, tree_size) < node_index:
        committer_index = leftmost - 1
    else:
        committer_index = rightmost + 1

    remove_actors(actions, actor_names, list(range(leftmost, rightmost+1)), actor_names[committer_index])

def get_test(tree_size, node_index):
    actor_names = ['actor{}'.format(i) for i in range(tree_size)]
    actions = create_group(actor_names)
    all_actors_commit(actions, actor_names)
    # remove_actors(actions, actor_names, [2, 3], 'actor0')
    blank_subtree(actions, actor_names, node_index, tree_size)
    return ",\n          ".join(map(lambda a : "{" + a + "}", actions))

with open('config.json', 'w') as f:
    f.write('''
    {
      "clients": [
        "localhost:50003"
      ],
      "scripts": {
        "script": [
          ''')
    f.write(get_test(40, 7))
    f.write('''
        ]
      }
    }
    ''')