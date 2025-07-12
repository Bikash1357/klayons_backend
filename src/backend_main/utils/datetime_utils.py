def time_diff_to_string(time_diff):
    seconds = round(time_diff.total_seconds())
    abs_seconds = abs(seconds)

    if abs_seconds < 60:
        unit = "second"
        value = abs_seconds
    elif abs_seconds < 3600:
        unit = "minute"
        value = abs_seconds / 60
    elif abs_seconds < 86400:
        unit = "hour"
        value = abs_seconds / 3600
    else:
        unit = "day"
        value = abs_seconds / 86400

    rounded_value = int(round(value))
    plural = "" if rounded_value == 1 else "s"

    return f"{rounded_value} {unit}{plural}"
