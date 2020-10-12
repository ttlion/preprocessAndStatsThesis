###########################################################################
###########################################################################
# Imports

import csv
import sys
import pandas as pd
import numpy as np
import subprocess
import re

###########################################################################
###########################################################################
# Ler ficheiros de input

parentsToCheck = { }
with open(sys.argv[1]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        for elem in row:
            parentsToCheck[elem] = [ ]

print( list( parentsToCheck.keys() ) )

dbnProgramPath = r'sdtDBN_v0_0_1.jar'
timestep = sys.argv[3]

searchExpr = r'^(.*) -> (.*)\[' + timestep +  r'\]'

dbns_structs_checked = []

with open(sys.argv[2]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for rowWithDBNs in csv_reader:
        dbns_structs_checked += [ rowWithDBNs[0].split('_')[-2] ]

        files_com_pais = {}
        i = -1
        for dbnFile in rowWithDBNs:
            i += 1

            p = subprocess.run(['java', '-jar', dbnProgramPath , '-fromFile', dbnFile ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf-8')

            auxText_getOutput = p.stdout

            # Check parents of desired child in proper "dbnFile"

            parentsToStore = []
            for line in auxText_getOutput.splitlines():
                
                checkParent = re.search(searchExpr, line)
                if(checkParent != None):
                    getParentFromLine = line.split(r' -> ')[0].split('[')[0]
                    parentsToStore += [ getParentFromLine ]
                
            files_com_pais[i] = parentsToStore

        for parent in parentsToCheck:
            i=0
            for file in files_com_pais:
                if i==0:
                    if (parent in files_com_pais[file]):
                        parentsToCheck[parent] += [files_com_pais[file].count(parent)]
                        # Usar o .count() assim nao e mt eficiente mas isto tb nao e muito
                        # grande por isso nao me vou preocupar
                    else:
                        parentsToCheck[parent] += [0]
                else:
                    if (parent in files_com_pais[file]):
                        parentsToCheck[parent][-1] += files_com_pais[file].count(parent)
                i += 1

# Put everything in dataframe
dataframeFinal = pd.DataFrame(parentsToCheck, index = dbns_structs_checked)
print(dataframeFinal)

# Store Dataframe in csv file
statsFileName = 'fileWithCounts_timestep{}.csv'.format(timestep) 
dataframeFinal.to_csv(statsFileName, sep=';') 