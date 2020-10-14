###########################################################################
###########################################################################
# Imports

import csv
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn.metrics as statMetrics
import statistics

###########################################################################
###########################################################################
# Defining proper command-line user interface

def showUsage():
    print('usage: python compareVars.py filesToCompare.csv outputPath timestepUntilCheckVar minTimestepLengthSeries maxTimestepLengthSeries varToCheck\n')
    print('filesToCompare.csv: File with pairs of files to compare. Each line of this file is in the form "fileWithCorrectValues,fileWithPredictions". See example')
    print('outputPath: Desired path for writing output file. If using just . the program will write in directory of program!')
    print('timestepUntilCheckVar: Program checks the predictions of varToCheck from timestep 1 until timestep timestepUntilCheckVar')
    print('minTimestepLengthSeries: Minimum size of the time-series (in the files with correct values) that program considers for getting the statistics')
    print('maxTimestepLengthSeries: Maximum size of the time-series (in the files with correct values) that program considers for getting the statistics')
    print('varToCheck: Variable that is in the files with predictions, whose predictions are to be compared with the true values\n')
    print('------------------------------------')
    print('IMPORTANT IMPORTANT IMPORTANT')
    print('timestepUntilCheckVar must be between 1 and the maximum timestep for which there are predictions in the fileWithPredictions files of filesToCompare.csv')
    print('varToCheck must be the same variable for which there are predictions in the fileWithPredictions files of filesToCompare.csv')
    print('IMPORTANT IMPORTANT IMPORTANT')
    print('------------------------------------')
    print('\nRun python compareVars.py -e for an example of filesToCompare.csv')
    print('\nRun python compareVars.py -h for usage')
    return

def printExample():
    print('The file filesToCompare.csv has the following format:\n')
    print('example_correctLabels_0.csv,example_estimatedLabels_0.csv\nexample_correctLabels_1.csv,example_estimatedLabels_1.csv\n...If desired, more lines can be added, always with files in the form fileWithCorrectValues,fileWithPredictions...\n')
    print('The files with correct values, for instance example_correctLabels_0.csv, have the following format (example for: three variables X, Y and Z; three timesteps 0, 1 and 2; two REFs 1 and 2):\n')
    print('REF,X__0,Y__0,Z__0,X__1,Y__1,Z__1,X__2,Y__2,Z__2\n1,-1,-1,-1,2,2,2,3,3,3\n2,-1,-1,-1,9,9,9,3,3,3\n')
    print('The files with predictions, for instance example_estimatedLabels_0.csv, have the following format (for instance, for predictions of X variable until timestep 2 for REFs 1 and 2):\n')
    print('id,X[1],X[2]\n1,2,3\n2,2,3\n')
    print('Note that timesteps in the file with correct values are with __ and that timesteps in the file with predictions are with [ ]')


# Check command-line arguments validity
if len(sys.argv) == 2:
    if sys.argv[1] == '-h':
        showUsage()
        exit()
    elif sys.argv[1] == '-e':
        printExample()
        exit()

if len(sys.argv) != 7:
    print('Not all arguments inserted! Run python compareVars.py -h for usage')
    exit()

if int(sys.argv[4]) < 0:
    print('minTimestepLengthSeries cannot be < 0 ! Run python compareVars.py -h for usage')
    exit()

if int(sys.argv[5]) < 0:
    print('maxTimestepLengthSeries cannot be < 0 ! Run python compareVars.py -h for usage')
    exit()

if int(sys.argv[4]) > int(sys.argv[5]):
    print('minTimestepLengthSeries cannot be > maxTimestepLengthSeries ! Run python compareVars.py -h for usage')
    exit()

###########################################################################
###########################################################################
# Ler ficheiros de input

severalPaths = []
timestepUntilCheckVar = int(sys.argv[3])
listsWithCorrectCounts = {}
listsWithPredictedCounts = {}
dictWithSeriesLength = {}
for i in range (1, timestepUntilCheckVar+1):
    listsWithCorrectCounts[i] = []
    listsWithPredictedCounts[i] = []
    dictWithSeriesLength[i] = []

minTimestepLengthSeries = int(sys.argv[4])
maxTimestepLengthSeries = int(sys.argv[5])

varToCheck = sys.argv[6]

# Get proper string to identifiy filenames
addToFilenames = 'inf_' + varToCheck + '_timesteps_{}_to_{}_until_Var{}'.format(minTimestepLengthSeries,maxTimestepLengthSeries,timestepUntilCheckVar)

with open(sys.argv[1]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        severalPaths = severalPaths + [ (row[0], row[1]) ]

for pathCorrect, pathEstim in severalPaths:

    # Read input files, putting patients REFs as indexes for each row
    inputDfCorrect = pd.read_csv(pathCorrect, sep = ',', index_col=0, header=0)
    inputDfEstim = pd.read_csv(pathEstim, sep = ',', index_col=0, header=0)

    colsToCheckCorrect = [col for col in inputDfCorrect.columns if (varToCheck+'_') in col]
    
    onlyVarDf = inputDfCorrect[colsToCheckCorrect]

    newDf = pd.DataFrame(onlyVarDf.applymap(lambda x: '?' in str(x)).dot(onlyVarDf.columns+',').str[:-1])
    
    newDf.columns = ['length']

    newDf['length'] = newDf['length'].apply(lambda x: int( onlyVarDf.columns[-1].replace((varToCheck + '__'), '') ) if str(x) == '' else int( str(x).split(',')[0].replace((varToCheck + '__'), '') ) - 1 )

    newDf = pd.concat([newDf, onlyVarDf], axis=1)

    colsWithEstim = [col for col in inputDfEstim.columns if (varToCheck in col)]
    estimDf = inputDfEstim[colsWithEstim]

    newDf = pd.concat([newDf, estimDf], axis=1)

    newDf = newDf.drop(newDf[newDf['length'] < minTimestepLengthSeries].index)
    newDf = newDf.drop(newDf[newDf['length'] > maxTimestepLengthSeries].index)
    
    for key in listsWithCorrectCounts:
        auxDf = newDf.drop(newDf[newDf[varToCheck + '__' + str(key)] == '?'].index)
        auxDf = auxDf.drop(auxDf[pd.isna(auxDf[varToCheck + '[' + str(key) + ']'])].index)
        listsWithCorrectCounts[key] += list(auxDf[varToCheck + '__' + str(key)])
        listsWithPredictedCounts[key] += list(auxDf[varToCheck + '[' + str(key) + ']'])
        dictWithSeriesLength[key] += list(auxDf['length'])

###################################
# Create dataframe with all info
rowsDf = ['Accuracy', '% Above', '% Bellow', '1st Quartile', 'Sensitivity', 'Specificity', 'AUC', 'Evaluated patients']
columnsDf = []
for key in listsWithCorrectCounts:
    columnsDf += ['Want Perfect__timestep' + str(key)]#, 'Want range 1__timestep' + str(key)]
statsDf = pd.DataFrame(index=rowsDf, columns=columnsDf)

###################################
# Fill dataframe
for key in listsWithCorrectCounts:

    listWithCorrectCounts = [int(i) for i in listsWithCorrectCounts[key]]
    listWithPredictedCounts = [int(i) for i in listsWithPredictedCounts[key]]

    ###########################################################################
    ###########################################################################
    # Stats calculation

    #####################################################################
    #####################################################################
    # Acurracies

    listWithSubtractions = np.array(listWithPredictedCounts) - np.array(listWithCorrectCounts)

    # Ideia: em cada cenario passar valores a labels
    #    -> Se estimado inferior ao correcto, label -1
    #    -> Se correto (pode ser range), label 0
    #    -> Se estimado superior ao correcto, label +1

    listAllZeros =  [0 for val in listWithSubtractions ]
    listWantPerfect = [0 if val==0 else -1 if val<0 else 1 for val in listWithSubtractions ]
    listWantRange1 = [0 if abs(val)<=1 else -1 if val<-1 else 1 for val in listWithSubtractions ]

    accuracyWantPerfect = statMetrics.accuracy_score(listAllZeros, listWantPerfect)
    #accuracyWantRange1 = statMetrics.accuracy_score(listAllZeros, listWantRange1)

    percentBelowWantPerfect = sum(1 for i in listWantPerfect if i==-1) / len(listWantPerfect)
    #percentBelowWantRange1 = sum(1 for i in listWantRange1 if i==-1) / len(listWantRange1)

    percentAboveWantPerfect = sum(1 for i in listWantPerfect if i==1) / len(listWantPerfect)
    #percentAboveWantRange1 = sum(1 for i in listWantRange1 if i==1) / len(listWantRange1)

    #####################################################################
    #####################################################################
    # Calcular sensitivity and specificity face a classe no 1o quartil

    firstQuartileClass = np.quantile(listWithCorrectCounts, 0.25)

    correctAboveOrBelowQuartile = [0 if val<=firstQuartileClass else 1 for val in listWithCorrectCounts ]
    predictedAboveOrBelowQuartile = [0 if val<=firstQuartileClass else 1 for val in listWithPredictedCounts ]

    confMatrix = statMetrics.confusion_matrix(correctAboveOrBelowQuartile, predictedAboveOrBelowQuartile)
    if( len(confMatrix)>1 ):
        # This confusion matrix has(assuming that 0 is positive and 1 is negative):
        #
        #                            |              Predicted
        #                            |  0: predict<=avg    |  1: predict>avg   
        # ---------------------------+---------------------|---------------------
        #          0: correct<=avg   |          TP         |          FN
        # Correct -------------------|---------------------|---------------------
        #          1: correct>avg    |          FP         |          TN        
        # 
        # 

        # Sensitivity(or TPR): TP/(TP+FN)
        sensitivity = confMatrix[0,0]/(confMatrix[0,0]+confMatrix[0,1])

        # Specificity(or FPR): TN/(TN+FP)
        specificity = confMatrix[1,1]/(confMatrix[1,1]+confMatrix[1,0])

        # AUC score
        auc = statMetrics.roc_auc_score(correctAboveOrBelowQuartile, predictedAboveOrBelowQuartile )

    else: # if there is only 1 true label
        sensitivity = -1
        specificity = -1
        auc = -1

    # Avg length of the analysed timeseries (ja nao estou a medir isto)
    #avgLen = sum(dictWithSeriesLength[key])/len(dictWithSeriesLength[key])

    # Write in Dataframe
    statsDf['Want Perfect__timestep' + str(key)] =  [accuracyWantPerfect, percentAboveWantPerfect, percentBelowWantPerfect, firstQuartileClass, sensitivity, specificity, auc, len(listWithCorrectCounts) ]
    #statsDf['Want range 1__timestep' + str(key)] =  [accuracyWantRange1, percentBelowWantRange1, percentAboveWantRange1, firstQuartileClass, sensitivity, specificity, auc, len(listWithCorrectCounts) ]

statsDf = statsDf.round(4)
print(statsDf)

###################################
# Store Dataframe in csv file
# statsFileName = '\\stats_befNIV_' + addToFilenames + '.csv' 
statsFileName = '\\output_stats.csv'
statsDf.to_csv(sys.argv[2] + statsFileName, sep=';') 

# The code bellow can be used to produce histogram of the predictions of a certain timestep:
##############################################
# Generate histogram

# Proper histogram filename
# histFileName = '\\hist_afterNIV_' + addToFilenames

# Get values only of Var[1] to present histogram
# listWithCorrectCounts = [int(i) for i in listsWithCorrectCounts[1]]
# listWithPredictedCounts = [int(i) for i in listsWithPredictedCounts[1]]
# listWithSubtractions = np.array(listWithPredictedCounts) - np.array(listWithCorrectCounts)

# Plot Histogram of predictions done in timestep1
# mybins = np.arange(start=-10.5, stop=10.5, step=1)
# plt.hist(listWithSubtractions, bins=mybins, alpha=0.5, histtype='bar', ec='black', color='purple', density=True)
# plt.title('Diferences between estimated class and real class')
# plt.xticks(np.arange(-10, 11, step=1))
# plt.xlabel('Distance to correct class')
# plt.ylabel('Percentage of the {} analysed values'.format(len(np.array(listsWithPredictedCounts[1]))))
# plt.savefig(sys.argv[2] + histFileName)
# #plt.show()
