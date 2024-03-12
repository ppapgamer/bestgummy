from datetime import datetime

def second_to_str(seconds: int):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    def add_s(string: str, value: int):
        if value != 1:
            return string + "s"
        return string
    final_str = ""
    if (h != 0):
        final_str += f"{h} {add_s('hour', h)} "
    if (m != 0):
        final_str += f"{m} {add_s('minute', m)} "
    final_str += f"{s} {add_s('second', s)}"
    return final_str

def seconds_between(t1: datetime, t2: datetime) -> int:
    return int((t2 - t1).total_seconds())
