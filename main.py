# -*- coding:utf-8 -*-
import argparse
import requests
from bs4 import BeautifulSoup
from lxml import etree
import Queue
import Threadpool
import re,sys
from argparse import ArgumentDefaultsHelpFormatter
reload(sys)
sys.setdefaultencoding("utf8")

#parser = argparse.ArgumentParser(prog="Spider", description='parse arg', formatter_class=ArgumentDefaultsHelpFormatter)
#parser.add_argument('-u', dest='url', action='store', required=True, help='the begin url')
#parser.add_argument('-d', dest='depth', action='store', required=True, help='the search depth')
#parser.add_argument('-k', dest='keyword', action='store', required=True, help='the search keyword')

#url = parser.parse_args().url
#depth = parser.parse_args().depth
#keyword = parser.parse_args().keyword


url='http://yanghan.life/'
depth = 1
keyword = 'AI'


class ScanSpider:
    def __init__(self,url,depth,keyword):
        self.begin_url = url
        self.search_depth = depth
        self.keyword = keyword
        self.url_queue = Queue.Queue(maxsize=10000)
        self.url_queue.put(self.begin_url)
        self.result_url=[]
        self.childurl=[]
        self.pool = Threadpool.Threadpool(5)


    def getChildurl(self,url):
        links=[]
        page_source = requests.get(url,timeout=2).content
        soup = BeautifulSoup(page_source, 'html.parser')
        for i in soup.find_all('a'):
            try:
                if u'javascript' in i['href']:
                    continue
                if i['href'][0]==r'/':
                    i['href'] = url+i['href'][1:]
                links.append(i['href'])
            except:
                pass
        #print links
        #tree = etree.HTML(page_source)
        #links = tree.xpath("//a/@href")
        return links

    def scrawl(self):
        temp_url = self.url_queue.get()
        print "searching",temp_url
        try:
            page_source = requests.get(temp_url,timeout=2).content
            print "get source success"
            if keyword in page_source:
                self.result_url.append(temp_url)
            templist=self.getChildurl(temp_url)
            for each in templist:
                self.childurl.append(each)
        except:
            pass



    def run(self):
        dep=0
        while dep<=self.search_depth:
            self.childurl=[]
            print "depth",dep
            while not self.url_queue.empty():
                self.pool.queueTask(self.scrawl())
            dep=dep+1
            num = 0
            print len(self.childurl)
            for each in self.childurl:
                num=num+1
                print "in queue",num,each
                self.url_queue.put(each)
            print "in queue success"
        self.pool.joinAll()
        print self.result_url





sp = ScanSpider(url,depth,keyword)
sp.run()










