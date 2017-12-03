import re
import datetime

_datetime_pattern = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<date>\d{1,2})\s+"
                               r"(?P<hour>\d+):(?P<minute>\d+):(?P<second>)\s+"
                               r"(?P<am_pm>AM|PM)?$"
                               , re.I)  # format: YEAR-MONTH-DATE HOUR:MIN:SECOND AM/PM


def parse_datetime(txt):
    m = re.match(txt)
    assert m, "Datetime format did not match"
    year = int(m.group('year'))
    month = int(m.group('month'))
    date = int(m.group('date'))
    hour = int(m.group('hour'))
    minute = int(m.group('minute'))
    second = int(m.group('second'))
    am_pm = m.group('am_pm').upper() if isinstance(m.group('am_pm'), str) else m.group('am_pm')

    # 24 hour conversion
    if am_pm:
        if am_pm == "PM":
            hour = 12 + hour

    dt = datetime.datetime(year, month, date, hour, minute, second)
    return dt
