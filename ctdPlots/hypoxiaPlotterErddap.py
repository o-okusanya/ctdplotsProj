import os
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox

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
                    colLabels=["Erddap data", "CTD data", difference],
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


def SalinityDiff(array, ctd):
    return array - ctd


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


def dataDepthLists(erdapDepth, erdapData, ctdFilteredDepths, ctdFilteredData, diffFn):
    # depthHash={}
    ''' Table list is the table data
    [Depth, ErddapValue, Ctd Value, difference]
    '''
    lTableList = []
    # depthList = []
    # for loop to add data into 2d list and depths to separate list
    for i, depth in enumerate(erdapDepth):
        ctdvalue = None
        if i == len(erdapDepth) - 1:
            ctdvalue = None
        else:
            # gets the ctd values
            ctdvalue = getCTDDepthandValue(depth, erdapDepth[i + 1], ctdFilteredDepths, ctdFilteredData)
        erddapDepthReading = erdapData[i]
        if erddapDepthReading is not None:
            erddapDepthReading = round(erddapDepthReading, 2)
        lTableList.append([depth, erddapDepthReading, ctdvalue, getDiff(erddapDepthReading, ctdvalue, diffFn)])
        # depthList.append(depth)
        # depthHash[depth]=[erdapData[i],ctdvalue]
    return lTableList  # , depthList


def getDiff(erdapData, ctdvalue, diffFn):
    if erdapData is None or ctdvalue is None:
        return None
    return round(diffFn(erdapData, ctdvalue), 3)


def getCTDDepthandValue(erdapDepth, nextErdapDepth, ctdDepths, ctdValues):
    # closestVal = closest()
    # close = False
    for i, ctdDepth in enumerate(ctdDepths):
        if abs(ctdDepth - erdapDepth) < 0.1:
            # Just passed the depth, is it close
            return round(ctdValues[i], 2)

    for i, ctdDepth in enumerate(ctdDepths):
        if abs(ctdDepth - erdapDepth) < 0.25:
            # Just passed the depth, is it close
            return round(ctdValues[i], 2)

    for i, ctdDepth in enumerate(ctdDepths):
        if abs(ctdDepth - erdapDepth) < 0.75:
            # Just passed the depth, is it close
            return round(ctdValues[i], 2)

    # if erdapDepth >= ctdDepth >= nextErdapDepth:


def by_depth(ele):
    return ele[0]


def getTile(name, erddapName, erdapTime, ctdDate):
    erdapDt = datetime.strptime(erdapTime, "%Y-%m-%dT%H:%M:%SZ")  # , tz=timezone.utc)
    ctdDate = datetime.fromtimestamp(ctdDate, tz=timezone.utc).strftime('%y-%m-%d %H:%M:%S%z')
    return erddapName + "\n" + name + "\n" + " ERDDAP Time: (" + \
           erdapDt.strftime('%y-%m-%d %H:%M:%S%z') + ")\n" + " CTD Date: (" + ctdDate + ")"


def addYLines(erdapDepth):
    for x in erdapDepth:
        pass
        # plt.axhline(x, color='blue', lw=0.25)  # y = 0


def plotTemp(ctdData, erdapDataArray, erddapName):
    name = "Water Temperature"
    fig, ax = plt.subplots()

    erdapTime, erdapDepth, erdapData = getErdapArray(erdapDataArray)
    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, erdapDepth, 1)
    plt.plot(np.asarray(ctdFilteredData), np.asarray(ctdFilteredDepths), marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(erdapData, erdapDepth, marker='o', ms=2, mfc='b', label='ERDDAP Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, erddapName, erdapTime[0], ctdData[0][0]))
    plt.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
    plt.xlabel(name + " (°C)")
    plt.ylabel("Depth (m)")
    plt.gca().invert_yaxis()
    plt.legend()

    tableList = dataDepthLists(erdapDepth, erdapData, ctdFilteredDepths, ctdFilteredData, WaterTemperatureDiff)

    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -0.2, 0.2)
    buildTable(tableList, colors, "Difference (±0.2)")
    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=0.4)
    addYLines(erdapDepth)
    saveTheFig(erddapName, name, erdapTime[0])
    # plt.show()


def plotConductivity(ctdData, erdapDataArray, erddapName):
    name = "Water Conductivity"
    fig, ax = plt.subplots()
    erdapTime, erdapDepth, erdapData = getErdapArray(erdapDataArray)

    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, erdapDepth, 2)
    plt.plot(ctdFilteredData, ctdFilteredDepths, marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(erdapData, erdapDepth, marker='o', ms=2, mfc='b', label='Array Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, erddapName, erdapTime[0], ctdData[0][0]))
    plt.subplots_adjust(top=0.75)
    plt.xlabel(name + " (mS.cm-1)")
    plt.ylabel("Depth (m)")
    plt.gca().invert_yaxis()
    plt.legend()
    addYLines(erdapDepth)
    tableList = dataDepthLists(erdapDepth, erdapData, ctdFilteredDepths, ctdFilteredData, ConductanceDiff)

    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -5.0, 5.0)
    buildTable(tableList, colors, "Difference (±5.0)")
    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=0.4)

    saveTheFig(erddapName, name, erdapTime[0])
    # plt.show()


def plotSalinity(ctdData, erdapData, erddapName):
    name = "Water Salinity"
    fig, ax = plt.subplots()
    erdapTime, erdapDepth, erdapData = getErdapArray(erdapData)

    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, erdapDepth, 3)
    plt.plot(ctdFilteredData, ctdFilteredDepths, marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(erdapData, erdapDepth, marker='o', ms=2, mfc='r', label='Array Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, erddapName, erdapTime[0], ctdData[0][0]))
    plt.subplots_adjust(top=0.75)
    plt.xlabel(name + " (PPT)")
    plt.ylabel("Depth (m)")
    plt.legend()
    plt.gca().invert_yaxis()
    addYLines(erdapDepth)
    tableList = dataDepthLists(erdapDepth, erdapData, ctdFilteredDepths, ctdFilteredData, SalinityDiff)

    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -5.0, 5.0)
    buildTable(tableList, colors, "Difference (±5.0)")

    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=0.4)

    saveTheFig(erddapName, name, erdapTime[0])
    # plt.show()


def plotDO(ctdData, erdapData, erddapName):
    name = "Dissolved Oxygen"
    fig, ax = plt.subplots()

    erdapTime, erdapDepth, erdapData = getErdapArray(erdapData)

    ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, erdapDepth, 4)
    plt.plot(ctdFilteredData, ctdFilteredDepths, marker='x', ms=2, mfc='r', label='CTD Data')
    plt.plot(erdapData, erdapDepth, marker='o', ms=2, mfc='r', label='Array Data')
    # reverse y-axis so depth goes down
    plt.title(getTile(name, erddapName, erdapTime[0], ctdData[0][0]))
    # plt.subplots_adjust(top=0.75)
    plt.xlabel(name + " (mg.L-1)")
    plt.ylabel("Depth (m)")
    plt.legend()
    plt.gca().invert_yaxis()
    rounded_depths = np.around(ctdFilteredDepths, decimals=1)
    addYLines(erdapDepth)
    tableList = dataDepthLists(erdapDepth, erdapData, ctdFilteredDepths, ctdFilteredData, DissolvedOxygenDiff)
    # Now inverse the table data for the chart
    tableList = sorted(tableList, key=by_depth)
    colors = colorTable(tableList, -0.5, 0.5)
    buildTable(tableList, colors, "Difference (± 0.5)")

    # This adds numbers to the plot
    # texts = plotValidationNums(tableList)
    # adjust_text(texts, only_move={'points': 'y', 'texts': 'y'})
    plt.subplots_adjust(bottom=.4)
    saveTheFig(erddapName, name, erdapTime[0])
    # plt.show()


def getThePlotData(ctdData, erdapDepth, ctdIndex):
    ctdFilteredData = []
    ctdFilteredDepths = []
    pastDepth = False
    # Iterate over the CTD Data. Only collect CTD data that is within the ERDDAP range
    for x, d in enumerate(ctdData):
        if ctdData[x, 5] < max(erdapDepth + 0.5) and not pastDepth:
            ctdFilteredData.append(ctdData[x, ctdIndex])
            ctdFilteredDepths.append(ctdData[x, 5])
        else:
            pastDepth = True
    return ctdFilteredData, ctdFilteredDepths


def saveTheFig(erddapName, name, dtStr):
    dt = datetime.strptime(dtStr, "%Y-%m-%dT%H:%M:%SZ")
    plotDir = 'plots'
    if not os.path.exists(plotDir):
        os.mkdir(plotDir)
    fname = os.path.join(plotDir, erddapName + "_" + name + "_" + dt.strftime("%Y_%m_%d") + ".png")
    print(f'saving this plot: {fname}')
    # plt.savefig(fname, format="svg", bbox_inches='tight')
    plt.savefig(fname, format="png", dbi="500", bbox_inches='tight')


def getErdapArray(erdapDataArray):
    erdapTime = []
    erdapDepth = []
    erdapData = []

    first = True
    for row in erdapDataArray:
        if first:
            first = False
        else:
            row = row.split(',')
            if len(row) == 3:
                # print(row)
                erdapTime.append(row[0])
                erdapDepth.append(row[1])
                erdapData.append(row[2])
    erdapTime = np.asarray(erdapTime)
    erdapDepth = np.absolute(np.asarray(erdapDepth, dtype=float))
    erdapData = np.asarray(erdapData, dtype=float)
    # print(erdapTime)
    return erdapTime, erdapDepth, erdapData
