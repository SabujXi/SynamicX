import re
import datetime

_datetime_pattern = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<date>\d{1,2})(\s+"
                               r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<second>\d{1,2}))?\s*"
                               r"(?P<am_pm>AM|PM)?)?$"
                               , re.I)  # format: YEAR-MONTH-DATE HOUR:MIN:SECOND AM/PM


def parse_datetime(txt):
    txt = txt.strip()
    m = _datetime_pattern.match(txt)
    assert m, "Datetime format did not match"
    year = int(m.group('year'))
    month = int(m.group('month').lstrip('0'))
    date = int(m.group('date').lstrip('0'))
    hour = int(m.group('hour').lstrip('0')) if m.group('hour') else 0
    minute = int(m.group('minute').lstrip('0')) if m.group('minute') else 0
    second = int(m.group('second').lstrip('0')) if m.group('second') else 0
    am_pm = m.group('am_pm').upper() if isinstance(m.group('am_pm'), str) else m.group('am_pm')

    # 24 hour conversion
    if am_pm:
        if am_pm == "PM":
            hour = 12 + hour

    dt = datetime.datetime(year, month, date, hour, minute, second)
    return dt

