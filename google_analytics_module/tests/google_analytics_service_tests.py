
import sys
import os
# insert current path to system path, so that we can import python file
sys.path.insert(1, os.getcwd())
from datetime import date
from google_analytics_module.services.google_analytics_service import GoogleAnalyticsService


google_analytics_service = GoogleAnalyticsService()
start_date = date(2023,7,1)
end_date = date(2024,6,30)
dataset_id = "0QK91R12" # Burnside
sessions_by_landing_page = google_analytics_service.get_sessions_by_landing_page(dataset_id, start_date, end_date)
op = 0