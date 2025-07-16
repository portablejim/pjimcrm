import re

from .models import TimesheetEntry


def get_running_timers():
    timers = TimesheetEntry.objects.exclude(timestamp_started=None)
    has_timers = len(timers) > 0
    current_timer = {}
    if has_timers:
        current_timer = {
            "id": timers[0].id,
            "client_name": timers[0].project.client.name,
            "project_name": timers[0].project.name,
            "description": timers[0].description,
            "description_set": timers[0].description_set,
            "length_raw": timers[0].length_raw.total_seconds(),
            "timestamp_started": timers[0].timestamp_started.isoformat(),
        }
        if not current_timer["description_set"]:
            current_timer["description"] = ""
    return {"running": has_timers, "timer": current_timer}


def parse_timer_length(length_string: str) -> int:
    timesheet_regex = re.compile(r"\d+:\d\d:\d\d")
    if timesheet_regex.match(length_string) is None:
        return None

    length_parts = [int(p) for p in length_string.split(":")]
    length_total = length_parts[0] * (60 * 60) + length_parts[1] * 60 + length_parts[2]
    return length_total
