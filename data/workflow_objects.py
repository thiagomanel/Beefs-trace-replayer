def objects(workflow_line_tokens):
    """
       it parses a workflow line into a tuple (id, n_parents, parents, n_children, children, syscall)
       workflow lines examples:
       1 0 - 3 2 3 2 1159 16303 16318 (chrome) open 1319203757986598-1310 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 32962 384 43
       2 2 1 1 1 3 1159 16303 16318 (chrome) fstat 1319203757987999-87 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 43 0
    """
    #our workflow format is shit ! this "-" when empty parents or children is BS
    _id = int(workflow_line_tokens[0])
    n_parents = int(workflow_line_tokens[1])

    if n_parents:
        parents = [int(parent) for parent in workflow_line_tokens[2:2 + n_parents]]
    else:
        parents = []

    if n_parents > 1:
        n_children_pos = 2 + n_parents
    else:
        n_children_pos = 3

    n_children = int(workflow_line_tokens[n_children_pos])
    if n_children:
        children = [int(child) for child in workflow_line_tokens[n_children_pos + 1:n_children_pos + 1 + n_children]]
        syscall_index = n_children_pos + 1 + n_children
    else:
        children = []
        syscall_index = n_children_pos + 2
    
    syscall = "".join(workflow_line_tokens[syscall_index:])
    return (_id, n_parents, parents, n_children, children, syscall)
