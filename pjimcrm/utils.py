"""Various utility functions."""

import datetime
import re

from .models import TimesheetEntry

class TimerRecord:
    description = ""

    def __init__(self, timer: TimesheetEntry):
        timestamp_started_str = ""
        if isinstance(timer.timestamp_started, datetime.datetime):
            timestamp_started_str = timer.timestamp_started.isoformat()
        self.id = timer.id
        self.client_name = timer.project.client.name
        self.project_name = timer.project.name
        self.description = timer.description
        self.description_set = timer.description_set
        self.length_raw = timer.length_raw.total_seconds()
        self.timestamp_started = timestamp_started_str

    def for_json(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "project_name": self.project_name,
            "description": self.description,
            "description_set": self.description_set,
            "length_raw": self.length_raw,
            "timestamp_started": self.timestamp_started,
        }

class TimesheetEntryCurrent:
    def __init__(self, running: bool, timer: TimerRecord | None):
        self.running = running
        self.timer = timer

    def for_json(self):
        if self.timer is None:
            return {
                "running": self.running,
            }

        return {
            "running": self.running,
            "timer": self.timer.for_json(),
        }


def get_running_timers() -> TimesheetEntryCurrent:
    """Get the running timer, if one is running."""
    timers = TimesheetEntry.objects.exclude(timestamp_started=None)
    has_timers = len(timers) > 0
    current_timer = None
    if has_timers:
        current_timer = TimerRecord(timers[0])
        if not current_timer.description_set:
            current_timer.description = ""
    return TimesheetEntryCurrent(has_timers, current_timer)


def parse_timer_length(length_string: str) -> int | None:
    """Parse a timer string (x:xx:xx) into a number of seconds."""
    timesheet_regex = re.compile(r"\d+:\d\d:\d\d")
    if timesheet_regex.match(length_string) is None:
        return None

    length_parts = [int(p) for p in length_string.split(":")]
    return length_parts[0] * (60 * 60) + length_parts[1] * 60 + length_parts[2]
