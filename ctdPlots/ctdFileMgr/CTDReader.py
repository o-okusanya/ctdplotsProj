import datetime
import logging
import os
import re

import numpy as np
import pytz

from ctdPlots.ctdFileMgr.CTDMgr import CTDMgr

'''
CTD Field Data
# name 0 = timeJ: Julian Days
# name 1 = tv290C: Temperature [ITS-90, deg C]
# name 2 = c0mS/cm: Conductivity [mS/cm]
# name 3 = sal00: Salinity, Practical [PSU]
# name 4 = sbeox0Mg/L: Oxygen, SBE 43 [mg/l]
# name 5 = depSM: Depth [salt water, m], lat = 38.56
# name 6 = prdM: Pressure, Strain Gauge [db]
# name 7 = flag:  0.000e+00
OLD # name 6 = flag:  0.000e+00
'''


# tz = pytz.timezone('America/New_York')


# la.localize(yearStartDate)
def processDir(dirName):
    print(dirName)
    # Data array, first row is headers
    files = os.listdir(dirName)
    for file in files:
        if os.path.isfile(os.path.join(dirName, file)):
            print("Found a file, going to process it", file)
            return processFile(os.path.join(dirName, file))


def getHeaders(file):
    data = []
    f = open(file, "r")
    lines = f.readlines()
    for line in lines:
        if line.startswith("#"):
            p = re.compile("# name (\d) = (.*)")
            m = p.match(line)
            if m:
                # print("Group:", m.group(1), " Data:", m.group(2))
                name = m.group(1) + ":" + m.group(2)
                print(name)
                # if "Julian Days" in name:
                #    data.append(name, np.float64)
                # else:
                data.append((name, np.float64))
                # print(line, end="")
    print("data", np.shape(data))
    # print("data", data)
    # [('name', np.unicode_, 16), ('grades', np.float64, (2,))]
    # [('0:timeJ: Julian Days', <class 'numpy.int64'>), ('1:tv290C: Temperature [ITS-90, deg C]', <class 'numpy.float64'>),
    # ('2:c0mS/cm: Conductivity [mS/cm]', <class 'numpy.float64'>), ('3:sal00: Salinity, Practical [PSU]', <class 'numpy.float64'>),
    # ('4:sbeox0Mg/L: Oxygen, SBE 43 [mg/l]', <class 'numpy.float64'>), ('5:depSM: Depth [salt water, m], lat = 38.56', <class 'numpy.float64'>), ('6:flag:  0.000e+00', <class 'numpy.float64'>)]
    return np.dtype(data)


def getDate(fileName, input, startYear):
    # Exmple input for a date
    # 152.273414

    '''if input < 154:
        # 6/3/2022 This is the UTC time, CTD was calibrated at UTC for this part of the year
        tz = pytz.timezone('UTC')
        yearStartDate = datetime.datetime(2022, 1, 1, 0, 0)
        tz.localize(yearStartDate)
        start = yearStartDate + datetime.timedelta(days=input)
    else:
    '''
    # Anything after this date 6/3/2022 is in EST
    if startYear == '2024':
        appTz = pytz.timezone('UTC')
    else:
        appTz = pytz.timezone('America/New_York')
    yearStartDate = datetime.datetime(int(startYear), 1, 1, 0, 0, tzinfo=appTz)
    # tz.localize(yearStartDate)
    hourAdj = CTDMgr.getOffset(fileName)

    start = yearStartDate + datetime.timedelta(hours=hourAdj, days=input)
    # The datetime has been localized at this point. Use epochtime from here out to be consistent
    # Fine level debugging of each data point
    logging.debug(f"First timestamp: {input},{start.timestamp()} {start}")
    return start.timestamp()


# def getFileMetaData(file):
#     if file.__contains__("HYP_E"):
#         return "east-gooses"
#     elif file.__contains__("HYP_W"):
#         return "west-gooses"
#     return "lower-choptank"

''' Get the ERDDAP name based on the NOAA name'''


def getErddapName(file):
    noaaId = getNcboName(file)
    if noaaId == "lower-choptank":
        return "zq_sd2023 - 2023"
    elif noaaId == "lower-potomac":
        return "lower-potomac-2023"
    elif noaaId == "mid-bay":
        return "mid-bay-2023"
    return None


def getNcboName(file):
    path = os.path.normpath(file)
    dirs = path.split(os.sep)
    noaaId = dirs[len(dirs) - 2]
    if noaaId == 'dataFiles':
        # This is the generic section, read the file name
        # CHOMA_01_Post_2023_06_27_0025
        filename = os.path.basename(file)
        if filename.startswith('CHOMA'):
            return 'lower-choptank'
        elif filename.startswith('CB5MH'):
            return 'mid-bay'
        elif filename.startswith('POTMH_01'):
            return 'lower-potomac'
        elif filename.startswith('POTMH_02'):
            return 'herring-creek'
        elif filename.startswith('POTMH_03'):
            return 'clements-island'
        elif filename.startswith('CB4MH_01'):
            return 'sharps-island'
        elif filename.startswith('CHOMH2_01'):
            return 'chlora-point'
        elif filename.startswith('CHOMH1_01'):
            return 'lower-choptank'
        return 'unknown'
    return noaaId


def getFileTiming(file):
    filename = os.path.basename(file)
    pattern = "_Pre_"
    match = re.search(pattern, filename)
    if match:
        return "Pre"
    return "Post"


def getFileSubname(file):
    filename = os.path.basename(file)
    pattern = "_(\d+)\."
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    return "001"


def getYearFromFilename(file):
    filename = os.path.basename(file)
    preStr = r"_Pre_(\d\d\d\d)_"
    postStr = r"_Post_(\d\d\d\d)_"
    pre = re.search(preStr, filename)
    if pre:
        x = pre.group(1)
        return x

    post = re.search(postStr, filename)
    if post:
        x = post.group(1)
        return x

    return None


def processFile(file):
    # Read the headers from the file
    dType = getHeaders(file)
    depth = 5
    year = getYearFromFilename(file)
    # dtype = [('name', 'S10'), ('height', float), ('age', int)]
    # Open the file for reading the data
    f = open(file, 'r')
    lines = f.readlines()
    allLines = []
    bottomDepth = findLowestPoint(lines, file, depth, year)
    for line in lines:
        if not line.startswith("#") and not line.startswith("*"):
            values = line.split()
            # The date is in a different format, convert to a datetime object
            values[0] = getDate(file, float(values[0]) - 1, year)
            fdepth = float(values[depth])  # Get the depth from the file
            # Start saving data after three meters adn stop when it comes up
            if fdepth >= 0.9:
                # print(fdepth)
                if fdepth >= bottomDepth:
                    print(f"DePTH HAS FLIPPED {fdepth} {bottomDepth}")
                    break  # End the loop, we have reached the bottom
                else:
                    # Still going down, add it
                    allLines.append([float(item) for item in values])
            # ctdData..append(values)
    # ctdArray = np.array(ctdData, dtype=dType)
    # dt = np.dtype(('0', np.float64), ('1', np.float64, (2,)), ('2', np.float64, (2,)), ('3', np.float64, (2,)), ('4', np.float64, (2,)), ('5', np.float64, (2,)), ('6', np.float64, (2,)))
    ctdData = np.array(allLines)  # , dtype=dt)
    print("Data structure shape read in:", np.shape(ctdData))

    # print(ctdData[:, 0])
    return ctdData


def findLowestPoint(lines, file, depth, year):
    bottomDepth = 0
    for line in lines:
        if not line.startswith("#") and not line.startswith("*"):
            values = line.split()
            # The date is in a different format, convert to a datetime object
            values[0] = getDate(file, float(values[0]) - 1, year)
            # Append the data to the array
            fdepth = float(values[depth])  # Get the depth from the file
            # Start saving data after three meters adn stop when it comes up
            if fdepth > bottomDepth:
                bottomDepth = fdepth

    return bottomDepth


'''
def processFile(file):
    # Read the headers from the file
    dType = getHeaders(file)
    ctdData = np.empty([len(dType)]) #, dtype=dType)
    # dtype = [('name', 'S10'), ('height', float), ('age', int)]
    # Open the file for reading the data
    f = open(file, 'r')
    lines = f.readlines()
    for line in lines:
        if not line.startswith("#") and not line.startswith("*"):
            values = line.split()
            # The date is in a different format, convert to a datetime object
            values[0] = getDate(values[0])
            # Append the data to the array
            # ctdData = np.concatenate((ctdData, [values]))
            values[1] = float(values[1])
            values[2] = float(values[2])
            values[3] = float(values[3])
            values[4] = float(values[4])
            values[5] = float(values[5])
            values[6] = float(values[6])
            print(values)
            npv = np.array((values[0], float(values[1]),float(values[2]),float(values[3]),float(values[4]),float(values[5]),float(values[6])))
            print(np.shape(npv))
            print(np.shape(ctdData))
            np.vstack(ctdData, npv)
            # ctdData..append(values)
    # ctdArray = np.array(ctdData, dtype=dType)
    print("Data structure shape read in:", np.shape(ctdData))
    # print(ctdData[:, 0])
    compareFileWithErddap(ctdData)
'''
