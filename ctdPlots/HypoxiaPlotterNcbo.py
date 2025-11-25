import logging
import os
from datetime import datetime, timezone

import pytz
from dateutil.parser import parse

import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from dateutil.tz import tzfile
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox

from ctdPlots.HypoxiaUtil import HypoxiaUtil

''' Extract the values from the data and make the table

def buildTable(tableValues, colors):
    # Get the depths into an array
    dv = np.array(tableValues)
    depthValues = dv[:, 0]
    # Remove the depths and leave the other values
    plotTbl = np.delete(tableValues, np.s_[0:1], axis=1)
    tblArr = list(plotTbl)
    if len(depthValues) > 8:
        new_table = plt.table(cellText=tblArr,
                              rowLabels=depthValues,
                              colLabels=["CTD data", "Erddap data", "Difference"],
                              loc='bottom',
                              bbox=[0.0, -0.9, 1, .5],
                              cellColours=colors)

        new_table.set_fontsize(6)
    else:
        new_table = plt.table(cellText=tblArr,
                              rowLabels=depthValues,
                              colLabels=["CTD data", "Erddap data", "Difference"],
                              loc='bottom',
                              bbox=[0.0, -0.7, 1, .35],
                              cellColours=colors)
        new_table.set_fontsize(7)
    return new_table
'''

''' Extract the values from the data and make the table
'''


def buildTable(tableValues, colors, difference):
    # Get the depths into an array
    dv = np.array(tableValues)
    depthValues = dv[:, 0]
    # Remove the depths and leave the other values
    plotTbl = np.delete(tableValues, np.s_[0:1], axis=1)
    tblArr = list(plotTbl)
    ''' Formatting the table
        So you can put the table a bit lower (-0.3), and setting the height to 0.275 (<0.3) will create an 
        horizontal space between the plot and the table while making taller cells as the default value of 
        the height seems to be smaller than 0.15.  
    # bbox is: [left, bottom, width, height]'''
    my_bbox = [0.0, -0.9, 1, 0.275]
    fontSize = 7
    # Modify the values if the table is larger
    if len(depthValues) > 8:
        my_bbox = [0.0, -0.7, 1, 0.35]
        fontSize = 6

    tbl = plt.table(cellText=tblArr,
                    rowLabels=depthValues,
                    colLabels=["Station data", "CTD data", difference],
                    # cellLoc='center',
                    loc='bottom',
                    # bbox=my_bbox,
                    bbox=[0.0, -1.3, 1.0, 1.0],
                    cellColours=colors)

    # print(tbl.properties())
    # cell_dict = tbl.get_celld()
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_text_props(fontproperties=FontProperties(weight='bold', size=7))
        # print(f"Before Adjusting {cell.get_height()}")
        cell.set_height(cell.get_height() * 1.5)
        # print(f"  AfterAdjusting {cell.get_height()}")
    # tbl.set_title("Data Values")
    # [a.axis("off") for a in plt]
    tbl.auto_set_font_size(True)
    # tbl.set_fontsize(9)
    # tbl.scale(2, 2)
    # [t.auto_set_font_size(False) for t in [tbl]]
    # [t.set_fontsize(8) for t in [tbl]]
    # tbl.auto_set_column_width(col=list(range(3)))
    # Adjust layout to make room for the table:
    plt.subplots_adjust(left=0.2, bottom=0.2)

    # new_table.set_fontsize(fontSize)
    # return new_table


def colorTable(tableList, maxDiffLow, maxDiffHigh):
    # dv = np.array(tableValues)
    # for loop to assign colors to differences in numbers
    colors = []
    for i in range(len(tableList)):
        # Either one is none, then no calc
        # if tableList[i][1] is None or tableList[i][2] is None:
        #    colors.append(["white", "white", "white"])
        if tableList[i][3] is not None and (
                tableList[i][3] < maxDiffLow or tableList[i][3] > maxDiffHigh):  # 5% difference
            colors.append(["white", "white", "red"])
            plt.axhline(tableList[i][0], color='red', lw=0.25)  # y = 0
        else:
            # Either none or within the range
            colors.append(["white", "white", "white"])
            plt.axhline(tableList[i][0], color='black', lw=0.25)  # y = 0
    return colors


'''
def colorTableOld(tableList):
    # for loop to assign colors to differences in numbers
    colors = []
    for i in range(len(tableList)):
        if tableList[i][1] == None or tableList[i][0] == None:
            colors.append(["white", "white"])
        else:
            difference = percentDiff(tableList[i][0], tableList[i][1])
            if difference >= 5:  # 5% difference
                colors.append(["red", "red"])
            else:
                colors.append(["green", "green"])
    return colors



def percentDiff(one, two):
    return (abs(one - two) / ((one + two) / 2)) * 100
'''

'''
Dissolved Oxygen	∓0.5 mg/L
Conductance	∓5% of true value
Water Temperature	∓0.2 °C
'''


def DissolvedOxygenDiff(array, ctd):
    return array - ctd


def ConductanceDiff(array, ctd):
    return array - ctd


def WaterTemperatureDiff(array, ctd):
    return array - ctd


def SalinityDiff(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')
    # return array - ctd


def plotValidationNums(tableList):
    # plot validation numbers
    texts = []
    for i, value in enumerate(tableList):
        # Don't show if both are empty
        texts.append(
            plt.text(getDisplayString(value[1]), value[0], getDisplayString(value[3]),
                     rotation="horizontal", fontsize=9))
        # print(texts)
    return texts


def getDisplayString(val):
    if val == None:
        return ''
    return round(val, 2)


def dataDepthLists(hypDepth, hypData, ctdFilteredDepths, ctdFilteredData, diffFn):
    # depthHash={}
    ''' Table list is the table data
    [Depth, ErddapValue, Ctd Value, difference]
    '''
    lTableList = []
    # depthList = []
    # for loop to add data into 2d list and depths to separate list
    for i, depth in enumerate(hypDepth):
        ctdvalue = None
        # if i == len(hypDepth) - 1:
        #    ctdvalue = None
        # else:
        # gets the ctd values
        # ctdvalue = getCTDDepthandValue(depth, hypDepth[i + 1], ctdFilteredDepths, ctdFilteredData)
        ctdvalue = getCTDDepthandValue(depth, hypDepth[i], ctdFilteredDepths, ctdFilteredData)
        erddapDepthReading = hypData[i]
        if erddapDepthReading is not None:
            erddapDepthReading = round(erddapDepthReading, 2)
        lTableList.append([depth, erddapDepthReading, ctdvalue, getDiff(erddapDepthReading, ctdvalue, diffFn)])
        # depthList.append(depth)
        # depthHash[depth]=[hypData[i],ctdvalue]
    return lTableList  # , depthList


def getDiff(hypData, ctdvalue, diffFn):
    if hypData is None or ctdvalue is None:
        return None
    return round(diffFn(hypData, ctdvalue), 3)


def getCTDDepthandValue(hypDepth, nexthypDepth, ctdDepths, ctdValues):
    # closestVal = closest()
    # close = False
    for i, ctdDepth in enumerate(ctdDepths):
        if abs(ctdDepth - hypDepth) < 0.1:
            # Just passed the depth, is it close
            return round(ctdValues[i], 2)

    for i, ctdDepth in enumerate(ctdDepths):
        if abs(ctdDepth - hypDepth) < 0.25:
            # Just passed the depth, is it close
            return round(ctdValues[i], 2)

    for i, ctdDepth in enumerate(ctdDepths):
        if abs(ctdDepth - hypDepth) < 0.75:
            # Just passed the depth, is it close
            return round(ctdValues[i], 2)

    # if hypDepth >= ctdDepth >= nexthypDepth:


def by_depth(ele):
    return ele[0]


def getTile(name, ncboName, hypTime, ctdDate):
    # 2023-05-08T15:00:00+00
    # EST = tz.gettz("America/New_York")
    tz = pytz.timezone('America/New_York')

    # logging.info(f"HypTime {hypTime}")
    erdapDt = parse(hypTime)
    # logging.info(f"erdapDt {erdapDt}")
    # logging.info(f"erdapDt.astimezone(tz) {erdapDt.astimezone(tz)}")

    # erdapDt = datetime.strptime(hypTime, "%Y-%m-%dT%H:%M:%S%z")  # , tz=timezone.utc)
    ctdDate = datetime.fromtimestamp(ctdDate, tz=timezone.utc)
    # strftime('%y-%m-%d %H:%M:%S%z')
    return ncboName + "\n" + name + "\n" + " Station Time: (" + \
           erdapDt.astimezone(tz).strftime('%y-%m-%d %H:%M:%S %Z %z') + ")\n" + " CTD Date: (" + ctdDate.astimezone(
        tz).strftime('%y-%m-%d %H:%M:%S %Z %z') + ")"


def addYLines(hypDepth):
    for x in hypDepth:
        pass
        # plt.axhline(x, color='blue', lw=0.25)  # y = 0


def plotDualTemp(ctdData, hypTimePre, hypDepthPre, hypDataPre, hypTimePost, hypDepthPost, hypDataPost, ncboName,
                 subName):
    name = "Water_Temperature"
    # fig, ax = plt.subplots()
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle('Horizontally stacked subplots')
    plotSub(ax1, ctdData, hypTimePre, hypDepthPre, hypDataPre, ncboName, subName)
    plotSub(ax2, ctdData, hypTimePost, hypDepthPost, hypDataPost, ncboName, subName)
    logging.debug("Saving the plott")
    saveTheFig(ncboName, name, subName, hypTimePre[0])


def plotSub(axis, ctdData, hypTime, hypDepth, hypData, ncboName, subName):
    name = "Water_Temperature"
    # hypTime, hypDepth, hypData = getErdapArray(hypDataArray)
    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, hypDepth, 1)
    axis.plot(np.asarray(ctdFilteredData), np.asarray(ctdFilteredDepths), marker='x', ms=2, mfc='r', label='CTD Data')
    axis.plot(hypData, hypDepth, marker='o', ms=2, mfc='b', label='Buoy Data')
    # reverse y-axis so depth goes down
    # axis.title = getTile(name, ncboName, hypTime[0], ctdData[0][0])
    plt.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
    # axis.xlabel(name + " (°C)")
    # axis.ylabel("Depth (m)")
    # axis.xlim([0, 30])
    # axis.gca().invert_yaxis()
    axis.legend()

    tableList = dataDepthLists(hypDepth, hypData, ctdFilteredDepths, ctdFilteredData, WaterTemperatureDiff)

    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -0.2, 0.2)
    buildTable(tableList, colors, "Difference (±0.2)")
    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=0.4)
    addYLines(hypDepth)

    # plt.show()


def plotTemp(ctdData, hypTime, hypDepth, hypData, ncboName, subName):
    name = "Water_Temperature"
    fig, ax = plt.subplots()

    # hypTime, hypDepth, hypData = getErdapArray(hypDataArray)
    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, hypDepth, 1)
    plt.plot(np.asarray(ctdFilteredData), np.asarray(ctdFilteredDepths), marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(hypData, hypDepth, marker='o', ms=2, mfc='b', label='Buoy Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, ncboName, hypTime[0], ctdData[0][0]))
    plt.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
    plt.xlabel(name + " (°C)")
    plt.ylabel("Depth (m)")
    plt.xlim([0, 30])
    plt.gca().invert_yaxis()
    plt.legend()

    tableList = dataDepthLists(hypDepth, hypData, ctdFilteredDepths, ctdFilteredData, WaterTemperatureDiff)

    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -0.2, 0.2)
    buildTable(tableList, colors, "Difference (±0.2)")
    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=0.4)
    addYLines(hypDepth)
    saveTheFig(ncboName, name, subName, hypTime[0])
    # plt.show()


def plotConductivity(ctdData, hypTime, hypDepth, hypData, ncboName, subName):
    name = "Water Conductivity"
    fig, ax = plt.subplots()
    # hypTime, hypDepth, hypData = getErdapArray(hypDataArray)
    dataUnitMod = np.vectorize(HypoxiaUtil.vectorCondChange)
    hypData = dataUnitMod(hypData)
    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, hypDepth, 2)
    # ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, hypDepth, 2)
    plt.plot(ctdFilteredData, ctdFilteredDepths, marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(hypData, hypDepth, marker='o', ms=2, mfc='b', label='Station Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, ncboName, hypTime[0], ctdData[0][0]))
    plt.subplots_adjust(top=0.75)
    plt.xlabel(name + " (mS.cm-1)")
    plt.ylabel("Depth (m)")
    plt.xlim([0, 50])
    plt.gca().invert_yaxis()
    plt.legend()
    addYLines(hypDepth)
    tableList = dataDepthLists(hypDepth, hypData, ctdFilteredDepths, ctdFilteredData, ConductanceDiff)

    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -5.0, 5.0)
    buildTable(tableList, colors, "Difference (±5.0)")
    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=0.4)

    saveTheFig(ncboName, name, subName, hypTime[0])
    # plt.show()


def plotSalinity(ctdData, hypTime, hypDepth, hypData, ncboName, subName):
    name = "Water Salinity"
    fig, ax = plt.subplots()
    # hypTime, hypDepth, hypData = getErdapArray(hypData)

    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, hypDepth, 3)
    plt.plot(ctdFilteredData, ctdFilteredDepths, marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(hypData, hypDepth, marker='o', ms=2, mfc='r', label='Station Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, ncboName, hypTime[0], ctdData[0][0]))
    plt.subplots_adjust(top=0.75)
    plt.xlabel(name + " (PPT)")
    plt.ylabel("Depth (m)")
    plt.xlim([0, 30])
    plt.legend()
    plt.gca().invert_yaxis()
    addYLines(hypDepth)
    tableList = dataDepthLists(hypDepth, hypData, ctdFilteredDepths, ctdFilteredData, SalinityDiff)

    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -5.0, 5.0)
    buildTable(tableList, colors, "Difference (±5.0 %)")

    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=0.4)

    saveTheFig(ncboName, name, subName, hypTime[0])
    # plt.show()


def plotDO(ctdData, hypTime, hypDepth, hypData, ncboName, subName):
    name = "Dissolved Oxygen"
    fig, ax = plt.subplots()

    # hypTime, hypDepth, hypData = getErdapArray(hypData)

    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, hypDepth, 4)
    plt.plot(ctdFilteredData, ctdFilteredDepths, marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(hypData, hypDepth, marker='o', ms=2, mfc='r', label='Station Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, ncboName, hypTime[0], ctdData[0][0]))
    # plt.subplots_adjust(top=0.75)
    plt.xlabel(name + " (mg.L-1)")
    plt.ylabel("Depth (m)")
    plt.xlim([0, 10])
    plt.legend()
    plt.gca().invert_yaxis()
    rounded_depths = np.around(ctdFilteredDepths, decimals=1)
    addYLines(hypDepth)
    tableList = dataDepthLists(hypDepth, hypData, ctdFilteredDepths, ctdFilteredData, DissolvedOxygenDiff)
    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -0.5, 0.5)
    buildTable(tableList, colors, "Difference (± 0.5)")

    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=.4)
    saveTheFig(ncboName, name, subName, hypTime[0])

    # plt.show()


def getThePlotData(ctdData, hypDepth, ctdIndex):
    ctdFilteredData = []
    ctdFilteredDepths = []
    pastDepth = False
    # Iterate over the CTD Data. Only collect CTD data that is within the ERDDAP range
    for x, d in enumerate(ctdData):
        if ctdData[x, 5] < max(hypDepth + 0.5) and not pastDepth:
            ctdFilteredData.append(ctdData[x, ctdIndex])
            ctdFilteredDepths.append(ctdData[x, 5])
        else:
            pastDepth = True
    return ctdFilteredData, ctdFilteredDepths


def saveTheFig(ncboName, name, subName, dtStr):
    dt = parse(dtStr)
    # dt = datetime.strptime(dtStr, "%Y-%m-%dT%H:%M:%SZ")
    rootDir = HypoxiaUtil.getRootDir()
    plotDir = os.path.join(rootDir, 'data_output/plots')
    if not os.path.exists(plotDir):
        os.mkdir(plotDir)
    aname = f"{ncboName}_{dt.strftime('%Y_%m_%d')}_{name}_{subName}.png"
    fname = os.path.join(plotDir, aname)
    # fname = os.path.join(plotDir, ncboName + "_" + name + "_" + dt.strftime("%Y_%m_%d") + ".png")
    print(f'saving this plot: {fname}')
    # plt.savefig(fname, format="svg", bbox_inches='tight')
    plt.savefig(fname, format="png", dbi="500", bbox_inches='tight')

# def getErdapArray(hypDataArray):
#     hypTime = []
#     hypDepth = []
#     hypData = []
#
#     first = True
#     for row in hypDataArray:
#         if first:
#             first = False
#         else:
#             row = row.split(',')
#             if len(row) == 3:
#                 # print(row)
#                 hypTime.append(row[0])
#                 hypDepth.append(row[1])
#                 hypData.append(row[2])
#     hypTime = np.asarray(hypTime)
#     hypDepth = np.absolute(np.asarray(hypDepth, dtype=float))
#     hypData = np.asarray(hypData, dtype=float)
#     # print(hypTime)
#     return hypTime, hypDepth, hypData
