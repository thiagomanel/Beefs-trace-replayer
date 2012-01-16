from enum import Enum

#		   (oct ?)  dec
#O_ACCMODE         0003	      	 3			
#O_RDONLY            00		 0
#O_WRONLY            01		 1
#O_RDWR              02		 2

#O_CREAT           0100		64
#O_EXCL            0200	       128
#O_NOCTTY          0400	       256
#O_TRUNC          01000        512

#O_APPEND         02000	      1024
#O_NONBLOCK       04000	      2048
#O_NDELAY    O_NONBLOCK
#O_SYNC          010000       4096
#O_FSYNC         O_SYNC
#O_ASYNC         020000       8192

#FIXME: it would be nice to have bind a value to enum value (in this case
#we can use it to store de flag octal code)
ACCESS_MODES = Enum("O_RDONLY", "O_WRONLY", "O_RDWR")
CREATION_FLAGS = Enum("O_CREAT", "O_EXCL", "O_NOCTTY", "O_TRUNC", 
                         "O_APPEND", "O_NONBLOCK", "O_NDELAY", 
                         "O_SYNC", "O_FSYNC", "O_ASYNC")

# something outside the range [0,3] is a programming error and the code should 
# fail
__value2access_modes__ = {0:ACCESS_MODES.O_RDONLY, 1:ACCESS_MODES.O_WRONLY, 
                           2:ACCESS_MODES.O_RDWR, 3:None}

__value2creation_flags__ = {64:CREATION_FLAGS.O_CREAT, 128:CREATION_FLAGS.O_EXCL, 
                               256:CREATION_FLAGS.O_NOCTTY, 
                               512:CREATION_FLAGS.O_TRUNC,
                               1024:CREATION_FLAGS.O_APPEND, 
                               2048:CREATION_FLAGS.O_NONBLOCK, 
                               4096:CREATION_FLAGS.O_SYNC, 
                               8192:CREATION_FLAGS.O_ASYNC}

""" from linux open flags to a human-friendly representation. 
http://linux.die.net/man/2/open
"""
def access_mode_bits(open_flags):
    return open_flags & 3

def access_mode(open_flags):
    return __value2access_modes__[access_mode_bits(open_flags)]

def creation_flags_bits(open_flags):
    return open_flags & ~3

def match(open_flags, flag_code):#see flag codes in table above
    return (open_flags & flag_code) == flag_code
    

def creation_flags(open_flags):
    flags = []
    for (code, flag) in __value2creation_flags__.iteritems():
        if match(open_flags, code):
            flags.append(flag)
    return flags
