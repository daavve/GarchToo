#!/usr/bin/python
#
# Worker script.  performs the actual building -- Version that does updating, does not update aur stuff
#
##################################################################################################################################

import subprocess
from collections import deque
import os
import socket
from multiprocessing.managers import BaseManager
import queue
import time

f = open("failed8update.txt", "w")
queue = queue.Queue()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
m.connect()
qu = m.get_queue()

PWD = subprocess.run(["pwd"], stdout=subprocess.PIPE, universal_newlines=True).stdout.strip("\n")


while(True):
    my_tdir_name = ""
    cur_pkg = qu.get()
    subprocess.run(["yaourt", "-G", cur_pkg], universal_newlines=True)
    built_pkgs = subprocess.run(["ls", "-l"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split("\n")
    for build_pkg in built_pkgs:
        if("drwxr-xr-x" in build_pkg):
            my_dir_name = build_pkg.split(None)[8]
            os.chdir(PWD + "/" + my_dir_name)
    build_results = subprocess.run(["makepkg"], universal_newlines=True)
    os.chdir(PWD)
    qu.put(build_results.returncode)
    time.sleep(1)
    if(build_results.returncode == 0):
        qu.put(str(my_dir_name))
        time.sleep(1)
        qu.get() # Wait for update to finish
    else:
        f.write(cur_pkg + "\n")
    subprocess.run(["rm", "-Rf", my_dir_name], universal_newlines=True)
    
f.close()

            
        
        


