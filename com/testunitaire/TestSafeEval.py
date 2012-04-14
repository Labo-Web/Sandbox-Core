'''
Created on 5 avr. 2012

@author: damienp
'''
from com.exception.safe_eval_exception import SafeEvalException
from com.safeexecution.SafeEvalVisitor import safe_eval
import time
import unittest

class TestSafeEval(unittest.TestCase):
    def test_builtin(self):
        # attempt to access a unsafe builtin
        self.assertRaises(SafeEvalException,
            safe_eval, "open('test.txt', 'w')")
        print 1

    def test_getattr(self):
        # attempt to get arround direct attr access
        self.assertRaises(SafeEvalException, \
            safe_eval, "getattr(int, '__abs__')")
        print 2

    def test_func_globals(self):
        # attempt to access global enviroment where fun was defined
        self.assertRaises(SafeEvalException, \
            safe_eval, "def x(): pass; print x.func_globals")
        print 3

    def test_lowlevel(self):
        # lowlevel tricks to access 'object'
        self.assertRaises(SafeEvalException, \
            safe_eval, "().__class__.mro()[1].__subclasses__()")
        print 4

    def test_timeout_ok(self):
        # attempt to exectute 'slow' code which finishes within timelimit
        def test():time.sleep(2)
        env = {'test':test}
        safe_eval("test()", env, timeout_secs = 5)
        print 5

    def test_timeout_exceed(self):
        # attempt to exectute code which never teminates
        self.assertRaises(SafeEvalException, \
            safe_eval, "while 1: pass")
        print 6

    def test_invalid_context(self):
        # can't pass an enviroment with modules or builtins
        env = {'f' : __builtins__['open'], 'g' : time}
        self.assertRaises(SafeEvalException, \
            safe_eval, "print 1", env)
        print 7

    def test_callback(self):
        # modify local variable via callback
        self.value = 0
        def test():self.value =1
        env = {'test':test}
        safe_eval("test()", env)
        self.assertEqual(self.value, 1)
        print 8
        
    def test_code(self):
    
        x = {'x':2}
        env = {'x':x}
        safe_eval('''
value = 1 
x['x'] = value + x['x']
print str(x)+ " <- TA MERE"
''', env)
        
        self.assertEqual(x['x'], 3)
        print 9