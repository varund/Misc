#curl http://dilbert.com/strip/1992-07-28 | grep 'img-comic' | awk -F'"' '{print $10}' | tail -n 1 > img.txt
import pycurl
import Queue
from StringIO import StringIO
from datetime import timedelta, date, datetime
import threading
from optparse import OptionParser

class GetImg (threading.Thread):
    def __init__(self, que):
        super(GetImg, self).__init__()
        self.que = que

    def getImgUrl(self, url):
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        buffer = StringIO()
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        val = buffer.getvalue()
        arr = val.split("\n")
        for line in arr:
            if line is not None and line.find("img-comic\"") > 0:
                urltags = line.split("\"")
                return urltags[9]

    def writeToFile(self, url, path):
        with open(path, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            c.perform()
            c.close()

    def run(self):
        print "Start!"
        while (not self.que.empty()):
            dt = self.que.get()
            print "Processing: %s" %dt
            url= self.getImgUrl("http://dilbert.com/strip/%s" %dt)
            self.writeToFile(url, "./%s.jpg" % dt)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)



if __name__ == "__main__":
    q = Queue.Queue()
    parser = OptionParser(usage="usage: %prog [options] filename",version="%prog 1.0")
    parser.add_option("-s", "--start", dest="start")
    parser.add_option("-e", "--end", dest="end")

    (options, args) = parser.parse_args()
    if options.start is None or options.end is None:
        parser.error("Use -s & -e")
    start = options.start
    end = options.end
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    for single_date in daterange(start_date, end_date):
        q.put(single_date.strftime("%Y-%m-%d"))

    print "Dates: %s" %q

    workers = []
    for i in range(1,10):
        worker = GetImg(q)
        workers.append(worker)

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()
