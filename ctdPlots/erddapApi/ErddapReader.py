from datetime import datetime, timedelta, timezone

import pytz
from erddapClient import ERDDAP_Tabledap


def getEGErddapData(time, variable, station):
    print("Getting data from Erddap:", time)
    remote = ERDDAP_Tabledap("https://erddap.sensors.ioos.us/erddap", station)
    remote.setResultVariables(['time', 'z', variable])
    # print(remote.getURL('htmlTable'))
    # remote.clearQuery()
    beginTime = datetime.fromtimestamp(time, tz=timezone.utc) - timedelta(minutes=9)
    endTime = datetime.fromtimestamp(time, tz=timezone.utc) + timedelta(minutes=1)

    # This is the EDT time block, adjust to UTC
    tz = pytz.timezone('UTC')
    startConstraint = "time>=" + beginTime.astimezone(tz).strftime("%Y-%m-%dT%H:%M:%SZ")
    endConstraint = "time<=" + endTime.astimezone(tz).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Getting data from {startConstraint} to {endConstraint} for {variable}")
    # .orderByClosest(['station', 'time/1day'])
    try:
        response = remote.setResultVariables(['time', 'z', variable]).addConstraint(startConstraint).addConstraint(
            endConstraint).getData('csvp')
        # print(response)
        responseCSV = response
        # Now split
        responseCSV = responseCSV.split("\n")
        #for x in responseCSV:
        #   print(x)
        print("Done Getting data from Erddap")
    except:
        print("-----------------------------------------------")
        print("Error with this request!!")
        print(f"{time}, {variable}, {station}")
        return None
    return responseCSV


def testinggetErddapData():
    remote = ERDDAP_Tabledap('https://coastwatch.pfeg.noaa.gov/erddap', 'cwwcNDBCMet')
    remote.setResultVariables(['station', 'time', 'atmp'])
    print(remote.getURL('htmlTable'))
    remote.clearQuery()
    responseCSV = (
        remote.setResultVariables(['station', 'time', 'atmp'])
        .addConstraint('time>=2020-12-29T00:00:00Z')
        .addConstraint('time<=2020-12-31T00:00:00Z')
        .orderByClosest(['station', 'time/1day'])
        .getData('csvp'))
    print(responseCSV)


def testinggetEGErddapData():
    remote = ERDDAP_Tabledap("https://erddap.sensors.ioos.us/erddap", 'east-gooses')
    remote.setResultVariables(['time', 'sea_water_temperature '])
    print(remote.getURL('htmlTable'))
    remote.clearQuery()
    responseCSV = (
        remote.setResultVariables(['time', 'sea_water_temperature'])
        .addConstraint('time>=2022-06-22T00:00:00Z')
        .addConstraint('time<=2022-06-23T00:00:00Z')
        # .orderByClosest(['station', 'time/1day'])
        .getData('csvp'))
    print(responseCSV)
