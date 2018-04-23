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

_datetime_pattern = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<date>\d{1,2})(\s+"
                               r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<second>\d{1,2}))?\s*"
                               r"(?P<am_pm>AM|PM)?)?$"
                               , re.I)  # format: YEAR-MONTH-DATE HOUR:MIN:SECOND AM/PM

_date_pattern = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<date>\d{1,2})$", re.I)  # format: YEAR-MONTH-DATE

_time_pattern = re.compile(r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<second>\d{1,2}))?(?P<am_pm>AM|PM)?$", re.I)  # HOUR:MIN:SECOND AM/PM


def _s2int(txt):
    txt = txt.strip()
    txt = txt.lstrip('0')
    if txt == '':
        return 0
    return int(txt)


def parse_datetime(txt):
    txt = txt.strip()
    m = _datetime_pattern.match(txt)
    assert m, "Datetime format did not match"
    year = _s2int(m.group('year'))
    month = _s2int(m.group('month'))
    date = _s2int(m.group('date'))
    hour = _s2int(m.group('hour')) if m.group('hour') else 0
    minute = _s2int(m.group('minute')) if m.group('minute') else 0
    second = _s2int(m.group('second')) if m.group('second') else 0
    am_pm = m.group('am_pm').upper() if isinstance(m.group('am_pm'), str) else m.group('am_pm')

    # 24 hour conversion
    if am_pm:
        if am_pm == "PM":
            hour = 12 + hour

    dt = datetime.datetime(year, month, date, hour, minute, second)
    return dt


def parse_date(txt):
    txt = txt.strip()
    m = _date_pattern.match(txt)
    assert m, "Date format did not match"
    year = _s2int(m.group('year'))
    month = _s2int(m.group('month'))
    date = _s2int(m.group('date'))

    dt = datetime.date(year, month, date)
    return dt


def parse_time(txt):
    txt = txt.strip()
    m = _time_pattern.match(txt)
    assert m, "Time format did not match"
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
