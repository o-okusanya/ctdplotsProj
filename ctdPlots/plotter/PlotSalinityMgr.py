import logging

from ctdPlots.plotter.PlotBaseMgr import PlotBaseMgr


class PlotSalinityMgr(PlotBaseMgr):

    def __init__(self, firstDate):
        PlotBaseMgr.__init__(self, firstDate)
        self.units = " (PPT)"
        self.limits = [0, 30]
        self.tableDesc = "Difference (±5.0 %)"
        self.DATA_INDEX = 3
        self.name = "Water Salinity"
        self.min = -5.0
        self.max = 5.0

    def plotDualSalinity(self, ctdData, dataTemperaturePre, dataTemperaturePost, ncboName, subName, fileTime):
        self._plotDualSalSub(self.ax1, self.name, ctdData, dataTemperaturePre, ncboName, self.PRE_LABEL, fileTime)
        self._plotDualSalSub(self.ax2, self.name, ctdData, dataTemperaturePost, ncboName, self.POST_LABEL, fileTime)

        self.fig.subplots_adjust(top=0.75)  # Adjust the plot to give room for the big title
        self.fig.subplots_adjust(bottom=0.4)

        logging.debug("Saving the plot")
        if dataTemperaturePre is None or dataTemperaturePre.timeArray is None:
            plotDate = dataTemperaturePost.timeArray[0]
        else:
            plotDate = dataTemperaturePre.timeArray[0]

        self._saveTheFig(ncboName, self.name, subName, fileTime, plotDate)
        # self._saveTheFig(ncboName, self.name, subName, fileTime, dataTemperaturePre.timeArray[0])

    def _plotDualSalSub(self, axis, name, ctdData, apiDataVo, ncboName, rptName, fileTime):
        # Get the temperature data from the CTD File
        if apiDataVo is None:
            # Only plot the CTD data
            ctdFilteredData, ctdFilteredDepths = self._getThePlotData(ctdData, None, self.DATA_INDEX)
        else:
            # Just plot the CTD data, no API data or table can be generated
            ctdFilteredData, ctdFilteredDepths = self._getThePlotData(ctdData, apiDataVo.getUniqueDepths(),
                                                                      self.DATA_INDEX)

            tableList = self._getDataDepthLists(apiDataVo.depthArray, apiDataVo.dataArray, apiDataVo.pressArray,
                                                ctdFilteredDepths, ctdFilteredData, self._percentDifference)  # DIFFE
            colors = self._colorTable(axis, tableList, self.min, self.max)
            self._buildDualTable(axis, tableList, colors, self.tableDesc)
        self._makePlot(axis, ctdFilteredData, ctdFilteredDepths, name, ctdData[0][0], apiDataVo, ncboName, self.units,
                       self.limits, rptName, fileTime)

        self.fig.subplots_adjust(left=0.2, bottom=0.2)
