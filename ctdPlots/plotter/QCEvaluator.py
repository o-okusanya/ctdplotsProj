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

    def evaluateList(self, tableList):
        flags = []
        for row in tableList:
            difference = row[4]  # col 4 is the difference
            flags.append(self.evaluateDifference(difference))
        return flags