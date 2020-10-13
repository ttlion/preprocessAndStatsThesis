# -*- coding: utf-8 -*-
"""
Program receives two input datasets, dataset1 and dataset2, both with the 
first column being REF (a unique id per subject).

The program creates a new dataset (file), which has the data of the REFs of
dataset2 that also exist in dataset1.

For instance, if dataset1 has data for REFs 1, 2 and 3, while dataset2 has data
for REFs 2, 3 and 4, the program will output the data of REFs 2 and 3 from dataset2.

@author: Tiago Leão
"""

###########################################################################
###########################################################################
# Imports

import csv
import sys

###########################################################################
###########################################################################
# Deal with command line user interface

def showUsage():
    print('usage: python prune_REFs.py dataset1.csv dataset2.csv outputFile.csv\n')
    print('dataset1.csv: Input dataset, a table in CSV format')
    print('dataset2.csv: Input dataset, a table in CSV format')
    print('outputFile.csv: Desired output file in CSV format')
    print('\nImportant Note: The first column of both dataset1 and dataset2 must be named REF and contain the unique ids of subjects')
    print('\nProgram outputs the data of dataset2 whose subjects (REFs) are in both dataset1 and dataset2')
    print('\nRun python prune_REFs.py -e for an example of input file')
    print('\nRun python prune_REFs.py -h for usage')
    return

def printExample():
    print('Example of Input:\n')
    print('+-----+------------+----------+----------+')
    print('| REF | Date       | Feature1 | Feature2 |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 10/02/2000 | a        | A        |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 03/04/2000 | b        | B        |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 05/05/2000 |          |          |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 07/01/2001 | d        | D        |')
    print('+-----+------------+----------+----------+')
    print('| 2   | 03/03/1999 | e        | E        |')
    print('+-----+------------+----------+----------+')
    print('| 2   | 04/02/2000 |          | F        |')
    print('+-----+------------+----------+----------+')
    print('| 2   | 05/04/2001 | g        | G        |')
    print('+-----+------------+----------+----------+')
    print('| 3   | 10/06/2018 | h        | H        |')
    print('+-----+------------+----------+----------+')
    print('| 3   | 04/07/2018 | i        | I        |')
    print('+-----+------------+----------+----------+')
    print('| 3   | 04/09/2018 | l        | L        |')
    print('+-----+------------+----------+----------+')
    return

if len(sys.argv) == 2:
    if sys.argv[1] == '-h':
        showUsage()
        exit()
    elif sys.argv[1] == '-e':
        printExample()
        exit()
    else:
        print('Arguments not properly inserted! Run python prune_REFs.py -h for usage')
        exit()

if len(sys.argv) != 4:
    print('Arguments not properly inserted! Run python prune_REFs.py -h for usage')
    exit()

###########################################################################
###########################################################################
# Ler ficheiros de input e output

inputpathDyn = sys.argv[1]
inputpathStatic = sys.argv[2]
outputpath = sys.argv[3]

###########################################################################
###########################################################################
# Abrir o ficheiros com valores dinamicos e inicializar reader respetivo

inputFile = open(inputpathDyn, newline='', encoding='utf-8-sig')
reader = csv.reader(inputFile)

###########################################################################
###########################################################################

# Tirar o header
header = next(reader)

if (header[0] != "REF"):
    print("Check if file well-formated!")
    exit()

refsNoFileDinamico = set()

##############

for row in reader:
    refsNoFileDinamico.add(row[0])


###########################################################################
###########################################################################
# Fechar o ficheiro com valores dinamicos
    
inputFile.close()

###########################################################################
###########################################################################
###########################################################################
###########################################################################
# Abrir o ficheiros com valores estaticos e inicializar reader respetivo

inputFile = open(inputpathStatic, newline='', encoding='utf-8-sig')
reader = csv.reader(inputFile)

# Abrir o ficheiro de output e inicializar writer respetivo

outputFile = open(outputpath, 'w', newline='')
writer = csv.writer(outputFile)


###########################################################################
###########################################################################
# Ler o ficheiro com valores estaticos e por no novo ficheiro, so uma vez por REF, 
# os valores estaticos das REFS que existirem nos ficheiros dinamico e estatico

# Tirar o header
header = next(reader)

if (header[0] != "REF"):
    print("Check if file well-formated!")
    exit()
    
writer.writerow(header)

for row in reader:
    currREF = row[0]
    
    if(currREF not in refsNoFileDinamico):
        continue
    
    writer.writerow(row)



inputFile.close()
outputFile.close()

###########################################################################
###########################################################################


