/**
 * Copyright (C) 2008 Universidade Federal de Campina Grande
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <stdlib.h>
#include <assert.h>
#include <fcntl.h>
#include <errno.h>

#include <poll.h>

#include "replayer.h"
#include "libnfs-glue.h"

//Below definitions are copied from linux/fs.h
//It seems my machine does not include this header. So, to avoid an error
//(I cannot ensure the machine that is going to run this code will include it
//or not) I will redefine instead of including linux/fs.h

#define ATTR_MODE       (1 << 0) //nfs_proc
#define ATTR_UID        (1 << 1) //nfs_proc
#define ATTR_GID        (1 << 2) //nfs_proc
#define ATTR_SIZE       (1 << 3) //nfs_proc
#define ATTR_ATIME      (1 << 4)
#define ATTR_MTIME      (1 << 5)
#define ATTR_CTIME      (1 << 6)
#define ATTR_ATIME_SET  (1 << 7) //nfs_proc
#define ATTR_MTIME_SET  (1 << 8) //nfs_proc
#define ATTR_FORCE      (1 << 9) // Not a change, but a change it
#define ATTR_ATTR_FLAG  (1 << 10)
#define ATTR_KILL_SUID  (1 << 11)
#define ATTR_KILL_SGID  (1 << 12)
#define ATTR_FILE       (1 << 13)
#define ATTR_KILL_PRIV  (1 << 14)
#define ATTR_OPEN       (1 << 15) //Truncating from open(O_TRUNC)
#define ATTR_TIMES_SET  (1 << 16)

/** from fs.h
struct iattr {
        unsigned int    ia_valid;
	umode_t         ia_mode;
	uid_t           ia_uid;
	gid_t           ia_gid;
	loff_t          ia_size;
	struct timespec ia_atime;
	struct timespec ia_mtime;
	struct timespec ia_ctime;
	struct file     *ia_file;
};*/

/** from libnfs-raw-nfs.h
struct SETATTR3args {
	nfs_fh3 object;
	sattr3 new_attributes;
	sattrguard3 guard;
}
struct sattr3 {
	set_mode3 mode;
	set_uid3 uid;
	set_gid3 gid;
	set_size3 size;
	set_atime atime;
	set_mtime mtime;
}*/

//FIXME: refactor later to be polimorfic with syscall_dispatch
int exec_nfs (struct replay_command* to_exec, int *exec_rvalue,
		struct replay* rpl, struct nfsio * con) {

    assert (to_exec != NULL);
    assert (rpl != NULL);
    Parms* args = to_exec->params;

    switch (to_exec->command) {
        case NFSD_PROC_FSSTAT_OP: {
	    *exec_rvalue = nfsio_fsstat (con);
	}
	break;
	case NFSD_PROC_SETATTR_OP: {

	    //TODO: check i_valid flag by calling chmod, chown in an mount point
	    int ia_valid;
	    int size;
	    ia_valid = args[1].argm->i_val;
	    size = args[2].argm->i_val;//FIXME: shouldn't be an offset_t ?

	    struct SETATTR3args sargs;
	    memset (&sargs, 0, sizeof (sargs));

	    //ligblue does not give much freedom to set mtime atime .. .
	    //and I think that an error when changing time is not so bad
	    //(it will load the server anyway). So I will keep this
	    //mtime.set_it at I saw in libglue.
	    sargs.new_attributes.mtime.set_it = SET_TO_SERVER_TIME;

	    //size
	    if (ia_valid & ATTR_SIZE) {
	    	sargs.new_attributes.size.set_it = TRUE;
	    	sargs.new_attributes.size.set_size3_u.size = size;
	    } else {
	    	sargs.new_attributes.size.set_it = FALSE;
	    }

	    //mode
	    if (ia_valid & ATTR_MODE) {
	        sargs.new_attributes.mode.set_it = TRUE;
	    } else {
	        sargs.new_attributes.mode.set_it = FALSE;
	    }

	    //uid, gid
	    if (ia_valid & ATTR_UID) {
	        sargs.new_attributes.uid.set_it = TRUE;
	    } else {
	        sargs.new_attributes.uid.set_it = FALSE;
	    }

	    if (ia_valid & ATTR_GID) {
	        sargs.new_attributes.gid.set_it = TRUE;
	    } else {
	        sargs.new_attributes.gid.set_it = FALSE;
	    }

	    fattr3 *attr;
	    attr = (fattr3*) malloc (sizeof (fattr3));
	    *exec_rvalue = nfsio_setattr2 (con, args[0].argm->cprt_val,
			    		   attr, &sargs);
	}
	break;
	case NFSD_PROC_GETATTR_OP: {
	    *exec_rvalue = nfsio_getattr (con, args[0].argm->cprt_val, NULL);
	}
	break;
	case NFSD_PROC_LOOKUP_OP: {
	    *exec_rvalue = nfsio_lookup (con, args[0].argm->cprt_val, NULL);
	}
	break;
	case NFSD_PROC_WRITE_OP: {

	    int offset, count, stable;

	    count = args[1].argm->i_val;
	    char * buf = (char*) malloc (count * sizeof(char));
	    offset = args[2].argm->i_val;
	    stable = args[3].argm->i_val;

            *exec_rvalue = nfsio_write (con, args[0].argm->cprt_val, buf,
			    		offset, count, stable);
	}
	break;
	case NFSD_PROC_READ_OP: {

	    int offset, count;

	    count = args[1].argm->i_val;
	    char * buf = (char*) malloc (count * sizeof(char));
	    offset = args[2].argm->i_val;

	    *exec_rvalue = nfsio_read (con, args[0].argm->cprt_val, buf,
			               offset, count);
	}
	break;
	case NFSD_PROC_RENAME_OP: {
	    *exec_rvalue = nfsio_rename (con, args[0].argm->cprt_val,
					 args[1].argm->cprt_val);
	}
	break;
	case NFSD_PROC_REMOVE_OP: {
	    *exec_rvalue = nfsio_remove (con, args[0].argm->cprt_val);
	}
        break;
	case NFSD_PROC_RMDIR_OP: {
	    *exec_rvalue = nfsio_rmdir (con, args[0].argm->cprt_val);
	}
	break;
	case NFSD_PROC_LINK_OP: {
	    *exec_rvalue = nfsio_link (con, args[0].argm->cprt_val,
			   	       args[1].argm->cprt_val);
	}
	break;
	case NFSD_PROC_SYMLINK_OP: {
	    *exec_rvalue = nfsio_symlink (con, args[0].argm->cprt_val,
				   	  args[1].argm->cprt_val);
	}
	break;
	case NFSD_PROC_READLINK_OP: {
	    //TODO:nfsio expose less args than nfs_readlink, does it matter ?
	    //*exec_rvalue = nfs_readlink (nfs, args[0].argm->cprt_val, buf, len);
	    int len = args[1].argm->i_val;
	    char * buf = (char*) malloc (len * sizeof(char));
	    *exec_rvalue = nfsio_readlink (con, args[0].argm->cprt_val);
	}
	break;
	case NFSD_PROC_READDIR_OP: {
	    //FIXME: nfsio ?
	    /**struct nfsdirent* rdirent = NULL;
 	    struct nfsdir* dirp = NULL;
	    if (nfs_opendir (nfs, args[0].argm->cprt_val, &dirp) < 0) {
		return -1;
	    }
	    rdirent = nfs_readdir (nfs, dirp);
	    if (rdirent) {
	        *exec_rvalue = 0;
	    } else {
	        return -1;
	    }*/
	   *exec_rvalue = -1;
	}
	break;
	case NFSD_PROC_READDIRPLUS_OP: {
            *exec_rvalue = nfsio_readdirplus (con, args[0].argm->cprt_val,
					      NULL, NULL);
	}
	break;
	case NFSD_PROC_ACCESS_OP: {
	    //TODO nfsio has more args the nfs_access how to match them ?
	    //*exec_rvalue = nfs_access (nfs, args[0].argm->cprt_val, args[0].argm->i_val);
	    //nfsio_access(struct nfsio *nfsio, const char *name, uint32_t desired, uint32_t *access)
	    *exec_rvalue = -1;
	}
	break;
	case NFSD_PROC_MKNOD_OP: {
	    //FIXME: it's not working; was returning an error code
	    int mode, dev;
	    mode = args[1].argm->i_val;
	    dev = args[2].argm->i_val;
	    //printf ("path=%s mode=%d dev=%d\n", args[0].argm->cprt_val, mode, dev);
            *exec_rvalue = nfs_mknod (con->nfs, args[0].argm->cprt_val, mode,
			    	      dev);
	}
	break;
	case NFSD_PROC_MKDIR_OP: {
	    *exec_rvalue = nfsio_mkdir (con, args[0].argm->cprt_val);
	}
	break;
	case NFSD_PROC_CREAT_OP: {
	    //TODO: nfsio_create exposes less args than nfs_creat. does it matter ?
            //*exec_rvalue = nfs_creat (nfs, args[0].argm->cprt_val, args[1].argm->i_val, &fh);
            *exec_rvalue = nfsio_create (con, args[0].argm->cprt_val);
	}
	break;
	case NFSD_PROC_COMMIT_OP: {
	    *exec_rvalue = nfsio_commit (con, args[0].argm->cprt_val);
	}
	break;
	default: {
	    return -1;
	}
	break;
    }

   return 0;
}
