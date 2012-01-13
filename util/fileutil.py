from enum import Enum

access_modes = Enum("O_RDONLY", "O_NONBLOCK", "O_LARGEFILE")

#O_ACCMODE	   0003
#O_RDONLY	     00
#O_WRONLY	     01
#O_RDWR		     02

#O_CREAT	   0100
#O_EXCL		   0200
#O_NOCTTY	   0400
#O_TRUNC	  01000
#O_APPEND	  02000
#O_NONBLOCK	  04000
#O_NDELAY    O_NONBLOCK
#O_SYNC		 010000
#O_FSYNC	 O_SYNC
#O_ASYNC	 020000

""" 
   conversion from linux open_mode to its string representation.
   see http://linux.die.net/man/2/open
"""
def access_mode(flags):
    return [access_modes.O_RDONLY, access_modes.O_NONBLOCK, access_modes.O_LARGEFILE]
