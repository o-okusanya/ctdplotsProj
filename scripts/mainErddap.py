import logging
import os
import sys

from ctdPlots.ctdFileMgr import CTDReader
from ctdPlots.erddapApi import ErddapReader
from ctdPlots.HypoxiaUtil import HypoxiaUtil
from scripts import scriptBase


# Recursively traverse the directories for processed CTD data
def getFiles(baseDir):
    ROOT_DIR = HypoxiaUtil.getRootDir()
    localBaseDir = os.path.join(ROOT_DIR, baseDir)
    paths = []
    for root, dirs, files in os.walk(localBaseDir):
        for file in files:
            if file.lower().endswith(".cnv"):
                paths.append(os.path.join(root, file))
    return paths


def readCTDData(ctdFile):
    # Get the name of the station from the cast file
    # erdapName = CTDReader.getFileMetaData(ctdFile)
    erdapName = CTDReader.getErddapName(ctdFile)
    # Run the file
    ctdData = CTDReader.processFile(ctdFile)
    return erdapName, ctdData


# Get the data from the Erddap server
def readErddapData(firstDate, variable, station):
    erdapData = ErddapReader.getEGErddapData(firstDate, variable, station)
    if erdapData == None:
        print('No data found, go back 10 min')
        erdapData = ErddapReader.getEGErddapData(firstDate - (10 * 60), variable, station)
        if erdapData == None:
            print('No data found, go back 20 min')
            erdapData = ErddapReader.getEGErddapData(firstDate - (20 * 60), variable, station)
            if erdapData == None:
                print('No data found, go back 30 min')
                erdapData = ErddapReader.getEGErddapData(firstDate - (30 * 60), variable, station)
    return erdapData


    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)
    # logging.basicConfig(level=logging.DEBUG)
    #
    # # create console handler and set level to info
    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter("%(levelname)s - %(message)s")
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    #
    # # create error file handler and set level to error
    # logFileName = os.path.join(os.getcwd(), 'logs', logName)
    # handler = logging.FileHandler(os.path.join(logFileName + "_error.log"), "a", encoding=None, delay="true")
    # handler.setLevel(logging.INFO)
    # # formatter = logging.Formatter("%(levelname)s - %(message)s")
    # formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    #                               datefmt='%H:%M:%S')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    #
    # # create debug file handler and set level to debug
    # handler = logging.FileHandler(logFileName, "a")
    # handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter("%(levelname)s - %(message)s")
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)


def main():
    erdapLog = setupLogging("erdap.txt")
    # Get all of the casts
    ctdFiles = getFiles("CTD_Data")
    # To run one cast use this
    # ctdFiles = [r"CTD_Data\\2022-06-29 East Maintenance\\CTD Casts\\Processed CTDs\\HYP_E_01906398_2022_06_29_0003.cnv"]
    # zctdFiles = [
    #    r"CTD_Data\\2022-08-04 West Maintenance-20220805T130343Z-001\\2022-08-04 West Maintenance\\CTD Plots\\Processed Data\\HYP_W_01906398_2022_08_04_0013.cnv"]
    # r"CTD_Data\\2022-07-15 East Deployment\\CTD Casts\\Processed Data\\HYP_W_01906398_2022_07_15_0008.cnv"]
    for ctdFile in ctdFiles:
        totalRecords = 0
        print(f"Reading this CTD File {ctdFile}")
        # read this file. Return the data and the station name
        erddapName, ctdData = readCTDData(ctdFile)
        firstDate = ctdData[0, 0]  # Epoch timestamp

        # Now get the data from ERDDAP
        erdapDataArray = readErddapData(firstDate, 'sea_water_temperature', erddapName)
        if erdapDataArray is not None:
            hypoxiaPlotter.plotTemp(ctdData, erdapDataArray, erddapName)
            totalRecords += len(erdapDataArray)

        erdapDataArray = readErddapData(firstDate, 'mass_concentration_of_oxygen_in_sea_water', erddapName)
        if erdapDataArray is not None:
            hypoxiaPlotter.plotDO(ctdData, erdapDataArray, erddapName)
            totalRecords += len(erdapDataArray)

        erdapDataArray = readErddapData(firstDate, 'sea_water_practical_salinity', erddapName)
        if erdapDataArray is not None:
            hypoxiaPlotter.plotSalinity(ctdData, erdapDataArray, erddapName)
            totalRecords += len(erdapDataArray)

        erdapDataArray = readErddapData(firstDate, 'sea_water_electrical_conductivity', erddapName)
        if erdapDataArray is not None:
            hypoxiaPlotter.plotConductivity(ctdData, erdapDataArray, erddapName)
            totalRecords += len(erdapDataArray)
        erdapLog.debug(f"--CTD File {ctdFile} has {totalRecords} found in Errdap")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Starting app")
    scriptBase.setupLogging("runErrdap.log")
    main()
