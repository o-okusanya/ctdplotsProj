import os
from datetime import datetime

import numpy as np
import pytz


class HypoxiaUtil:

    @staticmethod
    def getRootDir(projName="ctdplotsProj"):
        """
        Finds the root of the project and return it as string.
        The root is the directory named
        """
        path, directory = os.path.split(os.path.abspath(__file__))
        while directory and directory != projName:
            path, directory = os.path.split(path)
        if directory == projName:
            return os.path.join(path, directory)
        else:
            raise Exception("Couldn't determine path to the project root.")

    @staticmethod
    def utcDateChange(X):
        ''' Always use this function when changing date vectors '''
        return pytz.UTC.localize(X)

    @staticmethod
    def vectorDateChange(X):
        ''' Always use this function when changing date vectors '''
        return pytz.UTC.localize(datetime.utcfromtimestamp(X))

    @staticmethod
    def createEmptyTimes(beginTime, endTime):
        epochArray = np.arange(beginTime.timestamp(), endTime.timestamp(), 600, np.int32)
        dateconv = np.vectorize(HypoxiaUtil.vectorDateChange)
        dTime = dateconv(epochArray)
        return dTime

    @staticmethod
    def createEmptyDate(beginTime, endTime):
        epochArray = np.arange(beginTime.timestamp(), endTime.timestamp(), 600)
        # dateconv = np.vectorize(HypoxiaUtil.vectorDateChange)
        # dTime = dateconv(epochArray)
        return epochArray

    @staticmethod
    def vectorCondChange(X):
        ''' Always use this function when changing date vectors '''
        return X*10