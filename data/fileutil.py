from enum import Enum

#  P.S Disclaimer. my intention with this code is to learn python, otherwise we can use a dict{oct_value:string} and a couple of list to solve the problem

#FIXME This code works just fine but we can refactor it to an object (it seems beaultiful and I can learn more pythonic code):
#  1. it has an init method which receives the numeric open argument
#  2. it has an __repr__ which allows to eval to the object back
#  3. it has python properties to access the ACCESSS_MODES and a list of CREATION_FLAGS
#  4. it prints the strace format out e.g "O_RDONLY|O_NONBLOCK|O_LARGEFILE"
#  5. Maybe we can have subtypes and implement __get_item__ to index by octal codes or string representation of enum values

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
#O_DIRECT	 040000	     16384
#O_LARGEFILE	 100000	     32768 
#O_DIRECTORY     200000      65536
#O_NOFOLLOW      400000     131072
#O_NOATIME	1000000     262144
#O_CLOEXEC 	2000000     524288

#FIXME: it would be nice to have bind a value to enum value (in this case
#we can use it to store de flag octal code)
ACCESS_MODES = Enum("O_RDONLY", "O_WRONLY", "O_RDWR")
CREATION_FLAGS = Enum("O_CREAT", "O_EXCL", "O_NOCTTY", "O_TRUNC", 
                         "O_APPEND", "O_NONBLOCK", "O_NDELAY", 
                         "O_SYNC", "O_FSYNC", "O_ASYNC",
#"O_DSYNC","O_RSYNC" O_NDELAY O_PRIV,
   	 		 "O_DIRECT", "O_LARGEFILE",
			 "O_DIRECTORY", "O_NOFOLLOW", 
			 "O_NOATIME", "O_CLOEXEC")
#"FNDELAY" #"FAPPEND" #"FMARK" #"FDEFER" #"FASYNC"
#"FSHLOCK" #"FEXLOCK" #"FCREAT" #"FTRUNC" #"FEXCL"
#"FNBIO" #"FSYNC" #"FNOCTTY" #O_SHLOCK" #"O_EXLOCK"

# if outside the range [0,3] is a programming error and the code should fail
__value2access_modes = {0:ACCESS_MODES.O_RDONLY, 1:ACCESS_MODES.O_WRONLY, 
                           2:ACCESS_MODES.O_RDWR, 3:None}

__value2creation_flags = {64:CREATION_FLAGS.O_CREAT, 128:CREATION_FLAGS.O_EXCL, 
                               256:CREATION_FLAGS.O_NOCTTY, 
                               512:CREATION_FLAGS.O_TRUNC,
                               1024:CREATION_FLAGS.O_APPEND, 
                               2048:CREATION_FLAGS.O_NONBLOCK, 
                               4096:CREATION_FLAGS.O_SYNC, 
                               8192:CREATION_FLAGS.O_ASYNC,
                               16384:CREATION_FLAGS.O_DIRECT,
                               32768:CREATION_FLAGS.O_LARGEFILE,
                               65536:CREATION_FLAGS.O_DIRECTORY,
                               131072:CREATION_FLAGS.O_NOFOLLOW,
                               262144:CREATION_FLAGS.O_NOATIME,
                               524288:CREATION_FLAGS.O_CLOEXEC}

""" from linux open flags to a human-friendly representation. 
http://linux.die.net/man/2/open
"""
def _access_mode_bits(flags_number):
    return flags_number & 3

def access_mode(flags_number):
    return __value2access_modes[_access_mode_bits(flags_number)]

def _creation_flags_bits(flags_number):
    return flags_number & ~3

def _match(flags_number, flag_code):#see flag codes in table above
    return (flags_number & flag_code) == flag_code

def creation_flags(flags_number):
    flags = []
    for (code, flag) in sorted(__value2creation_flags.items()):#strace requires order
        if _match(flags_number, code):
            flags.append(flag)
    return flags

""" 
Converts from an strace string e.g O_RDONLY|O_NONBLOCK|O_LARGEFILE to
its correspondent numeric code
"""
def flags_number(mode_and_flags):
    number = 0
    tokens = mode_and_flags.split("|")#what if we have just one flag ?
     #not efficient and ugly, but i'm late. What i really want is to 
     #to index an Enum based on the types we use to build it, so in
     #the case below I can do ACCESS_MODE[token]
    for (access_mode_code, access_mode) in __value2access_modes.iteritems():
        if str(access_mode) in tokens:
            number = number | access_mode_code

    for (creation_flag_code, creation_flag) in __value2creation_flags.iteritems():
        if str(creation_flag) in tokens:
            number = number | creation_flag_code

    return number

"""
Converts from the open syscall open_flags parameter to the strace string
"""
def mode_and_flags(flags_number):
    m_and_f = []
    m_and_f.append(str(access_mode(flags_number)))
    m_and_f.extend([str(flag) for flag in creation_flags(flags_number)])
    return "|".join(m_and_f)
