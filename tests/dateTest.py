import datetime as dt

import pytz


def edt(rawJulianDate, offset):
    # This should be about 10:41 EDT
    # UTC time is 4 hours ahead of EDT

    # Create a timezone in the east coast then a date at the beginning of the year
    tz = pytz.timezone('America/New_York')
    yearStartDate1 = dt.datetime(2022, 1, 1, 0, 0)  # , tzinfo=tz)
    yearStartDate = tz.localize(yearStartDate1)
    # yearStartDate= yearStartDate.astimezone(tz)
    # Add that day fraction
    start = yearStartDate + dt.timedelta(hours=offset, days=rawJulianDate - 1)
    print(f"start America/New_York {start}, {start.timestamp()} Input:{rawJulianDate}")

'''
def utc(rawJulianDate):
    # Create a timezone in the east coast then a date at the beginning of the year
    tzUTC = pytz.timezone('UTC')
    yearStartDateUTC1 = dt.datetime(2022, 1, 1, 0, 0)
    yearStartDateUTC = tzUTC.localize(yearStartDateUTC1)
    yearStartDateUTC = yearStartDateUTC.astimezone(tzUTC)  # tzUTC.localize(yearStartDateUTC)
    # Add that day fraction
    startUTC = yearStartDateUTC + dt.timedelta(hours=+3, days=rawJulianDate - 1)
    print(f"start UTC              {startUTC}, {startUTC.timestamp()} Input:{rawJulianDate}")

'''

rawJulianDate = 136.338403  # 207.445243
edt(rawJulianDate, +2)
# utc(rawJulianDate)

rawJulianDate = 136.367083  # 207.445243
edt(rawJulianDate, +2)
# utc(rawJulianDate)

rawJulianDate = 136.402488  # 207.445243
edt(rawJulianDate, +2)
# utc(rawJulianDate)

rawJulianDate = 152.273414  # 207.445243
edt(rawJulianDate, -4)
