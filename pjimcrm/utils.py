from .models import Client, Project, Invoice, TimesheetEntry

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
        if not current_timer['description_set']:
            current_timer['description'] = ""
    return { "running": has_timers, "timer": current_timer }
