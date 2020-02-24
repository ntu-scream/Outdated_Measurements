# Outdated measurement code versions

### Published Apr 20, 2019

Older GUI for various measurements.  This version does not use pymeasure or multiprocessing.  The save function is does not save as CSV files.

All programs have been tried on the probe stations and have proven functional.  
This code has several improvements over the even older versions.

- improves run time with matplotlib animation function
- improved quit function that resets machines and kills all threads
- improved directory settings, default directory is ~/docs/measurements
- Built USMR and SOT USMR code
- toggle buttons for field output directions and loops
- dictionaries used to define default parameters for easy updates going forward
- better labeling and saved data
