import logging
import os
from datetime import datetime

import matplotlib
import pytz

from ctdPlots.HypoxiaUtil import HypoxiaUtil
from ctdPlots.ctdFileMgr import CTDReader
from ctdPlots.plotter.PlotConductivityMgr import PlotConductivityMgr
from ctdPlots.plotter.PlotDissolvedO2Mgr import PlotDissolvedO2Mgr
from ctdPlots.plotter.PlotSalinityMgr import PlotSalinityMgr
from ctdPlots.plotter.PlotTemperatureMgr import PlotTemperatureMgr
from hypbase.src.api.HypoxiaApi import HypoxiaApi
from hypbase.src.api.vo.HypoxiaStationVo import TRAVERSE_ORDER
from hypbase.src.vo.HypoxiaParameter import HypoxiaParameter


class HypoxiaPlotDualMgr:

    def __init__(self):
        self.hypApi = HypoxiaApi(HypoxiaUtil.getRootDir())

    def getApiData(self, ncboName, firstDate, beginOffset, endOffset, traverse_order, position):
        beginDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + beginOffset))
        endDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + endOffset))
        hypStationVo = self.hypApi.getDataFromApi(ncboName, beginDateTs, endDateTs)
        self.getStationWithOrder(hypStationVo, traverse_order, position, firstDate)
        return hypStationVo

    def getStationWithOrder(self, hypStationVo, traverse_order, position, firstDateEpoch):
        if hypStationVo is not None and hypStationVo.hypoxiaBuoyVoList is not None:
            firstDate = pytz.UTC.localize(datetime.utcfromtimestamp(firstDateEpoch))
            buoys = hypStationVo.hypoxiaBuoyVoList
            # There is a list of measurements for this station. This is going forward meaning it is the
            # right side of the image
            if traverse_order == TRAVERSE_ORDER.FORWARD:
                hpbvos = []
                aBuoy = buoys[len(buoys) - 1]
                if (abs(aBuoy.time - firstDate).total_seconds()) <= 60 and position == "Post":
                    aBuoy = buoys[len(buoys) - 2]
                hpbvos.append(aBuoy)
                hypStationVo.hypoxiaBuoyVoList = hpbvos
            else:
                # Traverse forward, get the first one
                hpbvos = []  # = HypoxiaBuoyVo()
                aBuoy = buoys[0]
                if (abs(aBuoy.time - firstDate).total_seconds()) <= 60 and position == "Pre":
                    aBuoy = buoys[1]
                hpbvos.append(aBuoy)
                hypStationVo.hypoxiaBuoyVoList = hpbvos
            # self.hypoxiaBuoyVoList.append(hpbvo)
            # station.hypoxiaBuoyVoList = []

    def runDualCTDPlot(self):
        # Get all the casts
        ctdFiles = self.getFiles("data_input/CTD_Data/dataFiles")
        # To run one cast use this
        # ctdFiles = [r"CTD_Data\\2022-06-29 East Maintenance\\CTD Casts\\Processed CTDs\\HYP_E_01906398_2022_06_29_0003.cnv"]
        # r"CTD_Data\\2022-07-15 East Deployment\\CTD Casts\\Processed Data\\HYP_W_01906398_2022_07_15_0008.cnv"]
        # hypApi = HypoxiaApi()
        for ctdFile in ctdFiles:
            logging.debug(f"Reading this CTD File {ctdFile}")
            # read this file. Return the data and the station name
            ncboName, ctdData = self.readCTDData(ctdFile)
            subName = CTDReader.getFileSubname(ctdFile)
            fileTime = CTDReader.getFileTiming(ctdFile)  # Post or Pre
            if len(ctdData) == 0:
                continue
            firstDate = ctdData[0, 0]  # Epoch timestamp
            logging.debug(f"First data point date {firstDate} File: {ctdFile}")

            # Now get the data from the CBIBS API
            # The left
            hypStaBefore = self.getApiData(ncboName, firstDate, -1800, 0, TRAVERSE_ORDER.REVERSE, fileTime)
            hypStaAfter = self.getApiData(ncboName, firstDate, 0, 1800, TRAVERSE_ORDER.FORWARD, fileTime)
            # hypStaPost = self.getApiData(ncboName, firstDate, -600, 2400)

            if hypStaBefore is not None or hypStaAfter is not None:
                dataTemperaturePre = self.getDataFromApiSet(hypStaBefore, HypoxiaParameter.SEA_WATER_TEMP)
                dataTemperaturePost = self.getDataFromApiSet(hypStaAfter, HypoxiaParameter.SEA_WATER_TEMP)
                pltr = PlotTemperatureMgr(firstDate)
                pltr.plotDualTemp(ctdData, dataTemperaturePre, dataTemperaturePost, ncboName, subName, fileTime)

                dataCondPre = self.getDataFromApiSet(hypStaBefore, HypoxiaParameter.CONDUCTIVITY)
                dataCondPost = self.getDataFromApiSet(hypStaAfter, HypoxiaParameter.CONDUCTIVITY)
                pltC = PlotConductivityMgr(firstDate)
                pltC.plotDualConductivity(ctdData, dataCondPre, dataCondPost, ncboName, subName, fileTime)

                # dataSalPre = self.getDataFromApiSet(hypStaBefore, HypoxiaParameter.SEA_WATER_SALINITY)
                # dataSalPost = self.getDataFromApiSet(hypStaAfter, HypoxiaParameter.SEA_WATER_SALINITY)
                # pltS = PlotSalinityMgr(firstDate)
                # pltS.plotDualSalinity(ctdData, dataSalPre, dataSalPost, ncboName, subName, fileTime)

                # dataDoPre = self.getDataFromApiSet(hypStaBefore, HypoxiaParameter.DISSOLVED_OXYGEN_ADJ)
                # dataDoPost = self.getDataFromApiSet(hypStaAfter, HypoxiaParameter.DISSOLVED_OXYGEN_ADJ)
                # Changed this to use NON_Adjusted DO
                dataDoPre = self.getDataFromApiSet(hypStaBefore, HypoxiaParameter.DISSOLVED_OXYGEN)
                dataDoPost = self.getDataFromApiSet(hypStaAfter, HypoxiaParameter.DISSOLVED_OXYGEN)
                pltO = PlotDissolvedO2Mgr(firstDate)
                pltO.plotDissolvedO2(ctdData, dataDoPre, dataDoPost, ncboName, subName, fileTime)

                '''
                dataCondPre = hypStaPre.getCondData()
                dataCondPost = hypStaPost.getCondData()
                HypoxiaPlotterDualNcbo.plotDualCond(ctdData, dataCondPre, dataCondPost, ncboName, subName, fileTime)

                dataSalPre = hypStaPre.getSalData()
                dataSalPost = hypStaPost.getSalData()
                HypoxiaPlotterDualNcbo.plotDualSalinity(ctdData, dataSalPre, dataSalPost, ncboName, subName, fileTime)

                dataDoPre = hypStaPre.getDOData()
                dataDoPost = hypStaPost.getDOData()
                HypoxiaPlotterDualNcbo.plotDualDO(ctdData, dataDoPre, dataDoPost, ncboName, subName, fileTime)
                '''
                # Close after each run
                matplotlib.pyplot.close()
            else:
                logging.warning("*** No data found ***")

    def getDataFromApiSet(self, apiData, hypParameter):
        if apiData is None:
            return None
        paramData = apiData.getFirstParamData(hypParameter.memberName, f"{hypParameter.memberName}_qc_flag")
        return paramData

    ### OLD WAY
    # def runDualCTDPlot(self):
    #     # Get all of the casts
    #     ctdFiles = self.getFiles("CTD_Data/dataFiles")
    #     # To run one cast use this
    #     # ctdFiles = [r"CTD_Data\\2022-06-29 East Maintenance\\CTD Casts\\Processed CTDs\\HYP_E_01906398_2022_06_29_0003.cnv"]
    #     # r"CTD_Data\\2022-07-15 East Deployment\\CTD Casts\\Processed Data\\HYP_W_01906398_2022_07_15_0008.cnv"]
    #     # hypApi = HypoxiaApi()
    #     for ctdFile in ctdFiles:
    #         logging.debug(f"Reading this CTD File {ctdFile}")
    #         # read this file. Return the data and the station name
    #         ncboName, ctdData = self.readCTDData(ctdFile)
    #         subName = CTDReader.getFileSubname(ctdFile)
    #         fileTime = CTDReader.getFileTiming(ctdFile)
    #         if len(ctdData) == 0:
    #             continue
    #         firstDate = ctdData[0, 0]  # Epoch timestamp
    #         # Now get the data from the CBIBS API
    #         hypStaPre = self.getApiData(ncboName, firstDate, 600, 1200)
    #         hypStaPost = self.getApiData(ncboName, firstDate, 0, 1200)
    #
    #         if hypStaPre is not None:
    #             dataTemperaturePre = hypStaPre.getTemperatureData()
    #             dataTemperaturePost = hypStaPost.getTemperatureData()
    #             pltr = PlotTemperatureMgr()
    #             pltr.plotDualTemp(ctdData, dataTemperaturePre, dataTemperaturePost, ncboName, subName, fileTime)
    #
    #             dataCondPre = hypStaPre.getCondData()
    #             dataCondPost = hypStaPost.getCondData()
    #             pltC = PlotConductivityMgr()
    #             pltC.plotDualConductivity(ctdData, dataCondPre, dataCondPost, ncboName, subName, fileTime)
    #
    #             dataSalPre = hypStaPre.getSalData()
    #             dataSalPost = hypStaPost.getSalData()
    #             pltS = PlotSalinityMgr()
    #             pltS.plotDualSalinity(ctdData, dataSalPre, dataSalPost, ncboName, subName, fileTime)
    #
    #             dataDoPre = hypStaPre.getDOData()
    #             dataDoPost = hypStaPost.getDOData()
    #             pltO = PlotDissolvedO2Mgr()
    #             pltO.plotDissolvedO2(ctdData, dataDoPre, dataDoPost, ncboName, subName, fileTime)
    #             # HypoxiaPlotterDualNcbo.plotDualTemp(ctdData, dataTemperaturePre, dataTemperaturePost, ncboName, subName,
    #             #                                    fileTime)
    #             '''
    #             dataCondPre = hypStaPre.getCondData()
    #             dataCondPost = hypStaPost.getCondData()
    #             HypoxiaPlotterDualNcbo.plotDualCond(ctdData, dataCondPre, dataCondPost, ncboName, subName, fileTime)
    #
    #             dataSalPre = hypStaPre.getSalData()
    #             dataSalPost = hypStaPost.getSalData()
    #             HypoxiaPlotterDualNcbo.plotDualSalinity(ctdData, dataSalPre, dataSalPost, ncboName, subName, fileTime)
    #
    #             dataDoPre = hypStaPre.getDOData()
    #             dataDoPost = hypStaPost.getDOData()
    #             HypoxiaPlotterDualNcbo.plotDualDO(ctdData, dataDoPre, dataDoPost, ncboName, subName, fileTime)
    #             '''
    #             # Close after each run
    #             matplotlib.pyplot.close()

    # def getDatesForFile(self, filePath, firstDate):
    #     fileName = Path(filePath).stem
    #     beginDateTs = None
    #     endDateTs = None
    #     pre = re.compile("_Pre_")
    #     post = re.compile("_Post_")
    #     if pre.search(fileName):
    #         # This is before the cast, so use the timestamp before
    #         beginDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate - 600))
    #         endDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 1200))
    #     elif post.search(fileName):
    #         beginDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 600))
    #         endDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 1200))
    #     else:
    #         beginDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 600))
    #         endDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 1200))
    #     # Description not found, use the basic match
    #     return beginDateTs, endDateTs

    # Recursively traverse the directories for processed CTD data
    def getFiles(self, baseDir):
        ROOT_DIR = HypoxiaUtil.getRootDir()
        localBaseDir = os.path.join(ROOT_DIR, baseDir)
        paths = []
        for root, dirs, files in os.walk(localBaseDir):
            for file in files:
                if file.lower().endswith(".cnv"):
                    paths.append(os.path.join(root, file))
        return paths

    def readCTDData(self, ctdFile):
        # Get the name of the station from the cast file
        ncboName = CTDReader.getNcboName(ctdFile)
        # Run the file
        ctdData = CTDReader.processFile(ctdFile)
        return ncboName, ctdData
