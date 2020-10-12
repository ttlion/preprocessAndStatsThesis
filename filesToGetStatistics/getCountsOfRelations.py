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

parentsToCheckTableIndx = { }
i=0
with open(sys.argv[1]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        for elem in row:
            parentsToCheckTableIndx[elem] = i
            i += 1

dbnProgramPath = r'sdtDBN_v0_0_1.jar'
timestepInit = int(sys.argv[3])
timestepEnd = int(sys.argv[4])

dbns_structs_checked = []

matrixWithCounts = [[0 for x in range(i)] for y in range(i)]

sumVar=0

with open(sys.argv[2]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for rowWithDBNs in csv_reader:
        dbns_structs_checked += [ rowWithDBNs[0].split('_')[-2] ]

        for dbnFile in rowWithDBNs:

            p = subprocess.run(['java', '-jar', dbnProgramPath , '-fromFile', dbnFile ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, encoding='utf-8')

            auxText_getOutput = p.stdout

            for timestep in range(timestepInit, timestepEnd+1):
                searchExpr = r'^(.*) -> (.*)\[' + str(timestep) + r'\]'

                for line in auxText_getOutput.splitlines():
                    checkParent = re.search(searchExpr, line)

                    if(checkParent != None):
                        att1 = line.split(r' -> ')[0].split('[')[0]
                        att2 = line.split(r' -> ')[1].split('[')[0]

                        if(att1 not in parentsToCheckTableIndx or att2 not in parentsToCheckTableIndx):
                            continue

                        att1Indx = parentsToCheckTableIndx[att1]
                        att2Indx = parentsToCheckTableIndx[att2]

                        if(att1Indx == att2Indx):
                            matrixWithCounts[att1Indx][att2Indx] += 1
                            sumVar += 1
                            continue

                        matrixWithCounts[att1Indx][att2Indx] += 1
                        matrixWithCounts[att2Indx][att1Indx] += 1
                        sumVar += 1

# Put everything in dataframe

dataframeFinal = pd.DataFrame(matrixWithCounts, index = list( parentsToCheckTableIndx.keys() ), columns=list( parentsToCheckTableIndx.keys() ))

# Store Dataframe in csv file
statsFileName = 'relationsCounts_timesteps _{}_ate{}_contagens.csv'.format(timestepInit,timestepEnd) 
dataframeFinal.to_csv(statsFileName, sep=';')

dataframeFinal = dataframeFinal.apply(lambda x: x/sumVar)

dataframeFinal = dataframeFinal.round(4)
print(dataframeFinal)

# Store Dataframe in csv file
statsFileName = 'relationsCounts_timesteps _{}_ate{}_percentagens.csv'.format(timestepInit,timestepEnd) 
dataframeFinal.to_csv(statsFileName, sep=';')

print('Structs checked:')
print(dbns_structs_checked)