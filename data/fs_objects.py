from clean_trace import *

#TODO: after using this module do we guarantee all file system hierarchy was created ? So, replayer
	#can run fine ?

def success(call_tokens):#FIXME move this to clean_trace.py module
    return_value = int(call_tokens[-1])
    if return_value < 0:
        return False
    return True 

def fullpath(call_tokens):
    return call_tokens[6]#FIXME move this to clean_trace.py module

def dirs(fullpath):
    _dirs = []
    _dirs.append(fullpath)
    last_slash_index = fullpath.rfind("/")
    if (last_slash_index > 0):
        _dirs.extend(dirs(fullpath[:last_slash_index]))
    return _dirs

#close and fstat handles fd. we can get its information on the related open call
def accessed_and_created(tokens):
    if success(tokens):
        _fullpath = fullpath(tokens)
        _call = call(tokens)
        if (_call == "unlink" or _call == "stat" or _call == "read" or _call == "write" or _call == "llseek"):#FIXME we can make basename and dirs to manage this
            parent = parent_path(_fullpath)
            return (dirs(parent), [basename(_fullpath)], [], [])
        elif (_call == "rmdir"):
            return (dirs(_fullpath), [], [], [])
        elif _call == "mkdir":
            parent = parent_path(_fullpath)
            return (dirs(parent), [], [basename(_fullpath)], [])
        elif _call == "open":
            parent = parent_path(_fullpath)
            return (dirs(parent), [basename(_fullpath)], [], [])

    return ([], [], [], [])
