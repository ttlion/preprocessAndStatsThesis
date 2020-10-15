# Files for getting statistics

Files provided:
  * [compareVars.py](#file-comparevarspy)
  * [getParentsCountsOfTimesteps.py](#file-getparentscountsoftimestepspy)
  * [getCountsOfRelations.py](#file-getcountsofrelationspy)

## File compareVars.py

* Allows getting several statistical indicators regarding the comparison of true values and respective predictions, for a certain variable throughout multiple timesteps.

* The true values are given as time-series, where the timesteps must start in 0 and are identified as __
  * An example of a CSV file with time-series, for four ids (1, 2, 3 and 4), three variables (X, Y and Z), and three timesteps (0, 1 and 2) is given next. The order of the variables must be the same in all timesteps! This example will be referred as example_correctLabels_0.csv:

```
          REF,X__0,Y__0,Z__0,X__1,Y__1,Z__1,X__2,Y__2,Z__2
          1,-1,-1,-1,2,2,2,3,3,3
          2,-1,-1,-1,9,9,9,3,3,3
          3,-1,-1,-1,2,2,2,1,1,1
          4,-1,-1,-1,2,2,2,3,3,3
```


* The predictions for a certain variable are given in a file where the timesteps must start at 1 and are identified as [ ]
  * An example of a CSV file with predictions for variable X until timestep 2, for four ids (1, 2, 3 and 4), is given next. This example will be referred as example_estimatedLabels_0.csv:

```
          id,X[1],X[2]
          1,2,3
          2,2,3
          3,2,3
          4,2,3
```

* The program receives a filesToCompare.csv argument. In each line of this file, there must be the file with the true values and then the file with the respective predictions.
  * An example of a line of a file filesToCompare.csv is

```
          example_correctLabels_0.csv,example_estimatedLabels_0.csv
```

* If there was also a file example_correctLabels_1.csv with some true values and a file example_estimatedLabels_1.csv with respective predictions, the file filesToCompare.csv could use all files presented (the ones ending in _0 and _1), being written as
  
```
          example_correctLabels_0.csv,example_estimatedLabels_0.csv
          example_correctLabels_1.csv,example_estimatedLabels_1.csv
```

* Note that the files example_estimatedLabels_0.csv and example_estimatedLabels_1.csv must estimate the values of the same variable (X in the given example).
  * This is generalizable for any number of files with predictions inserted in filesToCompare.csv!!

* Other arguments of program:
  * outputPath: the path in which the file with results is written (put . to write in the same directory of the program!).
  * timestepUntilCheckVar: program checks the predictions of varToCheck (explained next) from timestep 1 until timestep timestepUntilCheckVar.
    * timestepUntilCheckVar must be between 1 and the maximum timestep for which there are predictions in the prediction files of filesToCompare.csv!!
  * minTimestepLengthSeries: minimum size of the time-series (in the files with true values) that program considers for getting the statistics.
  * maxTimestepLengthSeries: maximum size of the time-series (in the files with true values) that program considers for getting the statistics.
  * varToCheck: must be the same variable that is in the prediction files of filesToCompare.csv (in the given example it would be X).

* To exemplify the usage of the program, the following files are provided:
   * example_filesToCompare.csv
   * example_correctLabels_0.csv
   * example_estimatedLabels_0.csv
   * example_correctLabels_1.csv
   * example_estimatedLabels_1.csv

* By running...
```
    python compareVars.py example_filesToCompare.csv . 2 0 3 X
```

* ...the program will:
  * First of all, in all explanations given next, the program only considers the predictions for time-series with lengths between 0 and 3 (which are all situations in this example, to ease the explanation).
  * Compare the true values of X__1 with the predictions X\[1\]
    * It does this considering the true values in example_correctLabels_0.csv and respective predictions in example_estimatedLabels_0.csv and also considering the true values in example_correctLabels_1.csv and respective predictions in example_estimatedLabels_1.csv
  * Compare the true values of X__2 with the predictions X\[2\]
    * It does this considering the true values in example_correctLabels_0.csv and respective predictions in example_estimatedLabels_0.csv and also considering the true values in example_correctLabels_1.csv and respective predictions in example_estimatedLabels_1.csv
  
  * Write the results into file "output_stats.csv". This output has several statistical indicators regarding the comparisons made.
    * For example, for the comparison of X__1 with X\[1\]:
      * example_correctLabels_0.csv has 4 subjects and example_estimatedLabels_0.csv predicts correctly the value of X\[1\] in 3 subjects.
        * The only wrong prediction is bellow the true value.
      * example_correctLabels_1.csv has 4 subjects and example_estimatedLabels_1.csv predicts correctly the value of X\[1\] in 3 subjects.
        * The only wrong prediction is above the true value.
      * Therefore, considering all files with true values and respective predictions, there are 8 values of X__1, for which there are 6 correct predictions. From the 2 wrong predictions, one is above the true value and the other is bellow the true value.
        * Therefore:
          * The accuracy is 6/8=0.75 (or 75%).
          * The % of predictions above is 1/8=0.125 (or 12.5%).
          * The % of predictions bellow is 1/8=0.125 (or 12.5%).

    * The 1st quartile for a variable X in timestep t is obtained considering all values of X__t in the files with the true values (files example_correctLabels_0.csv and example_correctLabels_1.csv in the given example). 
      * Then, given this quartile, referred as Q1 in the next table, each prediction (in the files example_estimatedLabels_0.csv and example_estimatedLabels_1.csv of the given example) is classified as True Positive (TP), False Negative (FN), False Positive (FP) and True Negative (TN) with the following table:

                                                 Predicted
                                    | prediction<=Q1 | prediction>Q1   
                    ----------------+----------------+----------------
                          true<=Q1  |       TP       |      FN
                    True -----------+----------------+----------------
                          true>Q1   |       FP       |      TN        

      * Having all TP, FN, FP and TN determined for the predictions of a variable X in timestep t, the respective sensitivity, specificity and AUC are determined (using standard expressions).
  
* A detailed explanation of the indicators calculated in this program is provided in the Master's Thesis of Tiago Leao.
  * See: *Section 7.2.1 Prediction of the variables’ values*
  
* Run "python compareVars.py -h" to get usage of program.

* Run "python compareVars.py -e" to get example of filesToCompare.csv.


## File getParentsCountsOfTimesteps.py

* The program receives as arguments:
  * parentsToCheck.csv: a line with some variables' names (either dynamic or static variables).
  * dbnsToUse.csv: a file with names of files in which there are stored sdtDBNs.
    * It has multiple lines. The program will make the counts for the sets of DBNs in each line.
      * Each line must have a tag associated, which is done by putting the names of the DBNs of each line always in the format tag_someDesiredName.
  * timestepToCheck: the desired timestep.
  
* The program counts, considering the DBNs in dbnsToUse.csv, the number of children each variable from parentsToCheck.csv has in the timestep timestepToCheck.

* The DBNs stored and whose filenames are put in the input file dbnsToUse.csv must be sdtDBNs.
  * The sdtDBN framework was developed in the Master's Thesis of Tiago Leao.
    * Check the sdtDBN webpage: [https://ttlion.github.io/sdtDBN/](https://ttlion.github.io/sdtDBN/).

* For this program to work, a file named sdtDBN_v0_0_1.jar must be given in the same directory of the file getParentsCountsOfTimesteps.py.
  * The file sdtDBN_v0_0_1.jar has the latest version of the sdtDBN program (also available in the [webpage](https://ttlion.github.io/sdtDBN/) previously mentioned).

* To exemplify the usage of the program, there are provided the files:
  * example_parentsToCheck.csv
  * example_dbnsToUse.csv

* The file example_dbnsToUse.csv uses three files with DBNs, also provided:
  * tag1_someStoredDBN1.txt
  * tag2_someStoredDBN2.txt
  * tag2_someOtherStoredDBN2.txt

* Although having different names, the files tag1_someStoredDBN1.txt, tag2_someStoredDBN2.txt and tag2_someOtherStoredDBN2.txt store the same sdtDBN, which is the following:

<p align="center" id="ref_examplefile_WithStoredDBN">
  <img alt="Graphical display of the example sdtDBN" src="example_figStoredDBN.png" style="width: 60vw; min-width: 330px;">
  <br> <em> Figure 1: Graphical display of the example sdtDBN.</em>
</p>

* See the [sdtDBN webpage](https://ttlion.github.io/sdtDBN/) for details on how to get the graphical display from the given files with stored sdtDBNs!

<!-- This graphical display can be obtained by running either of these instructions (check the [sdtDBN webpage](https://ttlion.github.io/sdtDBN/)):

```
java -jar sdtDBN_v0_0_1.jar -fromFile tag1_someStoredDBN1.txt -d | dot -Tpng -o tag1_someStoredDBN1.png

java -jar sdtDBN_v0_0_1.jar -fromFile tag2_someStoredDBN2.txt -d | dot -Tpng -o tag2_someStoredDBN2.png

java -jar sdtDBN_v0_0_1.jar -fromFile tag2_someOtherStoredDBN2.txt -d | dot -Tpng -o tag2_someOtherStoredDBN2.png
``` -->

* As the input file example_dbnsToUse.csv has

```
tag1_someStoredDBN1.txt
tag2_someStoredDBN2.txt,tag2_someOtherStoredDBN2.txt
```

* the result of running

```
python getParentsCountsOfTimesteps.py example_parentsToCheck.csv example_dbnsToUse.csv 1
```

* is the following:

```
      X  Y  Z  A  B
tag1  3  1  1  1  1
tag2  6  2  2  2  2
```

* Regarding the previous result:
  * In the first line, there are the counts of timestep 1 for the sdtDBN shown in [Fig. 1](#ref_examplefile_withstoreddbn). The results are correct: X has 3 children in timestep 1, Y has 1 child in timestep 1, etc.
  * In the second line, the results are the double of the first line, because two sdtDBNs are given in the line of tag2 (see file example_dbnsToUse.csv), with both sdtDBNs being equal to [Fig. 1](#ref_examplefile_withstoreddbn).


* Run "python getParentsCountsOfTimesteps.py -h" to get usage of program.

* Run "python getParentsCountsOfTimesteps.py -eParents" to get example of parentsToCheck.csv.

* Run "python getParentsCountsOfTimesteps.py -eDBNs" to get example of dbnsToUse.csv.


## File getCountsOfRelations.py

* The program receives as arguments:
  * parentsToCheck.csv: a line with some variables' names (either dynamic or static variables).
  * dbnsToUse.csv: a file with names of files in which there are stored sdtDBNs.
    * It has multiple lines.
      * Each line must have a tag associated, which is done by putting the names of the DBNs of each line always in the format tag_someDesiredName.
      * The program makes the counts considering all DBNs in all lines of dbnsToUse.csv, and displays all analyzed tags in the end of execution.
  * timestepInit: timestep in which relations among variables start being considered.
  * timestepEnd: timestep in which relations among variables stop being considered.

* The program counts, considering the DBNs in dbnsToUse.csv, the number of edges between each pair of variables from parentsToCheck.csv. The counts are made considering, in each DBN, all timesteps from timestepInit until timestepEnd.
  * The program provides as output a 2D matrix with the counts done for each pair of variables (the matrix is symmetric, as the direction of the edges is not important).
    * For example, if parentsToCheck.csv has variables X1, X2 and X3, the program will output a matrix with the following format:

                                   | X1 | X2 | X3
                                ---+----+----+----
                                X1 |    |    |
                                ---+----+----+----
                                X2 |    |    |
                                ---+----+----+----
                                X3 |    |    |
    
    * Each element of the previous matrix has the number of edges between the respective variables, considering all DBNs from dbnsToUse.csv, and considering, for each DBN, all timesteps between timestepInit and timestepEnd. 
      * The direction of the edges is not relevant, which makes the matrix symmetric. For example, the elements (X1,X2) and (X2,X1) of the previous matrix are the same, and each one has the total number of edges that are either X1->X2 or X2->X1, when considering all DBNs from dbnsToUse.csv, and considering, for each DBN, all timesteps between timestepInit and timestepEnd.

* The DBNs stored and whose filenames are put in the input file dbnsToUse.csv must be sdtDBNs.
  * The sdtDBN framework was developed in the Master's Thesis of Tiago Leao.
    * Check the sdtDBN webpage: [https://ttlion.github.io/sdtDBN/](https://ttlion.github.io/sdtDBN/).

* For this program to work, a file named sdtDBN_v0_0_1.jar must be given in the same directory of the file getCountsOfRelations.py.
  * The file sdtDBN_v0_0_1.jar has the latest version of the sdtDBN program (also available in the [webpage](https://ttlion.github.io/sdtDBN/) previously mentioned).

* To exemplify the usage of the program, there are provided the files:
  * example_parentsToCheck.csv
  * example_dbnsToUse.csv

* The file example_dbnsToUse.csv uses three files with DBNs, also provided:
  * tag1_someStoredDBN1.txt
  * tag2_someStoredDBN2.txt
  * tag2_someOtherStoredDBN2.txt

* Although having different names, the files tag1_someStoredDBN1.txt, tag2_someStoredDBN2.txt and tag2_someOtherStoredDBN2.txt store the same sdtDBN, which is the sdtDBN of [Fig. 1](#ref_examplefile_withstoreddbn), already used in the [explanation of the file getParentsCountsOfTimesteps.py](#file-getparentscountsoftimestepspy).

* As the input file example_dbnsToUse.csv has

```
tag1_someStoredDBN1.txt
tag2_someStoredDBN2.txt,tag2_someOtherStoredDBN2.txt
```

* the result of running

```
python getCountsOfRelations.py example_parentsToCheck.csv example_dbnsToUse.csv 0 2
```

* is the following:

```
    X   Y  Z  A  B
X   0  15  6  3  0
Y  15   0  9  0  3
Z   6   9  0  0  3
A   3   0  0  0  0
B   0   3  3  0  0
Structs checked:
['tag1', 'tag2']
```

* The previous result is as expected, because it consists of multiplying by 3 each element of the table obtained just for one DBN equal to [Fig. 1](#ref_examplefile_withstoreddbn). 
  * This is expected because the file example_dbnsToUse.csv has three DBNs equal to [Fig. 1](#ref_examplefile_withstoreddbn)!!
  
  * Note that the table obtained just for one DBN equal to [Fig. 1](#ref_examplefile_withstoreddbn) is:

                                     X  Y  Z  A  B
                                  X  0  5  2  1  0
                                  Y  5  0  3  0  1
                                  Z  2  3  0  0  1
                                  A  1  0  0  0  0
                                  B  0  1  1  0  0

    * This table is obtained from the sdtDBN of [Fig. 1](#ref_examplefile_withstoreddbn). The counts match: throughout all timesteps of the sdtDBN of [Fig. 1](#ref_examplefile_withstoreddbn), there are 5 edges between X and Y, 2 edges between X and Z, etc.

* Run "python getCountsOfRelations.py -h" to get usage of program.

* Run "python getCountsOfRelations.py -eParents" to get example of parentsToCheck.csv.

* Run "python getCountsOfRelations.py -eDBNs" to get example of dbnsToUse.csv.