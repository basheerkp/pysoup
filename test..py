import multiprocessing

from limetorrent import getItemsLimeTorrents
from torrentgalaxy import getItemsTorrentGalaxy

queue1 = multiprocessing.Queue()
queue2 = multiprocessing.Queue()

process1 = multiprocessing.Process(target=getItemsLimeTorrents, args=["boys dub", queue1])
process2 = multiprocessing.Process(target=getItemsTorrentGalaxy, args=["boys", queue2])

process1.start()
process2.start()

process1.join()
process2.join()

results1 = queue1.get()
results2 = queue2.get()

print(results2)
print(results1)
