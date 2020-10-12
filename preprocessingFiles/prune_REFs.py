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


