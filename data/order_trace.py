from itertools import tee
from itertools import izip
from itertools import chain

def pidfidprocess(tokens):
    return (tokens[1], tokens[2], tokens[3])

def order_by_pidfid(lines):

    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)

    def join(father, son):
        if son:
            father[3] = father[3] + 1
            father[4].append(son[0])
            son[1] = son[1] + 1
            son[2].append(father[0])

    lines_by_fidpidprocess = {}

    for (_id, line) in enumerate(lines):
        pfp = pidfidprocess(line.split())
        if not pfp in lines_by_fidpidprocess:
            lines_by_fidpidprocess[pfp] = []
        lines_by_fidpidprocess[pfp].append([_id + 1, 0, [], 0, [], line])

    for lines in lines_by_fidpidprocess.values():
        for (father, son) in pairwise(lines):
            join(father, son)

    return chain(lines_by_fidpidprocess.values())
