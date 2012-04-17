'''
Created on 12 avr. 2012

@author: damienp
'''
from com.exception.safe_eval_exception import SafeEvalTimeoutException, \
    SafeEvalContextException, SafeEvalCodeException, SafeEvalExecException
from com.helpers.helpers import Helpers
from com.safeexecution.SafeEvalError import SafeEvalBuiltinError, \
    SafeEvalAttrError, SafeEvalASTNodeError
from inspect import Traceback
import compiler
import inspect
import threading
import time
import traceback


#----------------------------------------------------------------------
# Restricted AST nodes & builtins.
#----------------------------------------------------------------------

# Deny evaluation of code if the AST contain any of the following nodes:
unallowed_ast_nodes = [
#   'Add', 'And',
#   'AssAttr', 'AssList', 'AssName', 'AssTuple',
#   'Assert', 'Assign', 'AugAssign',
    'Backquote',
#   'Bitand', 'Bitor', 'Bitxor', 'Break',
#   'CallFunc', 'Class', 'Compare', 'Const', 'Continue',
#   'Decorators', 'Dict', 'Discard', 'Div',
#   'Ellipsis', 'EmptyNode',
    'Exec',
#   'Expression', 'FloorDiv',
#   'For',
    'From',
#   'Function',
#   'GenExpr', 'GenExprFor', 'GenExprIf', 'GenExprInner',
#   'Getattr', 'Global', 'If',
    'Import',
#   'Invert',
#   'Keyword', 'Lambda', 'LeftShift',
#   'List', 'ListComp', 'ListCompFor', 'ListCompIf', 'Mod',
#   'Module',
#   'Mul', 'Name', 'Node', 'Not', 'Or', 'Pass', 'Power',
#   'Print', 'Printnl',
    'Raise',
#    'Return', 'RightShift', 'Slice', 'Sliceobj',
#   'Stmt', 'Sub', 'Subscript',
   'TryExcept', 'TryFinally',
#   'Tuple', 'UnaryAdd', 'UnarySub',
#   'While','Yield'
]

# Deny evaluation of code if it tries to access any of the following builtins:
unallowed_builtins = [
    '__import__',
#   'abs', 'apply', 'basestring', 'bool', 'buffer',
#   'callable', 'chr', 'classmethod', 'cmp', 'coerce',
    'compile',
#   'complex',
    'delattr',
#   'dict',
    'dir',
#   'divmod', 'enumerate',
    'eval', 'execfile', 'file',
#   'filter', 'float', 'frozenset',
    'getattr', 'globals', 'hasattr',
#    'hash', 'hex', 'id',
#   'input',
#   'int', 'intern', 'isinstance', 'issubclass', 'iter',
#   'len', 'list',
    'locals',
#   'long', 'map', 'max', 'min', 'object', 'oct',
    'open',
#   'ord', 'pow', 'property', 'range',
#   'raw_input',
#   'reduce',
    'reload',
#   'repr', 'reversed', 'round', 'set',
    'setattr',
#   'slice', 'sorted', 'staticmethod',  'str', 'sum', 'super',
#   'tuple', 'type', 'unichr', 'unicode',
    'vars',
#    'xrange', 'zip'
]

for ast_name in unallowed_ast_nodes:
    assert(Helpers.is_valid_ast_node(ast_name))
for name in unallowed_builtins:
    assert(
(name))
    

def is_unallowed_ast_node(kind):
    return kind in unallowed_ast_nodes

def is_unallowed_builtin(name):
    return name in unallowed_builtins

#----------------------------------------------------------------------
# Restricted attributes.
#----------------------------------------------------------------------

# In addition to these we deny access to all lowlevel attrs (__xxx__).
unallowed_attr = [
    'im_class', 'im_func', 'im_self',
    'func_code', 'func_defaults', 'func_globals', 'func_name',
    'tb_frame', 'tb_next',
    'f_back', 'f_builtins', 'f_code', 'f_exc_traceback',
    'f_exc_type', 'f_exc_value', 'f_globals', 'f_locals']

def is_unallowed_attr(name):
    return (name[:2] == '__' and name[-2:] == '__') or \
           (name in unallowed_attr)
           

class SafeEvalVisitor(object):

    def __init__(self):
        "Initialize visitor by generating callbacks for all AST node types."
        self.errors = []
        for ast_name in Helpers.all_ast_nodes:
            # Don't reset any overridden callbacks.
            if getattr(self, 'visit' + ast_name, None): continue
            if is_unallowed_ast_node(ast_name):
                setattr(self, 'visit' + ast_name, self.fail)
            else:
                setattr(self, 'visit' + ast_name, self.ok)

    def walk(self, ast):
        "Validate each node in AST and return True if AST is 'safe'."
        self.visit(ast)
        return self.errors == []
        
    def visit(self, node, *args):
        "Recursively validate node and all of its children."
        fn = getattr(self, 'visit' + Helpers.classname(node))
        if Helpers.DEBUG(): self.trace(node)
        fn(node, *args)
        for child in node.getChildNodes():
            self.visit(child, *args)

    def visitName(self, node, *args):
        "Disallow any attempts to access a restricted builtin/attr."
        name = node.getChildren()[0]
        lineno = Helpers.get_node_lineno(node)
        if is_unallowed_builtin(name):
            self.errors.append(SafeEvalBuiltinError( \
                "access to builtin '%s' is denied" % name, lineno))
        elif is_unallowed_attr(name):
            self.errors.append(SafeEvalAttrError( \
                "access to attribute '%s' is denied" % name, lineno))
               
    def visitGetattr(self, node, *args):
        "Disallow any attempts to access a restricted attribute."
        name = node.attrname
        lineno = Helpers.get_node_lineno(node)
        if is_unallowed_attr(name):
            self.errors.append(SafeEvalAttrError( \
                "access to attribute '%s' is denied" % name, lineno))
            
    def ok(self, node, *args):
        "Default callback for 'harmless' AST nodes."
        pass
    
    def fail(self, node, *args):
        "Default callback for unallowed AST nodes."
        lineno = Helpers.get_node_lineno(node)
        self.errors.append(SafeEvalASTNodeError( \
            "execution of '%s' statements is denied" % Helpers.classname(node),
            lineno))

    def trace(self, node):
        "Debugging utility for tracing the validation of AST nodes."
        print Helpers.classname(node)
        for attr in dir(node):
            if attr[:2] != '__':
                print ' ' * 4, "%-15.15s" % attr, getattr(node, attr)

def exec_timed(code, context, timeout_secs):
    """
    Dynamically execute 'code' using 'context' as the global enviroment.
    SafeEvalTimeoutException is raised if execution does not finish within
    the given timelimit.
    """
    assert(timeout_secs > 0)
    

    signal_finished = False
    exec_errors = []
    
    def alarm(secs):
        def wait(secs):
            for n in xrange(timeout_secs):
                time.sleep(1)
                if signal_finished: break
            else:
                #thread.interrupt_main()
                exec_errors.append(SafeEvalTimeoutException(secs))
        #thread.Start_new_thread(wait, (secs,))
        threading._start_new_thread(wait, (secs,))

   
    try:
        alarm(timeout_secs)
        exec code in context
        signal_finished = True
    
    except Exception, e:
        exec_errors.append(traceback.format_exc())
        
        #raise SafeEvalTimeoutException(timeout_secs)
    finally:
        return exec_errors
        
        
        
def safe_eval(out_queue, code, context = {}, timeout_secs = 1):
    
    ctx_errkeys, ctx_errors = [], []
    
    for (key, obj) in context.items():
        if inspect.isbuiltin(obj):
            ctx_errkeys.append(key)
            ctx_errors.append("key '%s' : unallowed builtin %s" % (key, obj))
        if inspect.ismodule(obj):
            ctx_errkeys.append(key)
            ctx_errors.append("key '%s' : unallowed module %s" % (key, obj))

    if ctx_errors:
        out_queue.put(SafeEvalContextException(ctx_errkeys, ctx_errors))

    ast = compiler.parse(code)
    checker = SafeEvalVisitor()

    if checker.walk(ast):
        exec_errors = exec_timed(code, context, timeout_secs)
      
        if(len(exec_errors) > 0):
            for error in exec_errors:
                out_queue.put(error)
            
    else:
        out_queue.put(SafeEvalCodeException(code, checker.errors))
    
    

        
        
       
