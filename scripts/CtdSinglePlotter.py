import logging
import os

from ctdPlots.HypoxiaPlotDualMgr import HypoxiaPlotDualMgr
from ctdPlots.HypoxiaPlotMgr import HypoxiaPlotMgr
from scripts import scriptBase


def main():
    # Setup logging
    scriptBase.setupLogging(os.path.basename(__file__))
    logging.info("String the app")

    hpm = HypoxiaPlotMgr()
    hpm.runSingleCTDPlot()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Starting app")

    main()
