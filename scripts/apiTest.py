import re

from scripts import scriptBase

def main():

    fileName = "CHOMA_01_Post_2023_05_08_0007"
    postStr = r"_Post_(\d\d\d\d)_"
    # matches = re.findall(postStr, fileName)
    post = re.search(postStr,fileName)
    if post:
        x = post.group(1)
    print(x)
    #hypApi = ()
    #hypApi.testApiQuery()
    # hypApi.testApiData()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Starting app")
    scriptBase.setupLogging("runErrdap.log")
    main()


