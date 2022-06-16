from app_messages import *


def get_json(groups):
    header = '{\n  "clients": [\n    "localhost:50003"\n  ],\n  "scripts": {\n'
    scripts = ','.join(g.get_json() for g in groups)
    footer = '\n  }\n}'
    return header + scripts + footer

groups = []

for n in [50, 63, 64, 65]:
    g = Group(n, "appMsgs: simpleCase")
    m = 3
    for sndr_list, num_msgs in [
        ([1, n // 2, n - 2], 1000),
        (range(1, n-1), 3),
    ]:
        simple_case(g, n, m, sndr_list, num_msgs)
    group_chnges(g, n)
    groups.append(g)


with open('config.json', 'w') as f:
    f.write(get_json(groups))