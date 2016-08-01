#!/usr/bin/python
#
# Serves messages between the runner and installer
#
#######################################################3

from multiprocessing.managers import BaseManager
import queue
queue = queue.Queue()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
s = m.get_server()
s.serve_forever()
