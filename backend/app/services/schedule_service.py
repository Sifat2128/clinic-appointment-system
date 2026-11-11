from datetime import datetime, timedelta
from typing import List


def generate_time_slots(start_time_str: str, end_time_str: str, slot_duration_minutes: int) -> List[str]:
    """Generates continuous discrete consultation time slot strings between start and end times.
    
    Example:
        generate_time_slots("09:00", "11:00", 30) -> ["09:00", "09:30", "10:00", "10:30"]
    """
    time_format = "%H:%M"
    start_dt = datetime.strptime(start_time_str, time_format)
    end_dt = datetime.strptime(end_time_str, time_format)

    if end_dt <= start_dt:
        return []

    slots: List[str] = []
    current_dt = start_dt
    delta = timedelta(minutes=slot_duration_minutes)

    while current_dt + delta <= end_dt:
        slots.append(current_dt.strftime(time_format))
        current_dt += delta

    return slots
