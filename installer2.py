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

PWD = subprocess.run(["pwd"], stdout=subprocess.PIPE, universal_newlines=True).stdout.strip("\n")
queue = queue.Queue()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
m.connect()
queue = m.get_queue()


def get_name(pkg: str):
    if("/x86_64/" in pkg):
        pkg = pkg.split("/x86_64/")[1]
    name_and_version = pkg.split("-x86_64.pkg.tar.xz")[0].split("-any.pkg.tar.xz")[0]
    minus_dashes = name_and_version.split("-")
    s_name = minus_dashes[0]
    s_ver = ""
    first_digit = True
    for i in range(1, len(minus_dashes)):
        if(not minus_dashes[i][0].isdigit()):
            s_name += "-" + minus_dashes[i]
        else:
            break
    return s_name

pkg_list = subprocess.run(["pacman", "-Syuv", "--print"], stdout=subprocess.PIPE, universal_newlines=True).stdout
subprocess.run(["pacman", "-Syuv", "--noconfirm"], universal_newlines=True)
pkgs = deque()
for pkg in pkg_list.split("\n"):
    if("pkg.tar.xz" in pkg):
        s_name = get_name(pkg)
        print(s_name)
        if("linux-atm" in s_name):  #white-list goes here
            pkgs.append(s_name)
        else:
            if("linux" not in s_name):  #black-list goes here
                pkgs.append(s_name)

my_dir_name = ""
while True:
    c_pkg = pkgs.popleft()
    queue.put(str(c_pkg))
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
                name = get_name(pkg)
                if(name not in pkgs and name not in rmpkglst):
                    rmpkglst.append(i_pkg)
        for rmpkg in rmpkglst:
            pkgs.remove(rmpkg)
        os.chdir(PWD)
        queue.put("advance")
        time.sleep(1)
