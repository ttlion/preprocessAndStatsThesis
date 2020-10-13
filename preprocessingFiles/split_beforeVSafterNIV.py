# -*- coding: utf-8 -*-
"""

@author: Tiago Leão
"""

###########################################################################
###########################################################################
# Imports

import csv
from datetime import datetime
import os
import sys 

###########################################################################
###########################################################################
# Defs for user interface

def showUsage():
    print('usage: python split_beforeVSafterNIV.py inputFile.csv deltaT option\n')
    print('inputFile.csv: Input dataset in CSV format')
    print('deltaT: number of months of interval between two timesteps to be created')
    print('option (0 or 1): 0 does Last Obs Carried Forward, 1 fills with ?')
    print('\nRun python split_beforeVSafterNIV.py -e for an example of input')
    print('\nRun python split_beforeVSafterNIV.py -h for usage')
    return

def printExample():
    print('Example of Input:\n')
    print('+-----+------------+----------+----------+------------+')
    print('| REF | Date       | Feature1 | Feature2 | NIV        |')
    print('+-----+------------+----------+----------+------------+')
    print('| 1   | 10/02/2000 | a        | A        | 01/06/2000 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 1   | 03/04/2000 | b        | B        | 01/06/2000 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 1   | 05/05/2000 | c        | C        | 01/06/2000 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 1   | 07/01/2001 | d        | D        | 01/06/2000 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 2   | 03/03/1999 | e        | E        | 01/01/2001 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 2   | 04/02/2000 | f        | F        | 01/01/2001 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 2   | 05/04/2001 | g        | G        | 01/01/2001 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 3   | 10/06/2018 | h        | H        | 01/01/2018 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 3   | 04/07/2018 | i        | I        | 01/01/2018 |')
    print('+-----+------------+----------+----------+------------+')
    print('| 3   | 04/09/2018 | l        | L        | 01/01/2018 |')
    print('+-----+------------+----------+----------+------------+')
    return

###########################################################################
###########################################################################
# Defs

def months_appart(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def writeFillToFile(option, fileToWrite, writers, ref, 
                        timestepDiscretized, prevRow, allUnknown):
    if option == 0: # Fazer last observation carried forward
        writers[fileToWrite].writerow([ref , timestepDiscretized, prevRow])
    elif option == 1: # Fazer ? fill
        writers[fileToWrite].writerow([ref , timestepDiscretized, allUnknown])
        
    return

###########################################################################
###########################################################################
# Check command line arguments validity

if len(sys.argv) == 2:
    if sys.argv[1] == '-h':
        showUsage()
        exit()
    elif sys.argv[1] == '-e':
        printExample()
        exit()


if len(sys.argv) != 4:
    print('Not all arguments inserted! Run python split_beforeVSafterNIV.py -h for usage')
    exit()

###########################################################################
###########################################################################
# Ler ficheiros de input e output

if sys.argv[1].find('.csv') == -1:
    print('Input file must be .csv format! Run python split_beforeVSafterNIV.py -h for usage')
    exit()

inputpath = sys.argv[1]

#outputpath =  input("Enter desired output file name (write filename.csv):")
outputpathBefore = inputpath.split('.csv')[0] + '_beforeNIV.csv'
outputpathAfter = inputpath.split('.csv')[0] + '_afterNIV.csv'

# Isto e ficheiro auxiliar por causa das ultimas linhas de codigo
auxiliarPathBefore = "auxiliar_before.csv"
auxiliarPathAfter = "auxiliar_after.csv"

# cria-se ficheiro auxiliar porque o ficheiro de output nao e impresso logo
# no formato desejado para csv, logo cria-se auxiliar e depois faz-se prune

###########################################################################
###########################################################################
# Abrir os ficheiros e inicializar readers e writers

inputFile = open(inputpath, newline='', encoding='utf-8-sig')
reader = csv.reader(inputFile)

auxiliarFileBefore = open(auxiliarPathBefore, 'w', newline='')
writerBefore = csv.writer(auxiliarFileBefore)

auxiliarFileAfter = open(auxiliarPathAfter, 'w', newline='')
writerAfter = csv.writer(auxiliarFileAfter)

# Criar dicionario para os writers
writers = { 0 : writerBefore, 1: writerAfter }

###########################################################################
###########################################################################

# Tirar o header
header = next(reader)

# Substituir o campo da date por um campo de datestep
header.pop(1)
header.insert(1, 'dateStep')

# Escrever o header no ficheiro de output
writers[0].writerow(header)
writers[1].writerow(header)

# Array para fill com ? se user especificar esssa opcao
allUnknown = ['?'] * (len(header) - 2)

###########################################################################
###########################################################################
# Inicializacoes

# Estou a assumir que os ids de pacientes nao sao negativos
prevRef = -100
currRef = 0

if int(sys.argv[2]) < 1:
    print('deltaT must be positive! Run python split_beforeVSafterNIV.py -h for usage')
    exit()

# timeIntervals sao de meses
timeInterval = int(sys.argv[2])

# Opcoes dos modos de funcionamento do programa
if int(sys.argv[3]) != 0 and int(sys.argv[3]) != 1 :
    print('option must be 0 or 1! Run python split_beforeVSafterNIV.py -h for usage')
    exit()

option = int(sys.argv[3])

# Meter a ultima posicao como onde estara o NIV, guardar o indice dessa ultima posicao numa var
indexNIV = len(header) - 1

###########################################################################
###########################################################################
# Ciclo de leitura e escrita para caso em que se força time series com 
# intervalos de tempo constantes

# Init de valores
currTimestep = 0
nextMandatory = timeInterval + 1 # para nao entrar no if na primeira iteracao do for

# Estes dois nem e preciso fazer init, apenas faco para nao haver warnings em baixo
timestepDiscretized = 0
prevRow = 0 # Isto depois vai deixar de ser int para ser uma row

fileToWrite = 0

##############

for row in reader:
    # Ler o ref e a data da linha em analise
    currRef = row[0]
    date_curr = datetime.strptime(row[1], '%d/%m/%Y')
    
    # Tirar o ref e a data da lista porque depois vou imprimir
    row.pop(0)
    row.pop(0)
    
    # Caso em que se tem novo ref e se tem que reinicializar tudo
    if currRef != prevRef:
        
        # Para se escrever sempre o ultimo dado da ref anterior
        if currTimestep > nextMandatory - timeInterval:
            writeFillToFile(option, fileToWrite, writers, prevRef, 
                            timestepDiscretized, prevRow, allUnknown)
        
        date_init = date_curr
        currTimestep = 0
        nextMandatory = 0
        prevRow = row
        timestepDiscretized = 0
        
        # Reinicializar os contadores da NIV date
        fileToWrite = 0 # Ainda se esta antes do NIV
        timeStepNIV = 100000000 # Um timestep tao grande que nao sera antingido
        if row[indexNIV-2] != '0':
            dateNIV = datetime.strptime(row[indexNIV-2], '%d/%m/%Y')
            timeStepNIV = months_appart(dateNIV, date_init)
        
    
    lastTimestep = currTimestep #guardo o anterior porque posso precisar no if a seguir
    # Ver qual o indice da linha atual
    currTimestep = months_appart(date_curr, date_init)
    
    # Ver se ja se tem que passar a escrever no ficheiro com dados depois do NIV
    if (fileToWrite == 0) and (currTimestep > timeStepNIV):       
        # Escrever ultimo dado no ficheiro com dados antes do NIV, se ainda nao tiver escrito!
        # A segunda condicao do and é para casos em que so ha dados ja dps do NIV!
        if lastTimestep > nextMandatory - timeInterval and timestepDiscretized != 0:
            writeFillToFile(option, fileToWrite, writers, currRef, 
                            timestepDiscretized, prevRow, allUnknown)
        
        # Reinicializar todos estes campos porque se vai escrever noutro ficheiro
        # e quer por-se a 1ª consulta depois do NIV como o timestep 0 desta
        # time series apos o NIV
        date_init = date_curr
        currTimestep = 0
        nextMandatory = 0
        prevRow = row
        timestepDiscretized = 0 # ponho isto a 0 porque se escreve noutro ficheiro
        fileToWrite = 1 # mudar o ficheiro onde se escreve


    # Caso ainda se tenha que escrever indices ate chegar ao atual
    while currTimestep > nextMandatory:
        writeFillToFile(option, fileToWrite, writers, currRef, 
                        timestepDiscretized, prevRow, allUnknown)       
        
        timestepDiscretized += 1
        nextMandatory += timeInterval

    # Se se estiver no timestep exato e imprime-se no novo ficheiro
    if currTimestep == nextMandatory:
        writers[fileToWrite].writerow( [currRef , timestepDiscretized, row] )
        timestepDiscretized += 1
        nextMandatory += timeInterval
    
    #Alterar os prevs
    prevRef = currRef
    prevRow = row

##############

# Para se escrever sempre o ultimo dado da ultima ref
if currTimestep > nextMandatory - timeInterval:
    writeFillToFile(option, fileToWrite, writers, currRef, 
                    timestepDiscretized, prevRow, allUnknown)


###########################################################################
###########################################################################
###########################################################################
###########################################################################
# Fechar os ficheiros
    
inputFile.close()
auxiliarFileBefore.close()
auxiliarFileAfter.close()

###########################################################################
###########################################################################
###########################################################################
###########################################################################
# Eliminar chars [ ' " e ] do ficheiro de output com dados antes NIV

fileToPrune = open(auxiliarPathBefore, newline='', encoding='utf-8-sig')
outputFile = open(outputpathBefore, 'w', newline='')

data = fileToPrune.read()
data = data.replace("'", "")
data = data.replace("[", "")
data = data.replace("]", "")
data = data.replace('"', "")
data = data.replace(' ', "")
outputFile.write(data)

fileToPrune.close()
outputFile.close()

os.remove("auxiliar_before.csv")


###########################################################################
###########################################################################
# Eliminar chars [ ' " e ] do ficheiro de output com dados depois NIV

fileToPrune = open(auxiliarPathAfter, newline='', encoding='utf-8-sig')
outputFile = open(outputpathAfter, 'w', newline='')

data = fileToPrune.read()
data = data.replace("'", "")
data = data.replace("[", "")
data = data.replace("]", "")
data = data.replace('"', "")
data = data.replace(' ', "")
outputFile.write(data)

fileToPrune.close()
outputFile.close()

os.remove("auxiliar_after.csv")

###########################################################################
###########################################################################
