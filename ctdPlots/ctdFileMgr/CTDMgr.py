import re


class CTDMgr:

    @staticmethod
    def getOffset(filename):
        if re.search('HYP_E_6913_2022_05_16_0004.cnv', filename) is not None:
            return 2
        elif re.search('HYP_E_Gooses_deploy_6913_2022_05_16_0006.cnv', filename) is not None:
            return 2
        elif re.search('HYP_W_6913_2022_05_16_0005.cnv', filename) is not None:
            return 2
        elif re.search('HYP_E_6913_2022_06_01_007.cnv', filename) is not None:
            return 3
        elif re.search('HYP_E_6913_2022_06_01_008.cnv', filename) is not None:
            return 3
        elif re.search('HYP_E_01906398_2022_06_17_0002.cnv', filename) is not None:
            return -1
        elif re.search('HYP_E_01906913_2022_06_17_0010.cnv', filename) is not None:
            return -1
        elif re.search('HYP_W_01906398_2022_06_17_0001.cnv', filename) is not None:
            return 1
        elif re.search('HYP_E_01906398_2022_06_29_0003.cnv', filename) is not None:
            return 0
        elif re.search('HYP_E_01906398_2022_06_30_0004.cnv', filename) is not None:
            return 0
        elif re.search('HYP_E_01906398_2022_06_30_0005.cnv', filename) is not None:
            return 0
        elif re.search('HYP_W_01906398_2022_06_30_0006.cnv', filename) is not None:
            return 0
        elif re.search('HYP_W_01906398_2022_06_30_0007.cnv', filename) is not None:
            return 0
        elif re.search('HYP_W_01906398_2022_07_15_0008.cnv', filename) is not None:
            return 0
        elif re.search('HYP_E_01906398_2022_07_15_0009.cnv', filename) is not None:
            return 0
        elif re.search('HYP_E_01906398_2022_07_26_0010.cnv', filename) is not None:
            return 0
        elif re.search('HYP_E_01906398_2022_07_26_0011.cnv', filename) is not None:
            return 0
        elif re.search('HYP_W_01906398_2022_07_26_0012.cnv', filename) is not None:
            return 0
        # Adjustment for after EDT ended
        elif re.search('CB5MH_01_Post_2023_11_15_0084.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('CB5MH_01_Pre_2023_11_06_0082.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('CB5MH_01_Pre_2023_11_15_0085.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('CHOMA_01_Post_2023_11_15_0088.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('CHOMA_01_Post_2023_11_30_0090.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('CHOMA_01_Pre_2023_11_06_0083.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('CHOMA_01_Pre_2023_11_15_0086.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('CHOMA_01_Pre_2023_11_30_0089.cnv', filename) is not None:
            return -1
        # Adjustment for after EDT ended
        elif re.search('POTMH_01_2023_11_15_0087.cnv', filename) is not None:
            return -1
        # No adjustment needed
        elif re.search('CB5MH_01_Pre_2023_12_22_0091.cnv', filename) is not None:
            return -1
        elif re.search('CHOMA_01_Post_2023_12_22_0093.cnv', filename) is not None:
            return -1
        elif re.search('CHOMA_01_Pre_2023_12_22_0092.cnv', filename) is not None:
            return -1
        # elif re.search('PTOMH_01_Post_2023_05_25_0011.cnv', filename) is not None:
        #     return -1
        return 0
