# -*- coding:utf-8 -*-

import Queue
import sys
import threading
from time import sleep
import StringIO
import traceback

reload(sys)
sys.setdefaultencoding("utf8")

class Threadpool:
    def __init__(self,numThreads):
        self.threads = []
        self.resizeLock =  threading.Condition(threading.Lock())
        self.taskLock = threading.Condition(threading.Lock())
        self.tasks = []
        self.isJoining = False
        self.setThreadCount(numThreads)

    def setThreadCount(self,newNumThreads):
        if self.isJoining:
            return False
        self.resizeLock.acquire()
        try:
            self.setThreadCountNolock(newNumThreads)
        finally:
            self.resizeLock.release()
        return True

    def setThreadCountNolock(self,newNumThreads):
        while newNumThreads > len(self.threads):
            newThread =  ThreadPoolThread(self)
            self.threads.append(newThread)
            newThread.start()

        while newNumThreads < len(self.threads):
            self.threads[0].goAway()
            del self.threads[0]


    def getThreadCount(self):

        self.resizeLock.acquire()
        try:
            return len(self.threads)
        finally:
            self.resizeLock.release()


    def queueTask(self,task,args=None, taskCallback=None):

        if self.isJoining == True:
            return  False

        if not callable(task):
            return False
        self.taskLock.acquire()
        try:
            self.tasks.append((task,args,taskCallback))
            print "append success"
            return True
        finally:
            self.taskLock.release()

    def getNextTask(self):
        self.taskLock.acquire()
        try:
            if self.tasks == []:
                return (None,None,None)
            else:
                print "pop 0"
                return self.tasks.pop(0)
        finally:
            self.taskLock.release()

    def joinAll(self,waitForTasks = True, waitForThreads = True):
        self.isJoining = True
        if waitForTasks:
            while self.tasks != []:
                sleep(.1)
        self.resizeLock.acquire()
        try:
            self.setThreadCountNolock(0)
            self.isJoining = True

            if waitForThreads:
                for t in self.threads:
                    t.join()
                    del t

            self.isJoining = False

        finally:
            self.resizeLock.release()

class ThreadPoolThread(threading.Thread):

    threadSleepTime = 0.1

    def __init__(self,pool):
        threading.Thread.__init__(self)
        self.__pool= pool
        self.__isDying = False

    def run(self):
        print "begin run"
        while self.__isDying == False:
            cmd, args , callback = self.__pool.getNextTask()
            if cmd is None:
                sleep(ThreadPoolThread.threadSleepTime)
            elif callback is None:
                cmd(args)
            else:
                callback(cmd(args))
    def goAway(self):
        self.__isDying = True













