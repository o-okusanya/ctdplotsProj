import logging
import os
from datetime import datetime
import re
import pytz
from pathlib import Path

from ctdPlots.HypoxiaApi import HypoxiaApi
from ctdPlots.ctdFileMgr import CTDReader
from ctdPlots import HypoxiaPlotterNcbo
from ctdPlots.HypoxiaUtil import HypoxiaUtil
from scripts import scriptBase

class HypoxiaPlotMgr:

    def runSingleCTDPlot(self):
        scriptBase.setupLogging("ncboCTDPlot.txt")
        # Get all of the casts
        ctdFiles = self.getFiles("CTD_Data")
        # To run one cast use this
        # ctdFiles = [r"CTD_Data\\2022-06-29 East Maintenance\\CTD Casts\\Processed CTDs\\HYP_E_01906398_2022_06_29_0003.cnv"]
        # r"CTD_Data\\2022-07-15 East Deployment\\CTD Casts\\Processed Data\\HYP_W_01906398_2022_07_15_0008.cnv"]
        hypApi = HypoxiaApi()
        for ctdFile in ctdFiles:
            logging.debug(f"Reading this CTD File {ctdFile}")
            # read this file. Return the data and the station name
            ncboName, ctdData = self.readCTDData(ctdFile)
            subName = CTDReader.getFileSubname(ctdFile)
            if len(ctdData) == 0:
                continue
            firstDate = ctdData[0, 0]  # Epoch timestamp
            beginDateTs, endDateTs = self.getDatesForFile(ctdFile, firstDate)
            # Now get the data from the CBIBS API
            hypSta = hypApi.getDataFromApi(ncboName, beginDateTs, endDateTs)
            if hypSta is not None:
                hypTime, hypDepth, hypData = hypSta.getTempData()
                HypoxiaPlotterNcbo.plotTemp(ctdData, hypTime, hypDepth, hypData, ncboName, subName)

                hypTime, hypDepth, hypData = hypSta.getDOData()
                HypoxiaPlotterNcbo.plotDO(ctdData, hypTime, hypDepth, hypData, ncboName, subName)

                hypTime, hypDepth, hypData = hypSta.getSalData()
                HypoxiaPlotterNcbo.plotSalinity(ctdData, hypTime, hypDepth, hypData, ncboName, subName)

                hypTime, hypDepth, hypData = hypSta.getCondData()
                HypoxiaPlotterNcbo.plotConductivity(ctdData, hypTime, hypDepth, hypData, ncboName, subName)



    def getDatesForFile(filePath, firstDate):
        fileName = Path(filePath).stem
        beginDateTs = None
        endDateTs = None
        pre = re.compile("_Pre_")
        post = re.compile("_Post_")
        if pre.search(fileName):
            # This is before the cast, so use the timestamp before
            beginDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 600))
            endDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 1200))
        elif post.search(fileName):
            beginDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 600))
            endDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 1200))
        else:
            beginDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 600))
            endDateTs = pytz.UTC.localize(datetime.utcfromtimestamp(firstDate + 1200))
        # Description not found, use the basic match
        return beginDateTs, endDateTs

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
        ncboName = CTDReader.getNcboName(ctdFile)
        # Run the file
        ctdData = CTDReader.processFile(ctdFile)

        return ncboName, ctdData