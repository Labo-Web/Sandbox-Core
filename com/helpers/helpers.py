'''
Created on 12 avr. 2012

@author: damienp
'''
import compiler
import inspect

class Helpers(object):
    '''
    classdocs
    '''

    def __init__(self, selfparams):
        pass
    
    
    
# List of all AST node classes in compiler/ast.py.
    all_ast_nodes = \
        [name for (name, obj) in inspect.getmembers(compiler.ast)
         if inspect.isclass(obj) and issubclass(obj, compiler.ast.Node)]
    
    # List of all builtin functions and types (ignoring exception classes).
    all_builtins = \
        [name for (name, obj) in inspect.getmembers(__builtins__)
         if inspect.isbuiltin(obj) or (inspect.isclass(obj) and \
                                       not issubclass(obj, Exception))]
        
#----------------------------------------------------------------------
# Utilties.
#----------------------------------------------------------------------
    @staticmethod
    def  classname(obj):
        return obj.__class__.__name__
    
    @staticmethod
    def  DEBUG():
        return False
    
    

    @staticmethod
    def is_valid_ast_node(name):
        return name in Helpers.all_ast_nodes

    @staticmethod
    def is_valid_builtin(name):
        return name in Helpers.all_builtins

    @staticmethod
    def get_node_lineno(node):
        return (node.lineno) and node.lineno or 0