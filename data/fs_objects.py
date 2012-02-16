def fullpath(call_tokens):
    return call_tokens[6]#FIXME move this to clean_trace.py module

def dirs(fullpath):
    print fullpath
    _dirs = []
    _dirs.append(fullpath)
    last_slash = fullpath.rfind("/")
    if (last_slash > 0):
        _dirs.extend(dirs(fullpath[:fullpath.rfind("/")]))
    return _dirs

def basename(fullpath):
    return []

def accessed_and_created(tokens):
    """
    """
    _fullpath = fullpath(tokens)
    return (dirs(_fullpath), basename(_fullpath), [], [])
