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
# Defining proper command-line user interface

def showUsage():
    print('usage: python getCountsOfRelations.py parentsToCheck.csv dbnsToUse.csv timestepInit timestepEnd \n')
    print('Program counts, considering the DBNs in dbnsToUse.csv, the number of edges between each pair of variables from parentsToCheck.csv. The counts are made considering, in each DBN, all timesteps from timestepInit until timestepEnd\n')
    print('Program provides as output a 2d matrix with the counts done between each pair of variables (matrix is symmetric, as direction of edges is not important)\n')
    print('parentsToCheck.csv: has a line with all variables for which the user wants to know the number of edges between the respective pairs')
    print('dbnsToUse.csv: has the DBNs to consider')
    print('timestepInit: has the initial timestep, to start considering relations among variables')
    print('timestepEnd: has the final timestep, to finish considering relations among variables')
    print('\nRun python getCountsOfRelations.py -eParents for an example of parentsToCheck.csv')
    print('\nRun python getCountsOfRelations.py -eDBNs for an example of dbnsToUse.csv')
    print('\nRun python getCountsOfRelations.py -h for usage')
    return

def printExampleParents():
    print('This file has a single line with the names of the desired variables, which can be static or dynamic')
    print('The program creates a 2d matrix where each dimension of the matrix has the variables of this file, and each element of the matrix has the number of edges between the respective variables. The matrix is symmetric because the direction of the edges is not relevant.')
    print('Example of a file, for dynamic variables X, Y and Z, and static variables A and B:\n')
    print('X,Y,Z,A,B')
    return

def printExampleDBNs():
    print('This file must have the DBNs that must be considered for making the counts.')
    print('The DBNs must be sdtDBNs stored in a file, see the sdtDBN webpage for more details.')
    print('This file has multiple lines. Each line must have a tag associated, which is done by putting the names of the DBNs of each line always in the format tag_someDesiredName')
    print('The program outputs the analyzed tags.')
    print('An example would be the following:\n')
    print('tag1_someStoredDBN1.txt\ntag2_someStoredDBN2.txt,tag2_someOtherStoredDBN2.txt\n')
    print('In the previous example, the program would make the counts considering all three DBNs (tag1_someStoredDBN1.txt, tag2_someStoredDBN2.txt and tag2_someOtherStoredDBN2.txt). Then, besides providing the counts as output, the program would output that it analyzed both tag1 and tag2')
    return

# Check command-line arguments validity
if len(sys.argv) == 2:
    if sys.argv[1] == '-h':
        showUsage()
        exit()
    elif sys.argv[1] == '-eParents':
        printExampleParents()
        exit()
    elif sys.argv[1] == '-eDBNs':
        printExampleDBNs()
        exit()

if len(sys.argv) != 5:
    print('Not all arguments inserted! Run python getCountsOfRelations.py -h for usage')
    exit()

if sys.argv[1].find('.csv') == -1:
    print('Input file parentsToCheck.csv must be .csv format! Run python getCountsOfRelations.py -h for usage')
    exit()

if sys.argv[2].find('.csv') == -1:
    print('Input file dbnsToUse.csv must be .csv format! Run python getCountsOfRelations.py -h for usage')
    exit()

if int(sys.argv[3]) < 0:
    print('timestepInit cannot be < 0 ! Run python getCountsOfRelations.py -h for usage')
    exit()

if int(sys.argv[4]) < 0:
    print('timestepEnd cannot be < 0 ! Run python getCountsOfRelations.py -h for usage')
    exit()

if int(sys.argv[3]) > int(sys.argv[4]):
    print('timestepInit cannot be > timestepEnd ! Run python getCountsOfRelations.py -h for usage')
    exit()

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
print(dataframeFinal)

# Store Dataframe in csv file
statsFileName = 'relationsCounts_timestep_{}_until_{}_counts.csv'.format(timestepInit,timestepEnd) 
dataframeFinal.to_csv(statsFileName, sep=';')

# To normalize values uncomment this
# dataframeFinal = dataframeFinal.apply(lambda x: x/sumVar)
# dataframeFinal = dataframeFinal.round(4)
# print(dataframeFinal)
#
# # Store Dataframe in csv file
# statsFileName = 'relationsCounts_timestep_{}_until{}_counts_normalized.csv'.format(timestepInit,timestepEnd) 
# dataframeFinal.to_csv(statsFileName, sep=';')

print('Structs checked:')
print(dbns_structs_checked)