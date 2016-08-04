#!/usr/bin/python
#
# Worker script.  performs the actual building
#
##################################################################################################################################

import subprocess
from collections import deque
import os
import socket
from multiprocessing.managers import BaseManager
import queue

f = open("failed.txt", "w")
queue = queue.Queue()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
m.connect()
queue = m.get_queue()

PWD = subprocess.run(["pwd"], stdout=subprocess.PIPE, universal_newlines=True).stdout.strip("\n")


class Prgram(object):
    def __init__(self, p_type: str, p_name: str, p_ver: str):
        self.p_type = p_type
        self.p_name = p_name
        self.p_ver = p_ver

pkg_list = subprocess.run(["yaourt", "-Q"], stdout=subprocess.PIPE, universal_newlines=True).stdout
pkgs = deque()
my_dir_name = ""
for pkg in pkg_list.split("\n"):
    if("/" in pkg):
        s_pkg = pkg.split("/")
        s_type = s_pkg[0]
        s_name_ver = s_pkg[1].split(" ")
        s_name = s_name_ver[0]
        s_ver  = s_name_ver[1]
        if("local" not in s_type and "linux" not in s_name):  #Don't build stull from the AUR or the Kernel
            pkgs.append(Prgram(s_type, s_name, s_ver))
while(True):
    cur_pkg = pkgs.popleft()
    subprocess.run(["yaourt", "-G", cur_pkg.p_name])
    built_pkgs = subprocess.run(["ls", "-l"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split("\n")
    for build_pkg in built_pkgs:
        if("drwxr-xr-x" in build_pkg):
            my_dir_name = build_pkg.split(None)[8]
            os.chdir(PWD + "/" + my_dir_name)
    build_results = subprocess.run(["makepkg"])
    if(build_results.returncode == 0):
        queue.put(my_dir_name)
        time.sleep(1)
        queue.get()  # Wait for install to finish
        built_pkgs = subprocess.run(["ls"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split(None)
        rmpkglst = []
        for b_pkg in built_pkgs:
            if(".pkg.tar.xz" in b_pkg):
                name = b_pkg.split("-" + cur_pkg.p_ver)[0]
                for i_pkg in pkgs:
                    if(i_pkg.p_name == name and i_pkg not in rmpkglst):
                        rmpkglst.append(i_pkg)
        for rmpkg in rmpkglst:
            pkgs.remove(rmpkg)
        os.chdir(PWD)
    else:
        os.chdir(PWD)
        f.write(cur_pkg.p_name + "\n")
    subprocess.run(["rm", "-Rf", my_dir_name], universal_newlines=True)
    
f.close()
queue.close_all()
            
        
        


