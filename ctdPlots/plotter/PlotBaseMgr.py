import logging
import os
import time
from datetime import datetime, timezone

import pytz
from dateutil.parser import parse

import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from dateutil.tz import tzfile
from matplotlib import pyplot
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox

from ctdPlots.HypoxiaUtil import HypoxiaUtil


class PlotBaseMgr:

    def __init__(self, firstDate):
        self.PRE_LABEL = "Before CTD Cast"
        self.POST_LABEL = "After CTD Cast"

        self.DEPTH_INDEX = 6  # TODO (Do i need this) self._getDepthIndex(firstDate)
        # Create the figure when initing
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2)
        self.fig.set_size_inches(18, 7)

        # Used for color coding the table

    def _percentDifference(self, current, previous):
        if current == previous:
            return 0
        try:
            return (abs(current - previous) / previous) * 100.0
        except ZeroDivisionError:
            return float('inf')

    def _valueDifference(self, array, ctd):
        return array - ctd

    ''' There is a file change made after this date that moves the depth index '''
    def _getDepthIndex(self, firstDate):
        # Anything before this date has a different depth index
        depthSwapDate = datetime(2023, 5, 23, 0, 0, 0)
        if firstDate < depthSwapDate.timestamp():
            return 5
        return 6

    def _buildDualTable(self, axis, tableValues, colors, difference):
        # Get the depths into an array
        dv = np.array(tableValues)
        depthValues = dv[:, 0]
        # Remove the depths and leave the other values
        plotTbl = np.delete(tableValues, np.s_[0:1], axis=1)
        tblArr = list(plotTbl)
        # TODO testing
        ''' Formatting the table
            So you can put the table a bit lower (-0.3), and setting the height to 0.275 (<0.3) will create an 
            horizontal space between the plot and the table while making taller cells as the default value of 
            the height seems to be smaller than 0.15.  
        # bbox is: [left, bottom, width, height]'''
        tbl = axis.table(cellText=tblArr,
                         rowLabels=depthValues,
                         colLabels=["Station data", "Pressure", "CTD data", difference],
                         loc='bottom',
                         bbox=[0.0, -1.3, 1.0, 1.0],
                         cellColours=colors)
        for (row, col), cell in tbl.get_celld().items():
            if row == 0:
                cell.set_text_props(fontproperties=FontProperties(weight='bold', size=7))
            cell.set_height(cell.get_height() * 1.5)
        tbl.auto_set_font_size(True)

    def _colorTable(self, axis, tableList, maxDiffLow, maxDiffHigh):
        # for loop to assign colors to differences in numbers
        colors = []
        for i in range(len(tableList)):
            # Either one is none, then no calc
            # if tableList[i][1] is None or tableList[i][2] is None:
            #    colors.append(["white", "white", "white"])
            # Added pressure, the diff is now col 4
            if tableList[i][4] is not None and (tableList[i][4] < maxDiffLow or tableList[i][4] > maxDiffHigh):
                # 5% difference
                colors.append(["white", "white", "white", "red"])
                axis.axhline(tableList[i][0], color='red', lw=0.25)  # y = 0
            else:
                # Either none or within the range
                colors.append(["white", "white", "white", "white"])
                axis.axhline(tableList[i][0], color='black', lw=0.25)  # y = 0
        return colors

    def _getDataDepthLists(self, hypDepth, hypData, pressData, ctdFilteredDepths, ctdFilteredData, diffFn):
        # depthHash={}
        ''' Table list is the table data
        [Depth, ErddapValue, Ctd Value, difference]
        '''
        lTableList = []
        # for loop to add data into 2d list and depths to separate list
        for i, depth in enumerate(hypDepth):
            ctdvalue = self._getCTDDepthandValue(depth, ctdFilteredDepths, ctdFilteredData)
            buoyDepthReading = hypData[i]

            if buoyDepthReading is not None:
                buoyDepthReading = round(buoyDepthReading, 2)
            buoyPressure = pressData[i]
            if buoyPressure is not None:
                buoyPressure = round(buoyPressure, 2)

            lTableList.append(
                [depth, buoyDepthReading, buoyPressure, ctdvalue, self._getDiff(buoyDepthReading, ctdvalue, diffFn)])
        # Now inverse the table data for the chart
        tableList = sorted(lTableList, key=self._by_depth)
        return tableList  # , depthList

    def _getDiff(self, hypData, ctdvalue, diffFn):
        if hypData is None or ctdvalue is None:
            return None
        return round(diffFn(hypData, ctdvalue), 3)

    def _getCTDDepthandValue(self, hypDepth, ctdDepths, ctdValues):
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

    # Key to sort by depth
    def _by_depth(self, ele):
        return ele[0]

    def _getTile(self, name, ncboName, hypTime, ctdDate, rptName, fileTime):
        # 2023-05-08T15:00:00+00
        # EST = tz.gettz("America/New_York")
        tz = pytz.timezone('America/New_York')
        # Get the datestring for the API data
        if hypTime == "N/A":
            erdapStr = hypTime
        else:
            erdapDt = parse(hypTime)
            erdapStr = erdapDt.astimezone(tz).strftime('%y-%m-%d %H:%M:%S %Z %z')
        ctdDate = datetime.fromtimestamp(ctdDate, tz=timezone.utc)
        if fileTime == "Pre":
            timeInf = "Pre Maintenance"
        else:
            timeInf = "Post Maintenance"
        return ncboName + " " + timeInf + "\n" + name + " " + rptName + "\n" + " Station Time: \n(" + \
            erdapStr + ")\n" + " CTD Date:\n(" + ctdDate.astimezone(
                tz).strftime('%y-%m-%d %H:%M:%S %Z %z') + ")"

    def _makePlot(self, axis, ctdFilteredData, ctdFilteredDepths, name, cdtTime, apiDataVo, ncboName, units, xlimits,
                  rptName, fileTime):
        # Plot the CTD data
        axis.plot(np.asarray(ctdFilteredData), np.asarray(ctdFilteredDepths), color='lightsteelblue', marker='x', ms=2,
                  mfc='r', label='CTD Data')

        # Plot the API data if it exists
        if apiDataVo is not None:
            axis.scatter(apiDataVo.dataArray, apiDataVo.getUniqueDepths(), s=280, color='darkviolet', marker='_',
                         zorder=3)
            axis.scatter(apiDataVo.dataArray, apiDataVo.getUniqueDepths(), s=80, color='navy', marker='.', zorder=3)
            axis.scatter(apiDataVo.dataArray, apiDataVo.getUniqueDepths(), s=80, color='crimson', marker='|', zorder=3)
            # plt.scatter(x, y, c=colors, edgecolors=colors)
            # for pos, ypt in zip(apiDataVo.dataArray, apiDataVo.depthArray):
            # axis.errorbar(apiDataVo.dataArray, apiDataVo.depthArray, yerr=0.5, ls='none', color='palegreen', capsize=2,
            #              capthick=2)

            # axis.plot(apiDataVo.dataArray, apiDataVo.depthArray, linewidth=1, color='black', marker='.', label='Buoy Data')
            # firstTime =  time.strftime('%Y-%m-%dT%H:%M:%SZ',  apiDataVo.timeArray[0])
            firstTime = apiDataVo.timeArray[0].isoformat()
            axis.set_title(self._getTile(name, ncboName, firstTime, cdtTime, rptName, fileTime))
        else:
            axis.set_title(self._getTile(name, ncboName, "N/A", cdtTime, rptName, fileTime))
        axis.set_xlabel(name + " " + units)  # DIFFERENT
        axis.set_ylabel("Depth (m)")
        axis.set_xlim(xlimits)  # DIFFERENT
        # reverse y-axis so depth goes down
        axis.invert_yaxis()
        axis.legend()

    def _getThePlotData(self, ctdData, hypDepthArray, ctdIndex):
        ctdFilteredData = []
        ctdFilteredDepths = []
        pastDepth = False
        # Iterate over the CTD Data. Only collect CTD data that is within the ERDDAP range
        for x, d in enumerate(ctdData):
            if hypDepthArray is None:
                # This is not cutoff, plot all of the data
                ctdFilteredData.append(ctdData[x, ctdIndex])
                ctdFilteredDepths.append(ctdData[x, self.DEPTH_INDEX])
            else:
                # Use the max depth from the array
                if ctdData[x, 5] < np.max(hypDepthArray) + 0.5 and not pastDepth:
                    ctdFilteredData.append(ctdData[x, ctdIndex])
                    ctdFilteredDepths.append(ctdData[x, self.DEPTH_INDEX])
                else:
                    pastDepth = True
        return ctdFilteredData, ctdFilteredDepths

    def _saveTheFig(self, ncboName, name, subName, fileTime, dtStr):
        # dt = parse(dtStr)
        # dt = datetime.strftime(dtStr, "%Y-%m-%dT%H:%M:%SZ")
        dt = dtStr.strftime('%Y_%m_%d')
        rootDir = HypoxiaUtil.getRootDir()
        plotDir = os.path.join(rootDir, 'data_output/plots')
        if not os.path.exists(plotDir):
            os.mkdir(plotDir)
        aname = f"{ncboName}_{dt}_{name}_{fileTime}_{subName}.svg"
        fname = os.path.join(plotDir, aname)
        # fname = os.path.join(plotDir, ncboName + "_" + name + "_" + dt.strftime("%Y_%m_%d") + ".png")
        print(f'saving this plot: {fname}')
        # plt.savefig(fname, format="svg", bbox_inches='tight')
        self.fig.savefig(fname, format="svg", bbox_inches='tight')
        pyplot.close()
