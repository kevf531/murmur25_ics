from icalendar import Calendar, Event
from datetime import datetime, timezone
import pandas as pd
import os
from typing import Optional


class ICSGenerator:
    """Converts pandas DataFrame to ICS calendar format"""

    def __init__(self, calendar_name: str = "Murmur 2025 Schedule"):
        self.calendar_name = calendar_name
