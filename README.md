# nhs_covid_visualiser

## Running the nhs_covid_data_visualiser.py script to retrieve and plot regional data ##

This will print the CLI help for the script:

```
python3 .\nhs_covid_data_visualiser.py -h
```

```
usage: nhs_covid_data_visualiser.py [-h] [-d] [-r] [-D] [-n region [region ...]]
                        [-a Number] [-N] [-l] [-p] [-j [path]] [-A]

This is a command line interface (CLI) for the nhs_covid_data_visualiser module

optional arguments:
  -h, --help            show this help message and exit
  -d, --no-download     Does not attempt to update data.
  -r, --region          Reads region data.
  -D, --delta           Reads number of cases that day.
  -n region [region ...]
                        Specify the region(s).
  -a Number             Rolling average.
  -N, --normalise       Normalises the data.
  -l, --list            Lists areas that data is collected in. (default: print
                        data)
  -p, --plot            Plots the data (default: print data).
  -j [path]             outputs the data as a JSON. (default: print data)

Ethan Jones & George Ashmore, 2020-06-30
```

Note that all the arguments that could be passed in on the command line are optional.

```
python3 nhs_covid_data_visualiser.py -n "Derby" -p
```

Passing in the region Derby will plot the cumulative COVID cases for that region.

```
python3 nhs_covid_data_visualiser.py
```

The following example with plot the normalised, 5-day rolling average data for the region of Derby.
```
python .\get_json_data.py -a 5 -n "Derby" -N -p
```
If no arguments are passed, all regions' cases will be printed as a dataframe (use flag -p for plotting).
