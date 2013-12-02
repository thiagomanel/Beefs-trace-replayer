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

#include <nfsc/libnfs.h>
#include <nfsc/libnfs-raw.h>
#include <nfsc/libnfs-raw-nfs.h>
#include <nfsc/libnfs-raw-nlm.h>

#include "replayer.h"

//FIXME: refactor later to be polimorfic with syscall_dispatch
int exec_nfs (struct replay_command* to_exec, int *exec_rvalue,
		struct replay* rpl, struct nfs_context *nfs) {

    assert (to_exec != NULL);
    assert (rpl != NULL);
    assert (nfs != NULL);
    Parms* args = to_exec->params;

    switch (to_exec->command) {
        case NFSD_PROC_FSSTAT_OP: {
	    //TODO maybe only with async
	}
	break;
	case NFSD_PROC_SETATTR_OP: {
	    //TODO maybe only with async
	}
	break;
	case NFSD_PROC_GETATTR_OP: {
	    //TODO maybe only with async
	}
	break;
	case NFSD_PROC_LOOKUP_OP: {
	    //FIXME: maybe only with async
	}
	break;
	case NFSD_PROC_WRITE_OP: {

	    int offset, count, open_ret;
	    struct nfsfh* wfh = NULL;

	    if ( (open_ret = nfs_open (nfs, args[0].argm->cprt_val, O_RDWR,
					&wfh)) < 0) {
		return open_ret;
	    }

	    count = args[1].argm->i_val;
	    char * buf = (char*) malloc (count * sizeof(char));
	    offset = args[2].argm->i_val;

            *exec_rvalue = nfs_pwrite (nfs, wfh, offset, count, buf);
	}
	break;
	case NFSD_PROC_READ_OP: {

	    int offset, count;
	    struct nfsfh* rfh = NULL;

	    if (nfs_open (nfs, args[0].argm->cprt_val, O_RDONLY, &rfh) < 0) {
		return -1;
	    }

	    count = args[1].argm->i_val;
	    char * buf = (char*) malloc (count * sizeof(char));
	    offset = args[2].argm->i_val;

            *exec_rvalue = nfs_pread (nfs, rfh, offset, count, buf);
	}
	break;
	case NFSD_PROC_RENAME_OP: {

	    *exec_rvalue = nfs_rename (nfs, args[0].argm->cprt_val,
					    args[1].argm->cprt_val);
	}
	break;
	case NFSD_PROC_REMOVE_OP: {
	    //TODO: maybe only using async calls
	}
        break;
	case NFSD_PROC_RMDIR_OP: {

	    *exec_rvalue = nfs_rmdir (nfs, args[0].argm->cprt_val);
	}
	break;
	case NFSD_PROC_LINK_OP: {

	    *exec_rvalue = nfs_link (nfs, args[0].argm->cprt_val,
				   	  args[1].argm->cprt_val);
	}
	break;
	case NFSD_PROC_SYMLINK_OP: {

	    *exec_rvalue = nfs_symlink (nfs, args[0].argm->cprt_val,
				   	     args[1].argm->cprt_val);
	}
	break;
	case NFSD_PROC_READLINK_OP: {

	    int len = args[1].argm->i_val;
	    char * buf = (char*) malloc (len * sizeof(char));

	    *exec_rvalue = nfs_readlink (nfs, args[0].argm->cprt_val, buf, len);
	}
	break;
	case NFSD_PROC_READDIR_OP: {

	    struct nfsdirent* rdirent = NULL;
 	    struct nfsdir* dirp = NULL;
	    if (nfs_opendir (nfs, args[0].argm->cprt_val, &dirp) < 0) {
		return -1;
	    }
	    rdirent = nfs_readdir (nfs, dirp);
	    if (rdirent) {
	        *exec_rvalue = 0;
	    } else {
	        return -1;
	    }
	}
	break;
	case NFSD_PROC_READDIRPLUS_OP: {
	    //TODO maybe only in async calls
	}
	break;
	case NFSD_PROC_ACCESS_OP: {

	    *exec_rvalue = nfs_access (nfs, args[0].argm->cprt_val,
			    	     args[0].argm->i_val);
	}
	break;
	case NFSD_PROC_MKNOD_OP: {
	    //FIXME: it's not working; was returning an error code
	    int mode, dev;
	    mode = args[1].argm->i_val;
	    dev = args[2].argm->i_val;

	    printf ("path=%s mode=%d dev=%d\n", args[0].argm->cprt_val, mode, dev);
            *exec_rvalue = nfs_mknod (nfs, args[0].argm->cprt_val, mode, dev);
	}
	break;
	case NFSD_PROC_MKDIR_OP: {

	    *exec_rvalue = nfs_mkdir (nfs, args[0].argm->cprt_val);
	}
	break;
	case NFSD_PROC_CREAT_OP: {

	    struct nfsfh* fh = NULL;
            *exec_rvalue = nfs_creat (nfs, args[0].argm->cprt_val,
			       		args[1].argm->i_val, &fh);
	}
	break;
	case NFSD_PROC_COMMIT_OP: {
	    //TODO maybe only using async calls
	}
	break;
	default: {
	    return -1;
	}
	break;
    }

   return 0;
}
