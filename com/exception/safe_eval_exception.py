'''
Created on 5 avr. 2012

@author: damienp
'''

class SafeEvalException(Exception):
    "Base class for all safe-eval related errors."
    pass

class SafeEvalExecException(SafeEvalException):
    """
    Exception class for reporting all errors which occured while
    validating AST for source code in safe_eval().

    Attributes:
      errors = encapsulation of the error
    """
    def __init__(self, errors):
        self.errors = errors
        
    def __str__(self):
        return '\n'.join([str(err) for err in self.errors])

class SafeEvalCodeException(SafeEvalException):
    """
    Exception class for reporting all errors which occured while
    validating AST for source code in safe_eval().

    Attributes:
      code   = raw source code which failed to validate
      errors = list of SafeEvalError
    """
    def __init__(self, code, errors):
        self.code, self.errors = code, errors
        
    def __str__(self):
        return '\n'.join([str(err) for err in self.errors])


class SafeEvalContextException(SafeEvalException):
    """
    Exception class for reporting unallowed objects found in the dict
    intended to be used as the local enviroment in safe_eval().

    Attributes:
      keys   = list of keys of the unallowed objects
      errors = list of strings describing the nature of the error
               for each key in 'keys'
    """
    def __init__(self, keys, errors):
        self.keys, self.errors = keys, errors
    def __str__(self):
        return '\n'.join([str(err) for err in self.errors])
        
class SafeEvalTimeoutException(SafeEvalException):
    """
    Exception class for reporting that code evaluation execeeded
    the given timelimit.

    Attributes:
      timeout = time limit in seconds
    """
    def __init__(self, timeout):
        self.timeout = timeout
    def __str__(self):
        return "Timeout limit execeeded (%s secs) during exec" % self.timeout
