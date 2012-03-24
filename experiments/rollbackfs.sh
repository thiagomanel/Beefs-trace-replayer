#!/bin/bash

DESTPATH=/local/nfs_manel
BACKUPPATH=/local/backup_nfs_manel

rsync -progtl --delete $BACKUPPATH/* $DESTPATH/
