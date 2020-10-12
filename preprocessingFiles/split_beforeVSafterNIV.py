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
# Ler ficheiros de input e output

#inputpath =  input("Enter input file (write filename.csv):")
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

# timeIntervals sao de meses
#timeInterval = int( input("Inserir numero de meses de intervalo entre dois timesteps consecutivos: "))
timeInterval = 3 # exemplo

# Opcoes dos modos de funcionamento do programa
#option = int(input("Inserir Opção (0 faz Last Obs Carried Forward, 1 faz fill com ?): "))
option = 0

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
