import logging
import os, sys

from ctdPlots.HypoxiaUtil import HypoxiaUtil

projName = 'CTDPlots'
'''
    # # The demo test code
    # mylogs.debug("The debug")
    # mylogs.info("The info")
    # mylogs.warning("The warn")mik
    # mylogs.error("The error")
    # mylogs.critical("The critical")
    # mylogs = logging.getLogger(__name__)
'''


def setupLogging(logName):
    if logName.endswith(".py"):
        logName = logName.replace(".py", ".log")

    # Get the global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger(__name__)
    createStreamHandler(logger, logging.DEBUG)
    createFileHandler(logger, logName, logging.DEBUG)
    createErrorFileHandler(logger, logName, logging.ERROR)


def createStreamHandler(myLogger, logLevel):
    # create console handler and set level to info
    streamHandler = logging.StreamHandler(stream=sys.stdout)
    streamHandler.setLevel(logLevel)
    streamHandler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    myLogger.addHandler(streamHandler)
    # Quick test
    myLogger.debug("Testing logging.StreamHandler")


def createFileHandler(myLogger, logName, logLevel):
    # create debug file handler and set level to debug
    logFileName = os.path.join(HypoxiaUtil.getRootDir(projName), "logs", logName)
    fileHandler = logging.FileHandler(logFileName, "a")
    fileHandler.setLevel(logLevel)
    fileHandler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    myLogger.addHandler(fileHandler)


def createErrorFileHandler(myLogger, logName, logLevel):
    errorLogFileName = os.path.join(HypoxiaUtil.getRootDir(projName), "logs", logName + "_error.log")
    errorHandler = logging.FileHandler(errorLogFileName, "a")
    errorHandler.setLevel(logLevel)
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                  datefmt='%H:%M:%S')
    errorHandler.setFormatter(formatter)
    myLogger.addHandler(errorHandler)
    # myLogger.error("Testing streamHandler")