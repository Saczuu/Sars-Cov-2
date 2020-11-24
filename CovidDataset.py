import pandas as pd
import numpy as np

def generateDataset():
    """Function generea lagged Covid-19 statistic for Poland.
    Add laged data for each day and name of day of week; return pandas DataFrame.

    Result:
        Output file with laged statistic for seleted countries.
    """
    # Read data from github
    data=pd.read_csv(
        'https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv'
    , sep=",")

    # Get data only for selected country
    result = data[data["Country"] == "Poland"]


    # Remove all date without new cases at begining of year
    start_date = 1
    for row in range(1, result.shape[0]):
        if result.iloc[row]["Confirmed"] == 0:
            start_date += 1
        else:
            break
    result = result.tail(-start_date)

    # Reformat date
    result["Date"] = pd.to_datetime(result["Date"], format='%Y-%m-%d')

    # Geting number of day in week
    result["DayOfWeek"] = result["Date"].dt.dayofweek

    #Change confirmend form totlan number into day specifinc new cases
    for i in range(result.shape[0]-1, 1, -1):
        result["Confirmed"].iat[i] -= result["Confirmed"].iat[i-1]


    # Add lag to each row
    for lag in range(1,8):
        empty_lagged = np.zeros(result.shape[0])
        result[("Confirmed"+str(lag))] = empty_lagged
        for row in range(lag, result.shape[0]):
            result["Confirmed"+str(lag)].iat[row] = result["Confirmed"].iat[(row-lag)]


    # Confirming type of data
    result.Confirmed1=result.Confirmed1.astype("int32")
    result.Confirmed2=result.Confirmed2.astype("int32")
    result.Confirmed3=result.Confirmed3.astype("int32")
    result.Confirmed4=result.Confirmed4.astype("int32")
    result.Confirmed5=result.Confirmed5.astype("int32")
    result.Confirmed6=result.Confirmed6.astype("int32")
    result.Confirmed7=result.Confirmed7.astype("int32")


    # Changing number of day into polish name of day
    day_list = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i in range(len(day_list)):
        result["DayOfWeek"] = result["DayOfWeek"].replace(i, day_list[i])


    # Reordering collumns for output 
    result=pd.DataFrame(result[["Date","DayOfWeek","Country",
    "Confirmed","Confirmed1","Confirmed2","Confirmed3","Confirmed4","Confirmed5","Confirmed6","Confirmed7"
    ,"Recovered", "Deaths"]])

    # Rename collumns name to polish eqivalent
    # result=result.rename(columns={"Date":"Data","DayOfWeek":"DzienTygodnia","Country":"Kraj",
    # "Confirmed":"Zachorowalo","Confirmed1":"Zachorowalo_1","Confirmed2":"Zachorowalo_2",
    # "Confirmed3":"Zachorowalo_3","Confirmed4":"Zachorowalo_4","Confirmed5":"Zachorowalo_5",
    # "Confirmed6":"Zachorowalo_6","Confirmed7":"Zachorowalo_7","Recovered":"Wyzdrowialo", "Deaths":"Zmarlo"})
    
    return result

def saveAsCSV(dataframe, filename):
    dataframe.to_csv("./"+filename+".csv", sep=';', index=False)


def discretize(filename):
    ## ToDo assert that inputfile has thoues collumns or is in specific structure

    # List of columns to discretization
    columns_to_discretize = ['Zachorowalo', 'Zachorowalo_1', 'Zachorowalo_2', 'Zachorowalo_3',	'Zachorowalo_4', 'Zachorowalo_5', 'Zachorowalo_6', 'Zachorowalo_7', 'Wyzdrowialo',	'Zmarlo']
    # Read data from input file
    dataset = pd.read_csv(filename+".csv", sep=";")

    for column in columns_to_discretize:
        # Pick collumn
        data = dataset[column]
        # Split into 2 parts
        data_1st_wave = data[:len(data)//2]
        data_2nd_wave = data[len(data)//2:]
        # Discretize each part into 4 bins
        data_1st_wave_discretized = pd.cut(data_1st_wave, 4, labels=["Mało", "Średnio" , "Dużo", "B. dużo"])
        data_2nd_wave_discretized = pd.cut(data_2nd_wave, 4, labels=["Mało", "Średnio" , "Dużo", "B. dużo"])
        # Connect discretize data
        data_discretized_connected = data_1st_wave_discretized.append(data_2nd_wave_discretized)
        # Get location of readed collumn
        loc = dataset.columns.get_loc(column)
        # Remove orginal column
        dataset = dataset.drop([column], axis=1)
        #Insert discretized value in same place as removed column
        dataset.insert(loc, column, data_discretized_connected)


    # Save change to same file
    saveAsCSV(dataset, filename)


def generateAndDiscretize():
    generateDataset("Poland", "output")
    discretize("output")