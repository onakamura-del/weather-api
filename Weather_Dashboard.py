import requests
import pandas as pd
from datetime import datetime as dt

url_rain = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"
url_temps = "https://api-open.data.gov.sg/v2/real-time/api/air-temperature"
headers = {"X-Api-Key": "YOUR_SECRET_TOKEN"}
params = {"date": "2025-12-10"}
response = requests.get(url_temps, headers=headers,params=params)
data = response.json()
print(data)
# dictionary with dictionary {stations a dictionary with a list in it with more dictionaries,
# readings is a dictionary with a list with a dictionary for every timestamp}
def jsonToTable(data):
    """turns a json(usually one page) into a pd dataframe """
    readings_big = {}
    for reading in data["data"]["readings"]:
        readings_big[reading["timestamp"]] = reading
    stations = data["data"]["stations"]
    output = pd.DataFrame(columns=["StationID","Rain","Place","Longitude","Latitude","Time"])
    for timestamp,readings in readings_big.items():
        for i in range(len(readings["data"])):
            row = []
            row.append(readings["data"][i]["stationId"])
            row.append(readings["data"][i]["value"])
            row.append(stations[i]["name"])
            row.append(stations[i]["location"]["latitude"])
            row.append(stations[i]["location"]["longitude"])
            row.append(timestamp)
            output.loc[len(output)] = row
    output.set_index("StationID",inplace=True)
    return output

def rain_data(date):
    date = date.split("/")
    params = {"date": f"{date[2]}-{date[0]}-{date[1]}"}
    output_long_term = pd.DataFrame()
    while True:
        response = requests.get(url_rain, headers=headers,params=params)
        data = response.json()
        output_short_term = jsonToTable(data)
        output_long_term = pd.concat([output_long_term,output_short_term])
        #concatinate shortterm into long term
        #print(data["data"].keys())
        if "paginationToken" not in data["data"].keys():
            print(output_long_term)
            break
        else:
            print(data["data"]["paginationToken"])
            print(data["data"])
            params = {"paginationToken":data["data"]["paginationToken"]}
    return output_long_term
    #output.to_csv("Rainfall.csv",header=True)
def temp_data(date):
    date = date.split("/")
    params = {"date" :f"{date[2]}-{date[0]}-{date[1]}"}
    output_long_term = pd.DataFrame()
    true = True
    for i in range(0,60,5):
        minute = i%60
        hour = (i-minute)/60
        params["date"] = params["date"] + f"T{hour}:{minute}:00+8:00"
        data = requests.get(url_temps,headers=headers,params=params).json()
        output_short_term = jsonToTable(data) 
        output_long_term = pd.concat([output_long_term,output_short_term])
    return output_long_term
date = input("Enter a Time(MM/DD/YYYY):")
#rain_output = rain_data(date)
temp_output = temp_data(date)
#output = output[output["Rain"] != 0]
#rain_output.to_csv("rain_data.csv")
#temp_data.to_csv("temp_data.csv")
# # Rain measurment, Place, longtitude, Latitude, time
