# HyTI Jitter Metrology
Code for validation and verification of an Optical Jitter Metrology system tested on the HyperSpectral Thermal Imager CubeSat.
The list of configurations is in this table below: 

| Configuration Number | Sources | Number of Trials |
|----------------------|---------|------------------|
| 1                    | Air bearing off, Electronics on, Payload off, ADCS off |5                  |
| 2                    | Air bearing off, Electronics on, Payload on, ADCS off  |5                  |
| 3                    | Air bearing on, Electronics on, Payload off, ADCS Electronics on | 4                  |
| 4                    |         |                  |
| 5                    |         |                  |
| 6                    |         |                  |
| 7                    |         |                  |

The "data" directory contains the csv files of the "raw data" collected by the metrology system. 
It also contains the csv files for each configuration that has the identified peaks, amplitude, FWHM, and their respective variances. 
These are labeled as "Configuration_#_dir.csv", where the # refers to the configuration number presented in the above table and dir refers to the direction of the data (either x or y). 

The "code" directory contains the Python files needed to obtain the data.
