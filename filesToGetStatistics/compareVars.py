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

print(newDf)
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
statsFileName = '\\stats_befNIV_' + addToFilenames + '.csv' 
statsDf.to_csv(sys.argv[2] + statsFileName, sep=';') 

##############################################
# Generate histogram

# Proper histogram filename
histFileName = '\\hist_afterNIV_' + addToFilenames

# Get values only of Var[1] to present histogram
listWithCorrectCounts = [int(i) for i in listsWithCorrectCounts[1]]
listWithPredictedCounts = [int(i) for i in listsWithPredictedCounts[1]]
listWithSubtractions = np.array(listWithPredictedCounts) - np.array(listWithCorrectCounts)

# Plot Histogram of predictions done in timestep1
mybins = np.arange(start=-10.5, stop=10.5, step=1)
plt.hist(listWithSubtractions, bins=mybins, alpha=0.5, histtype='bar', ec='black', color='purple', density=True)
plt.title('Diferences between estimated class and real class')
plt.xticks(np.arange(-10, 11, step=1))
plt.xlabel('Distance to correct class')
plt.ylabel('Percentage of the {} analysed values'.format(len(np.array(listsWithPredictedCounts[1]))))
plt.savefig(sys.argv[2] + histFileName)
#plt.show()
