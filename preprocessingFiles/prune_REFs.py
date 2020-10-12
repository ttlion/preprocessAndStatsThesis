# -*- coding: utf-8 -*-
"""

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
    print("0Confirmar que esta bem")
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

# Abrir o ficheiro de output i inicializar writer respetivo

outputFile = open(outputpath, 'w', newline='')
writer = csv.writer(outputFile)


###########################################################################
###########################################################################
# Ler o ficheiro com valores estaticos e por no novo ficheiro, so uma vez por REF, 
# os valores estaticos das REFS que existirem nos ficheiros dinamico e estatico

# Tirar o header
header = next(reader)

if (header[0] != "REF"):
    print("1Confirmar que esta bem")
    exit()
    
writer.writerow(header)

seenREFs = set()

for row in reader:
    currREF = row[0]
    
    if(currREF not in refsNoFileDinamico):
        continue
    
    #if(currREF not in seenREFs):
        #seenREFs.add(currREF)
    writer.writerow(row)


###########################################################################
###########################################################################

inputFile.close()
outputFile.close()

###########################################################################
###########################################################################


