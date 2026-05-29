import logging

from ctdPlots.plotter.PlotBaseMgr import PlotBaseMgr
from ctdPlots.plotter.QCEvaluator import QCEvaluator


class PlotDissolvedO2Mgr(PlotBaseMgr):

    def __init__(self, firstDate):
        PlotBaseMgr.__init__(self, firstDate)
        self.suspect = 0.3
        self.units = " (mg.L-1)"
        self.limits = [0, 15]
        self.tableDesc = "Difference (±0.5°C fail / ±0.3°C suspect) mg.L-1"
        self.DATA_INDEX = 4
        self.name = "Dissolved Oxygen"
        self.min = -0.5
        self.max = 0.5
        self.qc = QCEvaluator(failLow=self.min, failHigh=self.max, suspectLow=-self.suspect, suspectHigh=self.suspect)

    def plotDissolvedO2(self, ctdData, dataTemperaturePre, dataTemperaturePost, ncboName, subName, fileTime):
        self._plotDissolvedO2Sub(self.ax1, self.name, ctdData, dataTemperaturePre, ncboName, self.PRE_LABEL,
                                 fileTime)
        self._plotDissolvedO2Sub(self.ax2, self.name, ctdData, dataTemperaturePost, ncboName, self.POST_LABEL,
                                 fileTime)

        self.fig.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
        self.fig.subplots_adjust(bottom=0.4)

        logging.debug("Saving the plot")
        plotDate = None
        if dataTemperaturePre is None or dataTemperaturePre.timeArray is None:
            plotDate = dataTemperaturePost.timeArray[0]
        else:
            plotDate = dataTemperaturePre.timeArray[0]

        self._saveTheFig(ncboName, self.name, subName, fileTime, plotDate)
        # self._saveTheFig(ncboName, self.name, subName, fileTime, dataTemperaturePre.timeArray[0])

    def _plotDissolvedO2Sub(self, axis, name, ctdData, apiDataVo, ncboName, rptName, fileTime):
        # Get the temperature data from the CTD File
        if apiDataVo is None:
            # Only plot the CTD data
            ctdFilteredData, ctdFilteredDepths = self._getThePlotData(ctdData, None, self.DATA_INDEX)
        else:
            # Just plot the CTD data, no API data or table can be generated
            ctdFilteredData, ctdFilteredDepths = self._getThePlotData(ctdData, apiDataVo.getUniqueDepths(),
                                                                      self.DATA_INDEX)

            tableList = self._getDataDepthLists(apiDataVo.depthArray, apiDataVo.dataArray, apiDataVo.pressArray,
                                                ctdFilteredDepths, ctdFilteredData, self._valueDifference)  # DIFFERENT
            flags = self.qc.evaluateList(tableList)
            colors = self._colorTable(axis, tableList, flags)
            self._buildDualTable(axis, tableList, colors, self.tableDesc)
        self._makePlot(axis, ctdFilteredData, ctdFilteredDepths, name, ctdData[0][0], apiDataVo, ncboName,
                       self.units,
                       self.limits, rptName, fileTime)
        self.fig.subplots_adjust(left=0.2, bottom=0.2)
