#!/usr/bin/python
#
# Updates the packages, then works with runner2.py to rebuild updated packages
#
##############################################################

from multiprocessing.managers import BaseManager
from collections import deque
import queue
import os
import subprocess
import time

PWD = subprocess.run(["pwd"], stdout=subprocess.PIPE, universal_newlines=True).stdout
queue = queue.Queue()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
m.connect()
queue = m.get_queue()

class Prgram(object):
    def __init__(self, p_type: str, p_name: str, p_ver: str):
        self.p_type = p_type
        self.p_name = p_name
        self.p_ver = p_ver
        

def get_name_and_version(pkg_full_name: str):
        minus_dashes = pkg_full_name.split("-")
        s_name = minus_dashes[0]
        s_ver = ""
        first_digit = True
        for i in range(1, len(minus_dashes)):
            if(not minus_dashes[i][0].isdigit()):
                s_name += "-" + minus_dashes[i]
            else:
                if(first_digit):
                    s_ver = minus_dashes[i]
                    first_digit = False
                else:
                    s_ver += "-" + minus_dashes[i]
        return s_name, s_ver

pkg_list = subprocess.run(["pacman", "-Syuv", "--print"], stdout=subprocess.PIPE, universal_newlines=True).stdout
subprocess.run(["pacman", "-Syuv", "--noconfirm"], universal_newlines=True)
pkgs = deque()
for pkg in pkg_list.split("\n"):
    if("pkg.tar.xz" in pkg):
        name_and_version = pkg.split("/x86_64/")[1].split("-x86_64.pkg.tar.xz")[0].split("-any.pkg.tar.xz")[0] #Should probably use the python formatter here
        s_name, s_version = get_name_and_version(name_and_version)
        s_type = "update"
        print(s_name + ":" + s_version)
        if("local" not in s_type and "linux" not in s_name):  #Don't build stull from the AUR or the Kernel
            pkgs.append(Prgram(s_type, s_name, s_version))

my_dir_name = ""
while True:
    c_pkg = pkgs.popleft()
    queue.put(c_pkg.p_name)
    time.sleep(1)
    build_return_val = queue.get()
    if(build_return_val == 0):
        my_dir_name = queue.get()  # get folder name
        os.chdir(PWD + "/" + my_dir_name)
        built_pkgs = subprocess.run(["ls"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split(None)
        rmpkglst = []
        for b_pkg in built_pkgs:
            if(".pkg.tar.xz" in b_pkg):
                subprocess.run(["pacman", "-Uv", "--noconfirm", b_pkg], universal_newlines=True)
                name = b_pkg.split("-" + c_pkg.p_ver)[0]
                for i_pkg in pkgs:
                    if(i_pkg.p_name == name and i_pkg not in rmpkglst):
                        rmpkglst.append(i_pkg)
        for rmpkg in rmpkglst:
            pkgs.remove(rmpkg)
        os.chdir(PWD)
        queue.put("advance")
        time.sleep(1)
