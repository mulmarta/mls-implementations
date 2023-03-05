import tree_math
import collections
import base64

'''
actors: a list representing consecutive leaves in the tree. actors[leaf_index] is either
 * actor_name of leaf's owner
 * None if leaf is blank
'''

class Group:
    def __init__(self, num_members, name):
        self.name = name
        self.actors = ['actor0']
        self.actions = []
        self.next_free_actor = 1

        self.actions.append('"action": "createGroup", "actor": "actor0"')
        for _ in range(1, num_members):
            self.add_actor()
    
    def add_actor(self):
        '''
        An arbitrary member commits adding a new actor, all members process the add, new member joins.
        '''
        new_actor_name = "actor{}".format(self.next_free_actor)
        self.next_free_actor += 1

        committer = 0
        while self.actors[committer] == None: committer += 1

        self.actions.append('"action": "createKeyPackage", "actor": "{}"'.format(new_actor_name))
        self.actions.append('"action": "addProposal", "actor": "{}", "keyPackage": {}'.format(self.actors[committer], len(self.actions)-1))
        proposal_index = len(self.actions) - 1
        commit_index = self.commit_and_process(committer, [(proposal_index, committer)])
        self.actions.append('"action": "joinGroup", "actor": "{}", "welcome": {}'.format(new_actor_name, commit_index))
        self.insert_new_actor(new_actor_name)

    def insert_new_actor(self, new_actor_name):
        i = 0
        while i < len(self.actors):
            if self.actors[i] is None:
                self.actors[i] = new_actor_name
                break
            i += 1
        if i == len(self.actors):
            self.actors.append(new_actor_name)

    def commit_and_process(self, committer, proposals, removed = set()):
        '''
        Committer commits the proposals list, then all actors process.
        '''
        if self.actors[committer] == None:
            return None

        self.actions.append('"action": "commit", "actor": "{}", "byReference": {}'.format(
            self.actors[committer],
            [prop for prop, sender in proposals],
        ))

        commit_index = len(self.actions) - 1
        self.actions.append('"action": "handlePendingCommit", "actor": "{}"'.format(self.actors[committer]))

        for actor in range(len(self.actors)):
            if actor in removed:
                continue

            if actor != committer and self.actors[actor] is not None:
                self.actions.append('"action": "handleCommit", "actor": "{}", "commit": {}, "byReference": {}'.format(
                    self.actors[actor],
                    commit_index,
                    [prop for prop, sender in proposals if sender != actor],
                ))
        return commit_index
    
    def all_actors_commit(self):
        for committer in range(len(self.actors)):
            self.commit_and_process(committer, [])
    
    def remove_actors(self, committer, removed_actor_indices):
        if self.actors[committer] == None:
            return None

        committer = self.actors[committer]

        proposals = []
        for i in removed_actor_indices:
            if i < len(self.actors) and self.actors[i] is not None:
                proposals.append((len(self.actions), 'actor{}'.format(committer)))
                self.actions.append('"action": "removeProposal", "actor": "{}", "removed": {}'.format(committer, self.actors[i]))
                self.actors[i] = None

        self.commit_and_process(committer, proposals)

        i = len(self.actors) - 1
        while i >= 0 and self.actors[i] is None:
            self.actors.pop()
            i -= 1
    
    def propose_and_commit(self, committer, proposals, should_succeed=True):
        props = []
        added_actors = []
        removed_indices = set()
        for proposal, sender, data in proposals:
            if proposal == 'add':
                new_actor_name = "actor{}".format(self.next_free_actor)
                self.next_free_actor += 1
                added_actors.append(new_actor_name)
                self.actions.append('"action": "createKeyPackage", "actor": "{}"'.format(new_actor_name))
                proposal_data = ', "keyPackage": {}'.format(len(self.actions)-1)
            elif proposal == 'remove':
                proposal_data = ', "removed": "{}"'.format(self.actors[data])
                removed_indices.add(data)
            elif proposal == 'update':
                proposal_data = ''
            elif proposal == 'externalPSK':
                proposal_data = ', "pskId": "{}"'.format(data)
            elif proposal == 'groupContextExtensions':
                proposal_data = ', "extensions": {{{}}}'.format(', '.join('"{}": "{}"'.format(k, v) for k, v in data.items()))
            props.append((len(self.actions), sender))
            self.actions.append('"action": "{}Proposal", "actor": "{}"{}'.format(proposal, self.actors[sender], proposal_data))
        commit_index = self.commit_and_process(committer, props, removed_indices)
        if should_succeed:
            for removed in removed_indices:
                self.actors[removed] = None
            for new_actor_name in list(collections.OrderedDict.fromkeys(added_actors)):
                self.insert_new_actor(new_actor_name)
                self.actions.append('"action": "joinGroup", "actor": "{}", "welcome": {}'.format(new_actor_name, commit_index))

    def send_app_message(self, sender, message_bytes):
        if self.actors[sender] == None:
            return None
        self.actions.append('"action": "protect", "actor": "{}", "applicationData": "{}"'.format(self.actors[sender], b64string(message_bytes)))
        return len(self.actions) - 1
    
    def receive_app_message(self, receiver, ciphertext_index):
        if self.actors[receiver] == None:
            return None
        self.actions.append('"action": "unprotect", "actor": "{}", "ciphertext": {}'.format(self.actors[receiver], ciphertext_index))
        return len(self.actions) - 1

    def get_actor_in_range(self, left, right):
        '''
        Returns an actor with leaf index in range [left, right)
        '''
        for i in range(left, right):
            if self.actors[i] is not None:
                return i
        return None

    def get_nonempty_actors(self):
        return [i for i in range(len(self.actors)) if self.actors[i] is not None]

    def get_json(self):
        actions_str = ",\n      ".join(map(lambda a : "{" + a + "}", self.actions))
        header = '\n    "{}": [\n      '.format(self.name)
        footer = '\n    ]'
        return header + actions_str + footer

    def __str__(self):
        return str(self.actors)

def b64string(bytes):
    return str(base64.b64encode(bytes))[2:-1]

def get_json(groups):
    header = '{\n  "clients": [\n    "localhost:50003"\n  ],\n  "scripts": {\n'
    scripts = ','.join(g.get_json() for g in groups)
    footer = '\n  }\n}'
    return header + scripts + footer
