import sys

if __name__ == "__main__":
    """
       Pre-replay discovery script uses client side paths.
       We run proper stage-in at server side, so we need to translate paths to
       server side layout.

       For example, discovery scripts give us: 
           /local/thiagoepdc/espadarte_nfs//home/heitor/.cache/google-chrome/Default/Cache
       where /local/thiagoepdc/espadarte_nfs//home/ is the client mount point

       If the remote exported dir is /local/nfs_manel/, we translate above path to 
           /local/nfs_manel/heitor/.cache/google-chrome/Default/Cache

       Usage: python translate_to_serverside_paths.py server_exported_dir < original_prereplay_data > translate.data
    """
    exported_dir = sys.argv[1]
    sep = "/home"
    for line in sys.stdin:
        translate_line = line[line.find(sep) + len(sep):]
        sys.stdout.write("<path=" +exported_dir + translate_line)
