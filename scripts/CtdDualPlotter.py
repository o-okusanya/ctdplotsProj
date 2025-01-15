import logging
import os

from scripts import scriptBase
from ctdPlots.HypoxiaPlotDualMgr import HypoxiaPlotDualMgr


def main():
    # Setup logging
    scriptBase.setupLogging(os.path.basename(__file__))
    logging.info("String the app")

    hpdm= HypoxiaPlotDualMgr()
    hpdm.runDualCTDPlot()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Starting app")

    main()
