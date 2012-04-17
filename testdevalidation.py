'''
Created on 17 avr. 2012

@author: damienp
'''
from com.safeexecution.SafeEvalVisitor import safe_eval
import Queue
import threading

class TestDeValidation(object):
    '''
    classdocs
    '''


    def __init__(self, code, environment, time_out):
        self.code = code
        self.environment = []
        self.environment = environment
        self.time_out = time_out
        self.Queue = Queue.Queue()
        self.TTest = threading.Thread(target=safe_eval, args=(self.Queue, self.code,self.environment, self.time_out))

    
    def TTestRun(self):
       self.TTest.start()
       self.Check()
       print "c'est fini"
   
    def Check(self):
        while self.TTest.isAlive():
            func_value = self.Queue.get()
            print func_value
    