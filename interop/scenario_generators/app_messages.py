from group import *
import random

random.seed(42)

MAX_OUT_OF_ORDER = 1000

def shuffle(ctxts):
    for i in range(0, len(ctxts) - MAX_OUT_OF_ORDER, MAX_OUT_OF_ORDER):
        slice = ctxts[i: i+MAX_OUT_OF_ORDER]
        random.shuffle(slice)
        ctxts[i: i+MAX_OUT_OF_ORDER] = slice

def simple_case(g, n, m, sndr_list, num_msgs):
    ctxts, ptxts = [], []
    for i in range(m):
        for leaf in sndr_list:
            for j in range(num_msgs):
                ptxts.append("msg {} {}".format(i, j))
                ctxts.append(g.send_app_message(leaf, bytes("msg {} {}".format(i, j), 'ascii')))
        if i < m-1:
            g.commit_and_process(0, [])
    shuffle(ctxts)
    for rcvr in [0, n-1]:
        for ctxt in ctxts:
            g.receive_app_message(rcvr, ctxt)

def group_chnges(g, n):
    a, b, c = 0, n // 2, n-1
    ctxA = g.send_app_message(a, b'msgA')
    ctxB1 = g.send_app_message(b, b'msgB1')
    g.propose_and_commit(a, [('update', b, None)])
    ctxB2 = g.send_app_message(b, b'msgB2')
    g.propose_and_commit(a, [('remove', a, b), ('add', a, None)])
    ctxD = g.send_app_message(b, b'msgD')
    g.propose_and_commit(b, [('add', b, None)])
    for ctx in [ctxB1, ctxB2, ctxD]:
        g.receive_app_message(a, ctx)
    for ctx in [ctxA, ctxB1, ctxB2, ctxD]:
        g.receive_app_message(c, ctx)