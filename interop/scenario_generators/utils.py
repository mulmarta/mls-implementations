import tree_math

'''
actors: a list representing consecutive leaves in the tree. actors[leaf_index] is either
 * actor_name of leaf's owner
 * None if leaf is blank
'''

class Group:
    def __init__(self, num_members):
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

        committer = next(actor for actor in self.actors if actor is not None)

        self.actions.append('"action": "createKeyPackage", "actor": "{}"'.format(new_actor_name))
        self.actions.append('"action": "addProposal", "actor": "{}", "keyPackage": {}'.format(committer, len(self.actions)-1))
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

    def commit_and_process(self, committer, proposals):
        '''
        Committer commits the proposals list, then all actors process.
        '''
        self.actions.append('"action": "commit", "actor": "{}", "byReference": {}'.format(
            committer, 
            [prop for prop, sender in proposals if sender != committer],
        ))

        commit_index = len(self.actions) - 1
        self.actions.append('"action": "handlePendingCommit", "actor": "{}"'.format(committer))

        for actor in self.actors:
            if actor != committer and actor is not None:
                self.actions.append('"action": "handleCommit", "actor": "{}", "commit": {}, "byReference": {}'.format(
                    actor,
                    commit_index,
                    [prop for prop, sender in proposals if sender != actor],
                ))
        return commit_index
    
    def all_actors_commit(self):
        for committer in self.actors:
            if committer is not None:
                self.commit_and_process(committer, [])
    
    def remove_actors(self, committer, removed_actor_indices):
        proposals = []
        for i in removed_actor_indices:
            if i < len(self.actors) and self.actors[i] is not None:
                proposals.append((len(self.actions), 'actor{}'.format(committer)))
                self.actions.append('"action": "removeProposal", "actor": "{}", "removedLeafIndex": {}'.format(committer, i))
                self.actors[i] = None

        self.commit_and_process(committer, proposals)

        i = len(self.actors) - 1
        while i >= 0 and self.actors[i] is None:
            self.actors.pop()
            i -= 1
    
    def propose_and_commit(self, committer, proposals):
        props = []
        added_actors = []
        for proposal, sender, data in proposals:
            if proposal == 'add':
                new_actor_name = "actor{}".format(self.next_free_actor)
                self.next_free_actor += 1
                added_actors.append(new_actor_name)
                self.actions.append('"action": "createKeyPackage", "actor": "{}"'.format(new_actor_name))
                proposal_data = ', "keyPackage": {}'.format(len(self.actions)-1)
            elif proposal == 'remove':
                proposal_data = ', "removedLeafIndex": {}'.format(data)
            elif proposal == 'update':
                proposal_data = ''
            props.append((len(self.actions), 'actor{}'.format(sender)))
            self.actions.append('"action": "{}Proposal", "actor": "actor{}"{}'.format(proposal, sender, proposal_data))
        self.commit_and_process('actor{}'.format(committer), props)
        #for new_actor_name in added_actors:
        #    self.insert_new_actor(new_actor_name)

    def get_actor_in_range(self, left, right):
        '''
        Returns an actor with leaf index in range [left, right)
        '''
        for i in range(left, right):
            if self.actors[i] is not None:
                return self.actors[i]
        return None

    def size(self):
        return len(self.actors)

    def get_json(self):
        actions_str = ",\n      ".join(map(lambda a : "{" + a + "}", self.actions))
        header = '{\n  "clients": [\n    "localhost:50003"\n  ],\n  "scripts": {\n    "script": [\n      '
        footer = '\n    ]\n  }\n}'
        return header + actions_str + footer

    def __str__(self):
        return str(self.actors)