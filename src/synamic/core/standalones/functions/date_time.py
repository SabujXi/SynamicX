"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import re
import datetime

_datetime_pattern = re.compile(r"^\s*(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<date>\d{1,2})\s*(\s+"
                               r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<second>\d{1,2}))?\s*"
                               r"(?P<am_pm>AM|PM)?)?\s*$"
                               , re.I)  # format: YEAR-MONTH-DATE HOUR:MIN:SECOND AM/PM

_date_pattern = re.compile(r"^\s*(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<date>\d{1,2})\s*$", re.I)  # format: YEAR-MONTH-DATE

_time_pattern = re.compile(r"\s*(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<second>\d{1,2}))?\s*(?P<am_pm>AM|PM)?\s*$", re.I)  # HOUR:MIN:SECOND AM/PM

ReMatchType = type(re.match('', ''))


class DtPatterns:
    datetime = _datetime_pattern
    date = _date_pattern
    time = _time_pattern


def _s2int(txt):
    txt = txt.strip()
    txt = txt.lstrip('0')
    if txt == '':
        return 0
    return int(txt)


def parse_datetime(txt) -> datetime.datetime:
    if type(txt) is datetime.datetime:
        return txt
    elif type(txt) is not ReMatchType:
        txt = txt.strip()
        m = _datetime_pattern.match(txt)
        assert m, "Datetime format did not match"
    else:
        m = txt
        assert m.re is DtPatterns.datetime
    year = _s2int(m.group('year'))
    month = _s2int(m.group('month'))
    date = _s2int(m.group('date'))
    hour = _s2int(m.group('hour')) if m.group('hour') else 0
    minute = _s2int(m.group('minute')) if m.group('minute') else 0
    second = _s2int(m.group('second')) if m.group('second') else 0
    am_pm = m.group('am_pm').upper() if isinstance(m.group('am_pm'), str) else m.group('am_pm')

    # 24 hour conversion
    if am_pm:
        assert hour < 13, 'Hour cannot be greater than 12 when am/pm specified: %s' % txt
        if am_pm == "PM":
            hour = 12 + hour

    dt = datetime.datetime(year, month, date, hour, minute, second)
    return dt


def parse_date(txt) -> datetime.date:
    if type(txt) is datetime.date:
        return txt
    elif type(txt) is not ReMatchType:
        txt = txt.strip()
        m = _date_pattern.match(txt)
        assert m, "Date format did not match"
    else:
        m = txt
        assert m.re is DtPatterns.date
    year = _s2int(m.group('year'))
    month = _s2int(m.group('month'))
    date = _s2int(m.group('date'))

    dt = datetime.date(year, month, date)
    return dt


def parse_time(txt) -> datetime.time:
    if type(txt) is datetime.time:
        return txt
    elif type(txt) is not ReMatchType:
        txt = txt.strip()
        m = _time_pattern.match(txt)
        assert m, "Time format did not match"
    else:
        m = txt
        assert m.re is DtPatterns.time
    hour = _s2int(m.group('hour')) if m.group('hour') else 0
    minute = _s2int(m.group('minute')) if m.group('minute') else 0
    second = _s2int(m.group('second')) if m.group('second') else 0
    am_pm = m.group('am_pm').upper() if isinstance(m.group('am_pm'), str) else m.group('am_pm')

    # 24 hour conversion
    if am_pm:
        if am_pm == "PM":
            hour = 12 + hour

    t = datetime.time(hour, minute, second)
    return t
