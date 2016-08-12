#!/usr/bin/python
#
#
#
# Build embedded List
#
#
##################################################




pkg_list = "libcups:2.1.4-2 fontconfig:2.12.1-1 openjpeg2:2.1.1-2 libinput:1.4.1-1 poppler:0.46.0-2 cups-filters:1.10.0-2 cups:2.1.4-2 fakeroot:1.21-2 glew:2.0.0-1 gtk-update-icon-cache:3.20.8-1 gtk3:3.20.8-1 gvfs:1.28.2+22+g6c1124d-1 hugin:2016.0.0-4 inetutils:1.9.4-4 libnm-glib:1.2.4-1 libreoffice-fresh:5.2.0-2 libsynctex:2016.41290-4 mesa-demos:8.3.0-2 net-tools:1.60.20160710git-1 networkmanager:1.2.4-1 poppler-glib:0.46.0-2 poppler-qt4:0.46.0-2 poppler-qt5:0.46.0-2 python-setuptools:1:25.1.5-1 python2-setuptools:1:25.1.5-1 texlive-bin:2016.41290-4 texlive-fontsextra:2016.41439-2 texlive-formatsextra:2016.41438-2 texlive-games:2016.39318-2 texlive-genericextra:2016.41413-2 texlive-htmlxml:2016.41440-2 vte:0.28.2-8 xf86-video-intel:1:2.99.917+691+ga77397a-1"

import subprocess
from collections import deque
import os
import socket
from multiprocessing.managers import BaseManager
import queue
import time

f = open("failed4.txt", "w")
queue = queue.Queue()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
m.connect()
queue = m.get_queue()

PWD = subprocess.run(["pwd"], stdout=subprocess.PIPE, universal_newlines=True).stdout.strip("\n")

pkgs = deque()
my_dir_name = ""
for pkg in pkg_list.split(" "):
        name_and_version = pkg.split(":")
        s_type = "arch"
        if("linux" not in name_and_version[0]):  #Don't build stull from the AUR or the Kernel
            pkgs.append(name_and_version[0])
while(True):
    cur_pkg = pkgs.popleft()
    subprocess.run(["yaourt", "-G", cur_pkg])
    built_pkgs = subprocess.run(["ls", "-l"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split("\n")
    for build_pkg in built_pkgs:
        if("drwxr-xr-x" in build_pkg):
            my_dir_name = build_pkg.split(None)[8]
            os.chdir(PWD + "/" + my_dir_name)
            break
    for cat_file_line in subprocess.run(["cat", "PKGBUILD"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split("\n"):
        if("pkgname" in cat_file_line):
            if("(" in cat_file_line):
                pkg_names = cat_file_line.split("(")[1].strip(")").split(" ")
                for ind_pkg in pkg_names:
                    rmpkg = ind_pkg.strip("'")
                    if(rmpkg in pkgs):
                        pkgs.remove(rmpkg)
            else:
                rmpkg = cat_file_line.split("=")[1].strip("'")
                if(rmpkg in pkgs):
                    pkgs.remove(rmpkg)
            break
    build_results = subprocess.run(["makepkg"])
    if(build_results.returncode == 0):
        queue.put(my_dir_name)
        time.sleep(1)
        queue.get()  # Wait for install to finish
        os.chdir(PWD)
    else:
        os.chdir(PWD)
        f.write(cur_pkg + "\n")
    subprocess.run(["rm", "-Rf", my_dir_name], universal_newlines=True)
    
f.close()
queue.close_all()
            
        
        


