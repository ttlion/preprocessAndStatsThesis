# Files for preprocessing time-series data

## File discretize_dates.py

* Converts data provided as observations in certain dates into time-series.

* Outputs the same dataset but with dates (dd/mm/yyyy) discretized into timesteps (0, 1, 2, ...).

* It allows selecting the number of months between consecutive timesteps (defined as deltaT in program's usage).
  * If option2 = 1 only keeps timesteps separated by the specified number of months
    * For example, if patient has consultations in 01/01/2000, 01/04/2000, 01/05/2000, 01/07/2000, and choosing deltaT=3 (3 months interval).
      * With option2 = 1 only the data from 01/01/2000 and 01/04/2000 and 01/07/2000 is kept (as timesteps 0, 1 and 2).
  * If option2 = 0, program only uses the defined deltaT if there is not data between the specified timesteps.
    * For the same example where patient has consultations in 01/01/2000, 01/04/2000, 01/05/2000, 01/07/2000, and choosing deltaT=3 (3 months interval).
      * With option2 = 0 all data is kept (as timesteps 0, 3, 4 and 6), program chooses deltaT=1 as it is the maximum deltaT possible to keep all data.
  * Usually, option2 = 1 is the desired!

* It allows defining if timesteps in which there is no consultation are filled with nearest consultation or with ?
  * For example, if consultations in 01/01/2000 and 01/07/2000 and defining deltaT=3 (3 months interval).
    * Timestep 1 is the data from 01/04/2000, which does not exist.
      * If option1 = 0, timestep 1 is filled also with data from 01/01/2000.
      * If option1 = 1, timestep 1 is filled with ?

* Example input file: example_file_dates.csv

* Run "python discretize_dates.py -h" to get usage of program, with description of inputs.

* Run "python discretize_dates.py -e" to get another example of input file.

## File split_beforeVSafterNIV.csv

* Converts data provided as observations in certain dates (dd/mm/yyyy) into time-series. It creates, for each id, two time-series, one before NIV and other after NIV.
  * Note: NIV is used because file was created in context of ALS disease, but NIV can be seen simply as a date according to which the time-series should be separated!

* The *first column of input table* must be named REF, having the *patients' ids*.

* For each id, there must be provided the *consultation dates in the second column of input table*.
  * Each patient can have multiple consultations (in different dates), but only one NIV date.

* For each id, there must be given the *NIV date in the last column of the input table*.
  * For a certain id, the NIV date must be the same in all consultations (in all rows corresponding to that id, in the input table).

* For each id, there is created a time-series before and a time-series after NIV. Each time-series starts in timestep 0, and consecutive timesteps are separated by a number of months defined by the user (defined as deltaT in program's usage).
  * For example, if patient has consultations in 01/01/2000, 01/03/2000, 01/05/2000, 01/07/2000, has NIV in 01/04/2000, and choosing deltaT=2 (2 months interval).
  * The time-series with data before NIV is composed by data of the consultations in 01/01/2000, 01/03/2000, corresponding to timesteps 0 and 1 before NIV.
  * The time-series with data after NIV is composed by data of the consultations in 01/05/2000, 01/07/2000, corresponding to timesteps 0 and 1 after NIV.

* It allows defining if timesteps in which there is no consultation are filled with previous consultation or with ?
  * For example, if consultations in 01/03/2000 and 01/07/2000, NIV date in 01/01/2000, and defining deltaT=2 (2 months interval).
    * Only series after NIV is created (only consultations after NIV exist).
      * Timestep 0 is 01/03/2000 (first consultation after NIV).
      * Timestep 1 is 01/05/2000 (2 months after).
        * It is filled with ? if option=1. Is filled with data of timestep 0 if option=0.
      * Timestep 2 is 01/07/2000 (2 months after).

* Example input file: example_file_to_split.csv

* Run "python split_beforeVSafterNIV.py -h" to get usage of program, with description of inputs.

* Run "python split_beforeVSafterNIV.py -e" to get example of input file.


## File fill_data_LOCF.py

* Fills time-series using LOCF.

* Performs usual LOCF iteration and then a backwards iteration.
  * If a_0=?, a_1=8, a_2=9, a_3=? program does:
    * First iteration fills a_3=9 (usual LOCF).
    * Backwards iterations fills a_0=8.

* Can remove subjects where, after filling, at least one variable still has missing data.
  * If option1=1, program *REMOVES* subjects where, after filling, at least one variable still has missing data.
  * If option1=0, program *DOES NOT* remove subjects where, after filling, at least one variable still has missing data.

* User must introduce timestepMax, which is the maximum timestep for all time-series.
  * For example, if timestepMax=2, program will only keep timesteps 0, 1 and 2 of all time-series.
  * Note: if do not want to have a maximum timestep, just put an enormous number here!

* CSV input file should be with "," instead of ";" !!

* Example input file: example_file_to_fill.csv

* Program can also discretize variables into bins if desired!
  * Example discretization file: example_file_to_fill_discr.csv

* Run "python fill_data_LOCF.py -h" for usage.

* Run "python fill_data_LOCF.py -e" for example of input file format.

* Run "python fill_data_LOCF.py -d" for explanation of the discretization file.

## File fill_data_linInterpol.py

* Fills time-series using linear interpolation and extrapolation.
    * Interpolation fills data between certain timesteps, for example, if a_0=8, a_1=?, a_2=10, program fills a_1=9.
    * Extrapolation fills data that is not between timesteps, for example, if a_0=8, a_1=9, a_2=?, program fills a_2=10.

* Can remove subjects where, after filling, at least one variable still has missing data.
  * If option1=1, program *REMOVES* subjects where, after filling, at least one variable still has missing data.
  * If option1=0, program *DOES NOT* remove subjects where, after filling, at least one variable still has missing data.

* User must introduce timestepMax, which is the maximum timestep for all time-series.
  * For example, if timestepMax=2, program will only keep timesteps 0, 1 and 2 of all time-series.
  * Note: if do not want to have a maximum timestep, just put an enormous number here!

* CSV input file should be with "," instead of ";" !!

* Example input file: example2_file_to_fill.csv

* Program can also discretize variables into bins if desired!
  * Example discretization file: example_file_to_fill_discr.csv

* Run "python fill_data_linInterpol.py -h" for usage.

* Run "python fill_data_linInterpol.py -e" for example of input file format.

* Run "python fill_data_linInterpol.py -d" for explanation of the discretization file.

## File prune_REFs.py

* Given two datasets, checks which ids are in both datasets and keeps the data of those ids from the second dataset.

* Ids must be given in the first column of both datasets, which must be named REF.

* For example, using two datasets, dataset1 and dataset2.
  * If dataset1 has data for REFs 1, 2 and 3, while dataset2 has data for REFs 2, 3 and 4, 
    * The program will output the data of REFs 2 and 3 that is dataset2.

* Example input files: example_file_dataset1.csv and example_file_dataset2.csv

* Run "python prune_REFs.py -h" for usage.

* Run "python prune_REFs.py -e" for example of input files format.