#!/usr/bin/python
#
#
#
# Build embedded List
#
#
##################################################




pkg_list = "linux-api-headers:4.7-1 glibc:2.24-1 alsa-lib:1.1.2-1 binutils:2.26.1-2 gcc-libs:6.1.1-4 device-mapper:2.02.162-1 dhcpcd:6.11.2-1 findutils:4.6.0-2 gawk:4.1.3-2 gcc:6.1.1-4 gcc-ada:6.1.1-4 gcc-fortran:6.1.1-4 gcc-go:6.1.1-4 gcc-objc:6.1.1-4 libksba:1.3.4-2 gpgme:1.6.0-3 groff:1.22.3-7 gtk-update-icon-cache:3.20.6-2 mesa:12.0.1-6 mesa-libgl:12.0.1-6 gtk3:3.20.6-2 guile:2.0.12-1 jre7-openjdk-headless:7.u111_2.6.7-1 jre7-openjdk:7.u111_2.6.7-1 jdk7-openjdk:7.u111_2.6.7-1 libnl:3.2.28-1 libsynctex:2016.41290-2.1 lvm2:2.02.162-1 pacman-mirrorlist:20160802-1 python-beautifulsoup4:4.5.1-1 qt5-base:5.7.0-2 python-matplotlib:1.5.2-1 python-setuptools:1:25.1.3-1 python2-setuptools:1:25.1.3-1 strace:4.13-1 tcl:8.6.6-1 texlive-bin:2016.41290-2.1 texlive-latexextra:2016.41473-2 texlive-pictures:2016.41299-2 tk:8.6.6-1 valgrind:3.11.0-4"


import subprocess
from collections import deque
import os
import socket
from multiprocessing.managers import BaseManager
import queue
import time

f = open("failed2.txt", "w")
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
        time.sleep(1) # Don't eat your own message
        queue.get()  # Wait for install to finish
        os.chdir(PWD)
    else:
        os.chdir(PWD)
        f.write(cur_pkg + "\n")
    subprocess.run(["rm", "-Rf", my_dir_name], universal_newlines=True)
    
f.close()
queue.close_all()
            
        
        


