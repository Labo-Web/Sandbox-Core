'''
Created on 29 mars 2012

@author: damienp
'''
from com.safeexecution.SafeEvalVisitor import safe_eval


if __name__ == '__main__':

    #unittest.main()
    
    def methodeimport():print "methode compile"
    variable = {'x':2, 'y':4,'result': 0, 'methodeimport': methodeimport}
    environnement = {'dico':variable}
    code ='''
dico['methodeimport']()
dico['result'] = dico['x'] + dico['y']
print str(dico['result'])+ " <- TA MERE"
'''
        
    
    sandbox = safe_eval(code, environnement, 1)