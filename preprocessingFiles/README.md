# Files for preprocessing time-series data

## File discretize_dates.py

* Converts data provided as observations in certain dates into time-series

* Outputs the same dataset but with dates (dd/mm/yyyy) discretized into timesteps (0, 1, 2, ...)

* It allows selecting the number of months between consecutive timesteps (defined as deltaT in program usage)
  * If option2 = 1 only keeps timesteps separated by the specified number of months
    * For example, if patient has consultations in 01/01/2000, 01/04/2000, 01/05/2000, 01/07/2000, and choosing deltaT=3 (3 months interval)
      * With option2 = 1 only the data from 01/01/2000 and 01/04/2000 and 01/07/2000 is kept (as timesteps 0, 1 and 2)
  * If option2 = 0, program only uses the defined deltaT if there is not data between the specified timesteps
    * For the same example where patient has consultations in 01/01/2000, 01/04/2000, 01/05/2000, 01/07/2000, and choosing deltaT=3 (3 months interval)
      * With option2 = 0 all data is kept (as timesteps 0, 3, 4 and 6), program chooses deltaT=1 as it is the maximum deltaT possible to keep all data.
  * Usually, option2 = 1 is the desired!

* It allows defining if timesteps in which there is no consultation are filled with nearest consultation or with ?
  * For example, if consultations in 01/01/2000 and 01/07/2000 and defining deltaT=3 (3 months interval)
    * Timestep 1 is the data from 01/04/2000, which does not exist
      * If option1 = 0, timestep 1 is filled also with data from 01/01/2000
      * If option1 = 1, timestep 1 is filled with ?

* Run "python discretize_dates.py -h" to get usage of program, with description of inputs

* Run "python discretize_dates.py -e" to get example of input file

## File fill_data.py

* Fills time-series using LOCF
* Performs usual LOCF iteration and then a backwards iteration
  * If a_0=?, a_1=8, a_2=9, a_3=? program does:
    * First iteration fills a_3=9 (usual LOCF)
    * Backwards iterations fills a_0=8
* Removes subjects where after filling at least one variable still has missing data
  * Comment line 261 to avoid this behavior

* CSV input file should be with "," instead of ";"

* Run "python fill_data.py -h" for usage

* Run "python fill_data.py -e" for example of input file format

* Program also discretizes variables into bins if desired
  * Run "python fill_data.py -d" for example of discretization file


## File fill_data_linInterpol.py

* Fills time-series using linear interpolation and extrapolation
    * Interpolation fills data between certain timesteps, for example, if a_1=8, a_2=?, a_3=10, program fills a_2=9
    * Extrapolation fills data that is not between timesteps, for example, if a_1=8, a_2=9, a_3=?, program fills a_3=10

* Removes subjects where after filling at least one variable has missing data
  * Comment line 322 to avoid this behavior

* CSV input file should be with "," instead of ";"

* Run "python fill_data_linInterpol.py -h" for usage

* Run "python fill_data_linInterpol.py -e" for example of input file format

* Program also discretizes variables into bins if desired
  * Run "python fill_data_linInterpol.py -d" for example of discretization file