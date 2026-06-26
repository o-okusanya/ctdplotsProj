class QCEvaluator:
    def __init__(self, failLow, failHigh, suspectLow, suspectHigh):
        self.failLow = failLow
        self.failHigh = failHigh
        self.suspectLow = suspectLow
        self.suspectHigh = suspectHigh
        self.GOOD = 1
        self.SUSPECT = 3
        self.FAIL = 4
        self.MISSING = 9

    def evaluateDifference(self, difference):
        if difference is None:
            return self.MISSING
        if difference < self.failLow or difference > self.failHigh:
            return self.FAIL
        if difference < self.suspectLow or difference > self.suspectHigh:
            return self.SUSPECT
        else:
            return self.GOOD

    def evaluateList(self, axis, tableList):
        flags = []
        colors = []
        for row in tableList:
            difference = row[6]  #5th column is the difference
            flags.append(self.evaluateDifference(difference))
        #Evaluating the colors
        for i in range(len(tableList)):
            if flags[i] == 4:
                # outside suspect range failed
                colors.append(["white", "white", "white", "white", "white", "red"])
                axis.axhline(tableList[i][0], color='red', lw=0.25)  # y = 0
            elif flags[i] == 3:
                # inside suspect range
                colors.append(["white", "white", "white", "white", "white", "orange"])
                axis.axhline(tableList[i][0], color='red', lw=0.25)  # y = 0
            else:
                # either none or the ranges
                colors.append(["white", "white", "white", "white", "white", "white"])
                axis.axhline(tableList[i][0], color='black', lw=0.25)  # y = 0
        return colors