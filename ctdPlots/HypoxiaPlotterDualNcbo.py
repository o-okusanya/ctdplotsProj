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

'''
class HypoxiaPlotterDualNcbo:

    def __init__(self):
        self.PRE_LABEL = "Before CTD Cast"
        self.POST_LABEL = "After CTD Cast"
        self.DEPTH_INDEX = 6

    def _buildDualTable(axis, tableValues, colors, difference):
        # Get the depths into an array
        dv = np.array(tableValues)
        depthValues = dv[:, 0]
        # Remove the depths and leave the other values
        plotTbl = np.delete(tableValues, np.s_[0:1], axis=1)
        tblArr = list(plotTbl)
        # Formatting the table
        #    So you can put the table a bit lower (-0.3), and setting the height to 0.275 (<0.3) will create an 
        #    horizontal space between the plot and the table while making taller cells as the default value of 
        #    the height seems to be smaller than 0.15.  
        # bbox is: [left, bottom, width, height]
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

    def _DissolvedOxygenDiff(self, array, ctd):
        return array - ctd

    def _ConductanceDiff(self, array, ctd):
        return array - ctd

    def _WaterTemperatureDiff(self, array, ctd):
        return array - ctd

    def _percentDifference(self, current, previous):
        if current == previous:
            return 0
        try:
            return (abs(current - previous) / previous) * 100.0
        except ZeroDivisionError:
            return float('inf')

    # Not used?
    # def getDisplayString(val):
    #     if val is None:
    #         return ''
    #     return round(val, 2)

    def _getDataDepthLists(self, hypDepth, hypData, pressData, ctdFilteredDepths, ctdFilteredData, diffFn):
        # depthHash={}
        # Table list is the table data
        #[Depth, ErddapValue, Ctd Value, difference]
        #
        lTableList = []
        # for loop to add data into 2d list and depths to separate list
        for i, depth in enumerate(hypDepth):
            ctdvalue = getCTDDepthandValue(depth, ctdFilteredDepths, ctdFilteredData)
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

    def getTile(self, name, ncboName, hypTime, ctdDate, rptName, fileTime):
        # 2023-05-08T15:00:00+00
        # EST = tz.gettz("America/New_York")
        tz = pytz.timezone('America/New_York')
        erdapDt = parse(hypTime)
        ctdDate = datetime.fromtimestamp(ctdDate, tz=timezone.utc)
        if fileTime == "Pre":
            timeInf = "Pre Maintenance"
        else:
            timeInf = "Post Maintenance"
        return ncboName + " " + timeInf + "\n" + name + " " + rptName + "\n" + " Station Time: \n(" + \
               erdapDt.astimezone(tz).strftime(
                   '%y-%m-%d %H:%M:%S %Z %z') + ")\n" + " CTD Date:\n(" + ctdDate.astimezone(
            tz).strftime('%y-%m-%d %H:%M:%S %Z %z') + ")"

    def plotDualTemp(self, ctdData, dataTempreaturePre, dataTempreaturePost, ncboName, subName, fileTime):
        name = "Water Temperature"
        ax1, ax2 = self._getFigures()
        # fig.suptitle('Horizontally stacked subplots')
        self._plotDualTempSub(ax1, name, ctdData, dataTempreaturePre, ncboName, self.PRE_LABEL, fileTime)
        self._plotDualTempSub(ax2, name, ctdData, dataTempreaturePost, ncboName, self.POST_LABEL, fileTime)

        plt.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
        plt.subplots_adjust(bottom=0.4)

        logging.debug("Saving the plot")
        self._saveTheFig(fig, ncboName, name, subName, fileTime, dataTempreaturePre.timeArray[0])

    def _plotDualTempSub(self, axis, name, ctdData, apiDataVo, ncboName, rptName, fileTime):
        ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, apiDataVo.depthArray, 1)  # DIFFERENT
        units = " (°C)"
        limits = [0, 30]
        makePlot(axis, ctdFilteredData, ctdFilteredDepths, name, ctdData[0][0], apiDataVo, ncboName, units, limits,
                 rptName,
                 fileTime)

        tableList = dataDepthLists(apiDataVo.depthArray, apiDataVo.dataArray, apiDataVo.pressArray, ctdFilteredDepths,
                                   ctdFilteredData,
                                   WaterTemperatureDiff)  # DIFFERENT
        colors = colorTable(axis, tableList, -0.2, 0.2)
        buildDualTable(axis, tableList, colors, "Difference (±0.2 °C)")
        plt.subplots_adjust(left=0.2, bottom=0.2)

    def plotDualSalinity(ctdData, dataSalPre, dataSalPost, ncboName, subName, fileTime):
        name = "Water Salinity"
        ax1, ax2 = getFigures()
        # fig.suptitle('Horizontally stacked subplots')
        plotDualSalSub(ax1, name, ctdData, dataSalPre, ncboName, pre, fileTime)
        plotDualSalSub(ax2, name, ctdData, dataSalPost, ncboName, aft, fileTime)

        plt.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
        plt.subplots_adjust(bottom=0.4)

        logging.debug("Saving the plot")
        saveTheFig(ncboName, name, subName, fileTime, dataSalPre.timeArray[0])

    def plotDualSalSub(self, axis, name, ctdData, apiDataVo, ncboName, rptName, fileTime):
        ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, apiDataVo.depthArray, 3)  # DIFFERENT
        units = "(PPT)"
        limits = [0, 30]
        makePlot(axis, ctdFilteredData, ctdFilteredDepths, name, ctdData[0][0], apiDataVo, ncboName, units, limits,
                 rptName,
                 fileTime)

        tableList = dataDepthLists(apiDataVo.depthArray, apiDataVo.dataArray, apiDataVo.pressArray, ctdFilteredDepths,
                                   ctdFilteredData, percentDifference)  # DIFFERENT
        colors = colorTable(axis, tableList, -5.0, 5.0)
        buildDualTable(axis, tableList, colors, "Difference (±5.0 %)")
        plt.subplots_adjust(left=0.2, bottom=0.2)

    def plotDualDO(self, ctdData, dataDoPre, dataDoPost, ncboName, subName, fileTime):
        name = "Dissolved Oxygen"
        ax1, ax2 = getFigures()
        self._plotDualDOSub(ax1, name, ctdData, dataDoPre, ncboName, pre, fileTime)
        self._plotDualDOSub(ax2, name, ctdData, dataDoPost, ncboName, aft, fileTime)

        plt.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
        plt.subplots_adjust(bottom=0.4)

        logging.debug("Saving the plot Dissolved Oxygen")
        saveTheFig(ncboName, name, subName, fileTime, dataDoPre.timeArray[0])

    def _plotDualDOSub(self, axis, name, ctdData, apiDataVo, ncboName, rptName, fileTime):
        ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, apiDataVo.depthArray, 4)  # DIFFERENT
        units = " (mg.L-1)"
        limits = [0, 10]
        makePlot(axis, ctdFilteredData, ctdFilteredDepths, name, ctdData[0][0], apiDataVo, ncboName, units, limits,
                 rptName,
                 fileTime)

        tableList = dataDepthLists(apiDataVo.depthArray, apiDataVo.dataArray, apiDataVo.pressArray, ctdFilteredDepths,
                                   ctdFilteredData, DissolvedOxygenDiff)  # DIFFERENT
        colors = colorTable(axis, tableList, -0.5, 0.5)
        buildDualTable(axis, tableList, colors, "Difference (±0.5 mg/l)")
        plt.subplots_adjust(left=0.2, bottom=0.2)

    def _plotDualCond(self, ctdData, dataCondPre, dataCondPost, ncboName, subName, fileTime):
        name = "Water Conductivity"
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)
        plotDualCondSub(ax1, name, ctdData, dataCondPre, ncboName, pre, fileTime)
        plotDualCondSub(ax2, name, ctdData, dataCondPost, ncboName, aft, fileTime)

        fig.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
        fig.subplots_adjust(bottom=0.4)

        logging.debug("Saving the plot")
        saveTheFig(ncboName, name, subName, fileTime, dataCondPre.timeArray[0])

    def plotDualCondSub(self, axis, name, ctdData, apiDataVo, ncboName, rptName, fileTime):
        ctdFilteredData, ctdFilteredDepths = getThePlotData(ctdData, apiDataVo.depthArray, 2)  # DIFFERENT
        units = " (mS.cm-1)"
        limits = [0, 50]
        makePlot(axis, ctdFilteredData, ctdFilteredDepths, name, ctdData[0][0], apiDataVo, ncboName, units, limits,
                 rptName,
                 fileTime)

        tableList = dataDepthLists(apiDataVo.depthArray, apiDataVo.dataArray, apiDataVo.pressArray, ctdFilteredDepths,
                                   ctdFilteredData, percentDifference)  # DIFFERENT
        colors = colorTable(axis, tableList, -5.0, 5.0)
        buildDualTable(axis, tableList, colors, "Difference (±5.0 %)")
        axis.subplots_adjust(left=0.2, bottom=0.2)

    def _makePlot(self, axis, ctdFilteredData, ctdFilteredDepths, name, cdtTime, apiDataVo, ncboName, units, xlimits,
                  rptName,
                  fileTime):
        # Plot the CTD data
        axis.plot(np.asarray(ctdFilteredData), np.asarray(ctdFilteredDepths), color='lightsteelblue', marker='x', ms=2,
                  mfc='r', label='CTD Data')

        # Plot the API data
        axis.scatter(apiDataVo.dataArray, apiDataVo.depthArray, s=280, color='darkviolet', marker='_', zorder=3)
        axis.scatter(apiDataVo.dataArray, apiDataVo.depthArray, s=80, color='navy', marker='.', zorder=3)
        axis.scatter(apiDataVo.dataArray, apiDataVo.pressArray, s=80, color='crimson', marker='|', zorder=3)
        # plt.scatter(x, y, c=colors, edgecolors=colors)
        # for pos, ypt in zip(apiDataVo.dataArray, apiDataVo.depthArray):
        # axis.errorbar(apiDataVo.dataArray, apiDataVo.depthArray, yerr=0.5, ls='none', color='palegreen', capsize=2,
        #              capthick=2)

        # axis.plot(apiDataVo.dataArray, apiDataVo.depthArray, linewidth=1, color='black', marker='.', label='Buoy Data')
        axis.set_title(getTile(name, ncboName, apiDataVo.timeArray[0], cdtTime, rptName, fileTime))
        axis.set_xlabel(name + " " + units)  # DIFFERENT
        axis.set_ylabel("Depth (m)")
        axis.set_xlim(xlimits)  # DIFFERENT
        # reverse y-axis so depth goes down
        axis.invert_yaxis()
        axis.legend()

    def _getThePlotData(self, ctdData, hypDepth, ctdIndex):
        ctdFilteredData = []
        ctdFilteredDepths = []
        pastDepth = False
        # Iterate over the CTD Data. Only collect CTD data that is within the ERDDAP range
        for x, d in enumerate(ctdData):
            if ctdData[x, 5] < max(hypDepth + 0.5) and not pastDepth:
                ctdFilteredData.append(ctdData[x, ctdIndex])
                ctdFilteredDepths.append(ctdData[x, self.DEPTH_INDEX])
            else:
                pastDepth = True
        return ctdFilteredData, ctdFilteredDepths

    def _getFigures(self):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)
        return ax1, ax2

    def _saveTheFig(self, newPlot, ncboName, name, subName, fileTime, dtStr):
        dt = parse(dtStr)
        # dt = datetime.strptime(dtStr, "%Y-%m-%dT%H:%M:%SZ")
        rootDir = HypoxiaUtil.getRootDir()
        plotDir = os.path.join(rootDir, 'plots')
        if not os.path.exists(plotDir):
            os.mkdir(plotDir)
        aname = f"{ncboName}_{dt.strftime('%Y_%m_%d')}_{name}_{fileTime}_{subName}.svg"
        fname = os.path.join(plotDir, aname)
        # fname = os.path.join(plotDir, ncboName + "_" + name + "_" + dt.strftime("%Y_%m_%d") + ".png")
        print(f'saving this plot: {fname}')
        # plt.savefig(fname, format="svg", bbox_inches='tight')
        newPlot.savefig(fname, format="svg", bbox_inches='tight')
        newPlot.close()
'''