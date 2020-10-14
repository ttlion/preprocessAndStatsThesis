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
    print('usage: python getParentsCountsOfTimesteps.py parentsToCheck.csv dbnsToUse.csv timestepToCheck \n')
    print('Program counts, considering the DBNs in dbnsToUse.csv, the number of children each variable from parentsToCheck.csv has in the timestep timestepToCheck\n')
    print('parentsToCheck.csv: has a line with all variables for which the user wants to know the number of children')
    print('dbnsToUse.csv: has the DBNs to consider')
    print('timestepToCheck: has the desired timestep')
    print('\nRun python getParentsCountsOfTimesteps.py -eParents for an example of parentsToCheck.csv')
    print('\nRun python getParentsCountsOfTimesteps.py -eDBNs for an example of dbnsToUse.csv')
    print('\nRun python getParentsCountsOfTimesteps.py -h for usage')
    return

def printExampleParents():
    print('This file has a single line with the variables for which the user is interested in knowing the number of children (in the specified timestep).')
    print('The variables can be static or dynamic.')
    print('Example of a file, for dynamic variables X, Y and Z, and static variables A and B:\n')
    print('X,Y,Z,A,B')
    return

def printExampleDBNs():
    print('This file must have the DBNs that must be considered for making the counts.')
    print('The DBNs must be sdtDBNs stored in a file, see the sdtDBN webpage for more details.')
    print('This file may have multiple lines, in that case it will perform the counts for each set of DBNs in each line.')
    print('Each line must have a tag associated, which is done by putting the names of the DBNs of each line always in the format tag_someDesiredName')
    print('An example would be the following:\n')
    print('tag1_someStoredDBN1.txt\ntag2_someStoredDBN2.txt,tag2_someOtherStoredDBN2.txt\n')
    print('In the previous example, the program would output the counts for tag1 and tag2.')
    print('The counts associated with tag1 would be of the DBN stored in tag1_someStoredDBN1.txt')
    print('The counts associated with tag2 would be of the DBNs stored in tag2_someStoredDBN2.txt and tag2_someOtherStoredDBN2.txt')
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

if len(sys.argv) != 4:
    print('Not all arguments inserted! Run python getParentsCountsOfTimesteps.py -h for usage')
    exit()

if sys.argv[1].find('.csv') == -1:
    print('Input file parentsToCheck.csv must be .csv format! Run python getParentsCountsOfTimesteps.py -h for usage')
    exit()

if sys.argv[2].find('.csv') == -1:
    print('Input file dbnsToUse.csv must be .csv format! Run python getParentsCountsOfTimesteps.py -h for usage')
    exit()

if int(sys.argv[3]) < 0:
    print('Timestep cannot be < 0 ! Run python getParentsCountsOfTimesteps.py -h for usage')
    exit()

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