# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import time
import re
import urllib2
import threading


def findkeyword(url, key, mode):
    url_base = 'http://eecs.pku.edu.cn'
    res = []
    req = urllib2.Request(url)
    try:
        con = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print 'Error code: ', e.code
    except urllib2.URLError, e:
        print 'Error code: ', e.code
    else:
        docc = con.read()
        mutex.acquire()
        if url not in track and key in docc:
            #tagtitle(url, key)
            track.append(url)
            tagtest(docc, key)
        mutex.release()
        if mode == 0 and 'P_Page' in docc:
            ssoup = BeautifulSoup(docc)
            for col in ssoup.findAll('select',id = 'P_Page'):
                for item in col.findAll('option'):
                    url_add = item.get('value').strip()
                    url_new = url_base + url_add
                    if url_new not in track:
                        res.append(url_new)
                    '''
                    req = urllib2.Request(url_new)
                    try:
                        con = urllib2.urlopen(req)
                    except urllib2.HTTPError, e:
                        print 'Error code: ', e.code
                    except urllib2.URLError, e:
                        print 'Error code: ', e.code
                    else:
                        docc = con.read()
                        if key in docc and url_new not in res:
                            #tagtitle(url_new,key)
                            tagtest(docc,key)
                            res.append(url_new)
                    '''
    return res

def tagtitle(url, key):
    url_base = 'http://eecs.pku.edu.cn'
    req = urllib2.Request(url)
    try:
        con = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print 'Error code: ', e.code
    except urllib2.URLError, e:
        print 'Error code: ', e.code
    else:
        docc = con.read()
        ssoup = BeautifulSoup(docc)
        key_string = re.compile('.*'+key+'.*')
        for it in ssoup.findAll('span', {'class':'article_title'}):
            if key in it.getText().encode('utf-8'):
                parent = it.findParent()
                print(it.getText().encode('utf-8')+" "*5+parent.find('span',{'class':'article_date'}).getText().encode('utf-8'))
                print(url_base+parent.find('a').get('href'))
                print("="*70)

def tagtest(docc, key):
    global cnt
    url_base = 'http://eecs.pku.edu.cn'
    ssoup = BeautifulSoup(docc)
    key_string = re.compile('.*'+key+'.*')
    for it in ssoup.findAll('span', {'class':'article_title'}):
        if key in it.getText().encode('utf-8'):
            parent = it.findParent()
            print(it.getText().encode('utf-8')+" "*5+parent.find('span',{'class':'article_date'}).getText().encode('utf-8'))
            print(url_base+parent.find('a').get('href'))
            print("="*70)
            cnt += 1

class CrawlerThread(threading.Thread):
    def __init__(self,url,key,tid,mode):
        threading.Thread.__init__(self)
        self.url = url
        self.key = key
        self.tid = tid
        self.mode = mode
    def run(self):
        global mutex
        global queue
        global track
        if self.mode == 0:
            ans = findkeyword(self.url, self.key, 0)
            mutex.acquire()
            track.append(self.url)
            tagque.extend(ans)
            mutex.release()
        else:
            findkeyword(self.url, self.key, 1)
            mutex.acquire()
            track.append(self.url)
            mutex.release()



url = 'http://eecs.pku.edu.cn'
key = '优秀'
threadnum = 150
mutex = threading.Condition()

start = time.time()

req = urllib2.Request(url)
con = urllib2.urlopen(req)
doc = con.read()
con.close()
track = []
queue = []
tagque = []
cnt = 0
soup = BeautifulSoup(doc)


for link in soup.findAll('a'):
    link_name = link.get('href').strip()
    if 'index' not in link_name:
        continue
    else:
        if link_name[0] == '/':
            link_url = url + link_name
        else:
            link_url = url + '/' +link_name
        if link_url in track:
            continue
        queue.append(link_url)
print("start parsing One")

threadpool = []
i = 0

while i < len(queue):
    j = 0
    while j<threadnum and i+j < len(queue):
        lthread = CrawlerThread(queue[i+j], key, j, 0)
        threadpool.append(lthread)
        lthread.start()
        #if threadresult!=None:
        #   print 'Thread started:',i+j
        j += 1
    i += j
    for thread in threadpool:
        thread.join(30)
    threadpool = []

print("start parsing Two")
threadpool = []
queue = list(set(tagque)-set(track))

i = 0
while i < len(queue):
    j = 0
    while j<threadnum and i+j < len(queue):
        rthread = CrawlerThread(queue[i+j], key, j, 1)
        threadpool.append(rthread)
        rthread.start()
        #if threadresult!=None:
        #   print 'Thread started:',i+j
        j += 1
    i += j
    for thread in threadpool:
        thread.join(30)
    threadpool = []
print('run span:',time.time()-start)
print('total news:',cnt)
#tagtitle('http://eecs.pku.edu.cn/index.aspx?menuid=4&type=article&lanmuid=64&page=10&language=cn','表彰')