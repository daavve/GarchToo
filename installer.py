#!/usr/bin/python
#
# Runs install program according to instructions from runner
#
##############################################################

from multiprocessing.managers import BaseManager
import queue
import os
import subprocess

PWD = "/home/dave/projects/archtoo.gny"
queue = queue.Queue()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
m.connect()
queue = m.get_queue()
while True:
    got = queue.get()
    os.chdir(PWD + "/" + got)
    packages = subprocess.run(["ls"], stdout=subprocess.PIPE, universal_newlines=True).stdout.split(None)
    for package in packages:
        if(".pkg.tar.xz" in package):
            subprocess.run(["pacman", "-Uv", "--noconfirm", package], universal_newlines=True)
    os.chdir(PWD)
    queue.put("advance") #tells the other process to stop waiting
    
