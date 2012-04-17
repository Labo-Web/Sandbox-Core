'''
Created on 29 mars 2012

@author: damienp
http://bytes.com/topic/python/answers/521401-threading-event-usage-causing-intermitent-exception
'''
from testdevalidation import TestDeValidation
import time


if __name__ == '__main__':

    def methodeimport():print "methode compile"
    variable = {'x':2, 'y':4,'result': 0, 'methodeimport': methodeimport}
    environnement = {'dico':variable}
    code ='''
dico['methodeimport']()
dico['result'] = dico['x'] + dico['y']
print str(dico['result']) + 1
''' 

    start = time.clock()
    dicoThread = {}
    for n in range(0,100):
        dicoThread[n] = TestDeValidation(code, environnement, 1)
        dicoThread[n].TTestRun()
        pass
    
    elapsed = (time.clock() - start)
    print elapsed