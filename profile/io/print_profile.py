import sys

class CallTree(object):
    def __init__(self, funcname):
        self.funcname = funcname
        self.children = {}
        self.callCounter = 0

    def addChildCall(self, call_tree):
        if not call_tree.funcname in self.children:
            self.children[call_tree.funcname] = call_tree

    def incCallCounter(self):
        self.callCounter = self.callCounter + 1

def iprint(root, current_node, ident_level):
    ident_str = "-"
    for i in range(ident_level):
        ident_str = ident_str + "-"
    ident_str = ident_str + ">"
    print ident_str, current_node.funcname, str(current_node.callCounter)
    for child_name, child in current_node.children.iteritems():
        iprint(root, child, ident_level + 1)

def call_tree(stacks):
    root = CallTree(beefs)
    for stack in stacks:
        current_root = root
        for func in reversed(stack):
            if func in current_root.children:
                current_root = current_root.children[func]
                current_root.incCallCounter()
            else:
                tmpRoot = CallTree(func)
                tmpRoot.incCallCounter()
                current_root.addChildCall(tmpRoot)#inc propagation ?
                current_root = tmpRoot
    return root

"""
    Usage: python $0 < btrac.out > out
"""
if __name__ == "__main__":

    stacks_by_exec = {}

    current_stack = None
    for line in sys.stdin:
        if "#" in line:
            continue
        if "execname" in line:
            current_stack = []
            stack_id = current_execname, pid, tid =\
            tuple([token.split("=")[1].strip() for token in\
                                                          line.split(" ")])

            if not stack_id in stacks_by_exec:
                stacks_by_exec[stack_id] = []

            stacks_by_exec[stack_id].append(current_stack)
        else:
            func = line.split(":")[1].split("+")[0].strip()
            current_stack.append(func)

    print "#stacks", len(stacks_by_exec)
    root = None
    beefs = "beefs_replayer"
    filtered_stacks = []

    if (sys.argv[1] == "a"):
        for ((_execname, pid, tid), stacks) in stacks_by_exec.iteritems():
            if _execname == beefs:
                sys.stderr.write(" ".join(["a", pid, tid, "\n"]))
                filtered_stacks.extend(stacks)
    elif (sys.argv[1] == "w"):
        for ((_execname, pid, tid), stacks) in stacks_by_exec.iteritems():
            if ((_execname == beefs) and (pid != tid)):
                sys.stderr.write(" ".join(["w", pid, tid, str(pid != tid), "\n"]))
                filtered_stacks.extend(stacks)
    else:
        sys.stderr.write("Usage: python $0 [w,a] < btrace.out\n")
        exit(1)

    print "#filtered_stacks", len(filtered_stacks)
    root = call_tree(filtered_stacks)
    iprint(root, root, 0)
