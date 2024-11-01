"""test methods, easy for debugging in python code"""
import sys
import os


# insert current path to system path, so that we can import python file
sys.path.insert(1, os.getcwd())

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
from datetime import date
from google_analytics_module.services.google_analytics_service import (
    GoogleAnalyticsService,
)
from dotenv import load_dotenv
# pylint: enable=wrong-import-order
# pylint: enable=wrong-import-position

load_dotenv()

google_analytics_service = GoogleAnalyticsService()
start_date = date(2023, 7, 1)
end_date = date(2024, 6, 30)
# dataset_id = "0QK91R12" # Burnside
ORGANISATION_ID = "202703"

sessions_count = google_analytics_service.get_sessions_by_organisation_id(
    start_date, end_date, ORGANISATION_ID
)
print("sessions count ", sessions_count)
