# Scripts

The file specifies a number of `scripts`. Each script describes a particular scenario describing the life of a group. In particular, each script specifies a sequence of **actions** (e.g. sending a proposal) performed by **actors** (e.g. alice). At each point in time, each actor has at most one MLS client who participates in at most one MLS session. A client and a session for an actor are created in one of two ways:

1. When the actor executes the createGroup action, a client with a session is created.
2. When the actor executes the createKeyPackage action, a client without a session is created. When later the actor executes the joinGroup action, a session for the client is created.

Note: Creating a new client / session silently overwrites the first one.


# Actions

Each action specifies two values: a string `action` set to the action type (e.g. `addProposal`) and a string `actor` set to the name of the actor performing the action. Some action specify more values. Such values may be pointers to outputs of previous actions. For example, the action `addProposal` specifies a pointer to the `createKeyPackage` action that created the key package of the added client. A pointer to an action is always its index in the sequence of all actions in the given script.

The outputs of each action are logged in the `transcript` as key-value pairs. Outputs can be either packets packets sent to the delivery service (logged as hex-encoded bytes) or values outputted to the user (stored as strings). The `transcript` is printed to STDOUT.


The following actions are supported.


| `action`             | Values specified by the action in addition to `actor` and `action` | Output values stored in `transcript` | Description                                       |
|:---------------------|:-------------------------------------------|:------------------------------|:--------------------------------------------------|
| `createGroup`        | -                                          | -                             | A new client for the `actor` and a new group with themselves in it are created.      |
| `createKeyPackage`   | -                                          | `keyPackage`: packet                   | A new client for the `actor` and a new key package for them are created.      |
| `addProposal`        | `keyPackage`: int                          | `proposal`: packet               | The `actor`’s current client sends a proposal that adds a member with the key package created during the `createKeyPackage` action with index `keyPackage`. |
| `removeProposal`     | `removedLeafIndex`: int                    | `proposal`: packet               | The `actor`’s current client sends a proposal that removes a member with leaf index `removedLeafIndex`. |
| `externalPSKProposal`     | `pskId`: string                    | `proposal`: packet               | The `actor`’s current client sends an external PSK proposal with given `pskId` given as b64 encoded bytes. (Only external PSKs are allowed; resumption PSKs are only used in reinitialization). |
| `groupContextExtensionsProposal`     | `extensions`: map[int]string                    | `proposal`: packet               | The `actor`’s current client sends a proposal that replaces group context extensions by `extensions` represented as an array mapping `extension_type` given a int to `extension_data` given as b64 encoded bytes. |
| `commit`             | `byReference`: []int                       | `commit`: packet, `welcome`: packet | The `actor`’s current client first processes the proposals created during actions identified by the indices in the list `byReference` and then they send a commit. The `byReference` list MUST NOT include proposals from `actor`. |
| `handlePendingCommit`| -                                          | state update (see below)                  | The `actor`’s current client accepts the commit it sent. |
| `handleCommit`       | `commit`: int, `byReference`: []int        | state update (see below)                  | The `actor`’s current client first processes the proposals created during actions with indices specified in `byReference`. Then it processes the commit created during the `commit` action with index `commit` which includes them by reference. The `byReference` list MUST NOT include proposals created by `actor`. The `commit` MUST NOT have been created by `actor`.
| `joinGroup`          | `welcome`: int                        | [TODO]                        | The `actor`’s current client joins the group using the welcome message created during the `commit` action index `welcome`. This creates a new session.
| `protect`            | `applicationData`: string                  | `ciphertext`: packet             | The `actor`’s current client encrypts given data, given as b64 encoded bytes. |
| `unprotect`          | `ciphertext`: int                          | `applicationData`: hex encoded bytes              | The `actor`’s current client decrypts the ciphertext created during the `protect` action with index `ciphertext`. The message MUST NOT have been generated by the actor. |

State update outputted after processing a commit is a list consisting of zero or more of the following items. Here `i` is always an integer used to make keys unique.

* Key `added[i]`, value `leafIndex` denotes that a member was added and now has given `leafIndex`.
* Key `updated[i]`, value `leafIndex` denotes that an update from a member with given `leafIndex` was applied.
* Key `removedIndex[i]`, value `leafIndex` followed by key `removedLeaf[i]`, value `leafNode` denotes that a member who had given `leafIndex` was removed and his leaf node (no longer in the tree) used to be `leafNode` (represented as TLS-serialized hex-encoded bytes).
* Key `psks[i]`, value `pskId` denotes that a PSK with given `pskId` was mixed into the key schedule. The value `pskId` includes all data from `PreSharedKeyID` except `nonce`. It is TLS-serialized and hex-encoded.






