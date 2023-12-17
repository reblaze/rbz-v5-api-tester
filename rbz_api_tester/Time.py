from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

def convert_time_macros(general: str) -> str:
    final = general.replace("@@NOW()@@", convert("@@NOW()@@"))
    pattern = r"\@\@NOW\([-+]\d*[a-z]*\)\@\@"
    matches = re.findall(pattern, general)
    if matches:
        for match in matches:
            final = final.replace(match, convert(match))        
    return final

def convert(time_str: str) -> str:
    if not time_str.startswith("@@NOW("):
        raise Exception(f"Unrecognized Time Param: {time_str}")
    now = datetime.utcnow()
    current_date = now.date()
    current_time = now.time()
    final = now

    formatted_date = final.strftime("%Y-%m-%d")
    formatted_time = final.strftime("%H:%M:%S")

    tm = time_str.strip("@@")
    if tm == "NOW()":
        return f"{formatted_date} {formatted_time}"
    else:
        pattern = r"NOW\((?P<sign>[-+])(?P<num>\d*)(?P<unit>.*)\)"
        match = re.match(pattern, tm)
        if match:
            sign = match.group("sign")
            num = int(match.group("num"))
            unit = match.group("unit")
        else:
            raise Exception(f"Unrecognized Time Param: {time_str}")

        if unit.lower() == "years":
            if sign == "-":
                final = now - relativedelta(years=num)
            elif sign == "+":
                final = now + relativedelta(years=num)
            else:
                raise Exception(f"Unrecognized Time Param: {time_str}")
        elif unit.lower() == "months":
            if sign == "-":
                final = now - relativedelta(months=num)
            elif sign == "+":
                final = now + relativedelta(months=num)
            else:
                raise Exception(f"Unrecognized Time Param: {time_str}")
        elif unit.lower() == "weeks":
            if sign == "-":
                final = now - relativedelta(weeks=num)
            elif sign == "+":
                final = now + relativedelta(weeks=num)
            else:
                raise Exception(f"Unrecognized Time Param: {time_str}")
        elif unit.lower() == "days":
            if sign == "-":
                final = now - relativedelta(days=num)
            elif sign == "+":
                final = now + relativedelta(days=num)
            else:
                raise Exception(f"Unrecognized Time Param: {time_str}")
        elif unit.lower() == "hours":
            if sign == "-":
                final = now - relativedelta(hours=num)
            elif sign == "+":
                final = now + relativedelta(hours=num)
            else:
                raise Exception(f"Unrecognized Time Param: {time_str}")
        elif unit.lower() == "minutes":
            if sign == "-":
                final = now - relativedelta(minutes=num)
            elif sign == "+":
                final = now + relativedelta(minutes=num)
            else:
                raise Exception(f"Unrecognized Time Param: {time_str}")
        elif unit.lower() == "seconds":
            if sign == "-":
                final = now - relativedelta(seconds=num)
            elif sign == "+":
                final = now + relativedelta(seconds=num)
            else:
                raise Exception(f"Unrecognized Time Param: {time_str}")

        formatted_date = final.strftime("%Y-%m-%d")
        formatted_time = final.strftime("%H:%M:%S")
        return f"{formatted_date} {formatted_time}"