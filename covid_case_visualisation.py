"""
A Python module that ingests COVID-19 case data and visualises it using matplotlib.
- George Ashmore <gashmore1@sheffield.ac.uk>
- Ethan Jones <ejones18@sheffield.ac.uk>
- First authoured 2020-06-09
"""
import json
import argparse
import datetime
import time
import os

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from uk_covid19 import Cov19API

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

def add_to_geo_json_eer(data, geo_json, case_type):
    """
    Adds the COVID data of the corresponding EER region in the geo_json file.
    """
    for region in geo_json['features']:
        try:
            eer_list = np.array(data[["Date",region['properties']['eer16nm']]].values)
            not_nan_array = ~ np.isnan([i[1] for i in eer_list])
            eer_list = eer_list[not_nan_array]
            eer_list = {datetime.datetime.timestamp(i[0]):i[1] for i in eer_list}
            region['properties'][case_type] = eer_list
        except:
            region['properties'][case_type] = [0]
    return geo_json

def add_to_geo_json_lad(data, geo_json, case_type):
    """
    Adds the COVID data of the corresponding LAD region in the geo_json file.
    """
    for region in geo_json['features']:
        try:
            lad_list = np.array(data[["Date",region['properties']['lad17nm']]].values)
            not_nan_array = ~ np.isnan([i[1] for i in lad_list])
            lad_list = lad_list[not_nan_array]
            lad_list = {datetime.datetime.timestamp(i[0]):i[1] for i in lad_list}
            region['properties'][case_type] = lad_list
        except:
            region['properties'][case_type] = [0]
    return geo_json

def plot_data(data):
    """
    Plots the data as a line graph.
    """
    names = list(data.keys())[1:]
    data.plot(y=names, x='Date', kind='line')
    plt.show()

def get_all_region_data(data, cumulative=True):
    """
    Fetches all regional COVID-19 data.
    """
    regional_data = {}
    region_names = set()
    for i in data['data']:
        region_names.add(i['areaName'])
        date = i['date']
        date = datetime.datetime(*(time.strptime(i['date'], '%Y-%m-%d'))[0:6])
        area_name = i['areaName']
        if not date in regional_data:
            regional_data[date] = {}
        if cumulative:
            regional_data[date][area_name] = i['cumCasesBySpecimenDate']
        else:
            regional_data[date][area_name] = i['newCasesBySpecimenDate']
    regional_data_frame = pd.DataFrame(regional_data)
    regional_data_frame = regional_data_frame.transpose()
    regional_data_frame = regional_data_frame.iloc[::-1].reset_index(drop=False)
    regional_data_frame = regional_data_frame.rename(columns={"index":"Date"})
    return regional_data_frame

def normalised_data(data):
    """
    Normalises the COVID-19 data.
    """
    no_date = data.drop(['Date'], axis=1)
    min = no_date.min().min()
    max = no_date.max().max() - min
    def f(x):
        if type(x) == float:
            return (x-min)/max
        else:
            return x
    return data.applymap(f)

def get_regional_data(offline=False):
    """
    Fetches the regional json file if timestamp isn't the same as new json data.
    """
    try:
        with open('regional_covid_data.json', 'r') as json_file:
            regional_data = json.load(json_file)
            path_to_regional_file = os.path.join(ROOT_PATH, "regional_covid_data.json")
            time_created = os.path.getmtime(path_to_regional_file)
            time_created = datetime.datetime.fromtimestamp(time_created)
            current_time = datetime.datetime.now()
            delta_t = (current_time - time_created)
            time_out = datetime.timedelta(days=2)
            if delta_t > time_out and not offline:
                print("Reacquiring regional data...")
                raise
    except:
        try:
            print("Fetching new regional data...")
            regional_data = get_regional_data_from_api()
        except:
            print("Failed to acquire data, running in offline mode.")
            regional_data = get_regional_data(True)
    return regional_data

def get_ltla_data(offline=False):
    """
    Fetches the LTLA json file if timestamp isn't the same as new json data.
    """
    try:
        with open('ltlas_covid_data.json', 'r') as json_file:
            ltla_data = json.load(json_file)
            path_to_ltla_file = os.path.join(ROOT_PATH, "ltlas_covid_data.json")
            time_created_ = os.path.getmtime(path_to_ltla_file)
            time_created = datetime.datetime.fromtimestamp(time_created_)
            current_time = datetime.datetime.now()
            delta_t = (current_time - time_created)
            time_out = datetime.timedelta(days=2)
            if delta_t > time_out and not offline:
                print("Reacquiring ltla data...")
                raise
    except:
        try:
            print("Fetching new ltla data...")
            ltla_data = get_ltla_data_from_api()
        except:
            print("Failed to acquire data, running in offline mode.")
            ltla_data = get_ltla_data(True)
    return ltla_data

def get_ltla_data_from_api():
    """
    Fetches the LTLA data from the .gov.uk COVID API.
    """
    all_ltla = ["areaType=ltla"]
    cases_and_deaths = {"date": "date",
                        "areaName": "areaName",
                        "areaCode": "areaCode",
                        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
                        "cumCasesBySpecimenDate": "cumCasesBySpecimenDate",
                        "newDeathsByDeathDate": "newDeaths28DaysByDeathDate",
                        "cumDeathsByDeathDate": "cumDeaths28DaysByDeathDate"
                        }
    api = Cov19API(
        filters=all_ltla,
        structure=cases_and_deaths,
    )
    data = api.get_json()
    with open('ltlas_covid_data.json', 'w') as json_file:
        json.dump(data, json_file)
    return data

def get_regional_data_from_api():
    """
    Fetches the regional data from the .gov.uk COVID API.
    """
    all_regions = ["areaType=region"]
    cases_and_deaths = {"date": "date",
                        "areaName": "areaName",
                        "areaCode": "areaCode",
                        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
                        "cumCasesBySpecimenDate": "cumCasesBySpecimenDate",
                        "newDeathsByDeathDate": "newDeaths28DaysByDeathDate",
                        "cumDeathsByDeathDate": "cumDeaths28DaysByDeathDate"
                        }
    api = Cov19API(
        filters=all_regions,
        structure=cases_and_deaths,
    )
    data = api.get_json()
    with open('regional_covid_data.json', 'w') as json_file:
        json.dump(data, json_file)
    return data

def get_all_lad_data(data, cumulative=True):
    """
    Fetches all regional data.
    """
    regional_data = {}
    region_names = []
    for i in data['data']:
        if not i['areaName'] in region_names:
            region_names.append(i['areaName'])
        date = i['date']
        date = datetime.datetime(*(time.strptime(i['date'], '%Y-%m-%d'))[0:6])
        area_name = i['areaName']
        if not date in regional_data:
            regional_data[date] = {}
        if cumulative:
            regional_data[date][area_name] = i['cumCasesBySpecimenDate']
        else:
            regional_data[date][area_name] = i['newCasesBySpecimenDate']
    regional_data_frame = pd.DataFrame(regional_data)
    regional_data_frame = regional_data_frame.transpose()
    regional_data_frame = regional_data_frame.iloc[::-1].reset_index(drop=False)
    regional_data_frame = regional_data_frame.rename(columns={"index":"Date"})
    return regional_data_frame

def parse_options():
    """
    Parse command line options.
    """
    parser = argparse.ArgumentParser(description=("This is a command line interface (CLI) for "
                                                  "the nhs_covid_data_visualiser module"),
                                     epilog="Ethan Jones & George Ashmore, 2020-06-30")
    parser.add_argument("-d", "--no-download", dest="offline", action="store_true",
                        required=False,
                        help="Does not attempt to update data.")
    parser.add_argument("-r", "--region", dest="region", action="store_true",
                        required=False,
                        help="Reads region data.")
    parser.add_argument("-D", "--delta", dest="delta", action="store_false",
                        required=False,
                        help="Works out the delta cases.")
    parser.add_argument("-n", action="store", type=str, dest="region_name",
                        metavar="region",
                        nargs='+',
                        required=False,
                        help="Specify the region(s).")
    parser.add_argument("-a", dest="average", action="store",
                        metavar="Number",
                        type=int,
                        required=False,
                        help="Rolling average.")
    parser.add_argument("-N", "--normalise", action="store_true", dest="normalised",
                        required=False,
                        help="Normalises the data.")
    parser.add_argument("-l", "--list",
                        action="store_true", dest="list", required=False,
                        help="Lists areas that data is collected in. (default: print data)")
    parser.add_argument("-p", "--plot", action="store_true", dest="plot_data",
                        required=False,
                        help="Plots the data (default: print data).")
    parser.add_argument("-j", action="store", type=str, metavar="path", dest="json_save",
                        nargs='?',
                        default=False,
                        required=False,
                        help="outputs the data as a JSON. (default: print data)")
    options = parser.parse_args()
    return options

if __name__ == "__main__":
    OPTIONS = parse_options()
    REGIONAL_DATA = get_regional_data(OPTIONS.offline)
    LTLA_DATA = get_ltla_data(OPTIONS.offline)
    if OPTIONS.region:
        DATA_FRAME = get_all_region_data(REGIONAL_DATA, OPTIONS.delta)
    else:
        DATA_FRAME = get_all_lad_data(LTLA_DATA, OPTIONS.delta)
    if OPTIONS.region_name:
        REGIONS_TO_KEEP = {"Date", *OPTIONS.region_name}
        DATA_FRAME.drop(DATA_FRAME.columns.difference(REGIONS_TO_KEEP), 1, inplace=True)
    elif OPTIONS.list:
        for name in list(DATA_FRAME.columns[1:]):
            print(name)
    if OPTIONS.average:
        DATA_FRAME.iloc[:, 1:] = DATA_FRAME.iloc[:, 1:].rolling(abs(OPTIONS.average),
                                                                min_periods=1, center=True).mean()
    if OPTIONS.normalised:
        DATA_FRAME = normalised_data(DATA_FRAME)
    if OPTIONS.plot_data:
        plot_data(DATA_FRAME)
    elif OPTIONS.json_save != False:
        path = "../LAD.json"
        if OPTIONS.region:
            path = "../EER.json"
        file = open(path,"r")
        data = json.load(file)
        data_type = "Total"
        if OPTIONS.delta:
            data_type = "Delta"
        if OPTIONS.region:
            json_data = add_to_geo_json_eer(DATA_FRAME, data, data_type)
        else:
            json_data = add_to_geo_json_lad(DATA_FRAME, data, data_type)
        if OPTIONS.json_save != None:
            try:
                JSON_FILE_OUTPUT = open(OPTIONS.json_save, "w")
                json.dump(json_data, JSON_FILE_OUTPUT)
            except:
                print("Could not save to file")
        else:
            print(json_data)
    elif not OPTIONS.list:
        print(DATA_FRAME)
