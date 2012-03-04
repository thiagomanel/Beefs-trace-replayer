class WorkflowLine:
    """
       it parses a workflow line into a tuple (id, n_parents, parents, n_children, children, syscall)
       workflow lines examples:
       1 0 - 3 2 3 2 1159 16303 16318 (chrome) open 1319203757986598-1310 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 32962 384 43
       2 2 1 1 1 3 1159 16303 16318 (chrome) fstat 1319203757987999-87 /home/thiagoepdc/.config/google-chrome/com.google.chrome.gUMVsk 43 0
    """
    def __init__(self, workflow_line_tokens):
        #our workflow format is shit ! this "-" when empty parents or children is BS
        self._id = int(workflow_line_tokens[0])
        self.n_parents = int(workflow_line_tokens[1])

        if self.n_parents:
            self.parents = [int(parent) for parent in workflow_line_tokens[2:2 + self.n_parents]]
        else:
            self.parents = []

        if self.n_parents > 1:
            n_children_pos = 2 + n_parents
        else:
            n_children_pos = 3

        self.n_children = int(workflow_line_tokens[n_children_pos])
        if self.n_children:
            self.children = [int(child) for child in workflow_line_tokens[n_children_pos + 1:n_children_pos + 1 + self.n_children]]
            syscall_index = n_children_pos + 1 + self.n_children
        else:
            self.children = []
            syscall_index = n_children_pos + 2
    
        self.syscall = " ".join(workflow_line_tokens[syscall_index:])
