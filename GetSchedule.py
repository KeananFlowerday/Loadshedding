import requests
import configparser
import json
from datetime import datetime

# Function to check if a time range is within an event's start and end times
def is_time_range_within_event(event_start_time, event_end_time, time_range):
    start_str, end_str = time_range.split('-')
    start_time = datetime.strptime(start_str, '%H:%M').time()
    end_time = datetime.strptime(end_str, '%H:%M').time()
    return event_start_time <= start_time and event_end_time >= end_time

def get_load_shedding_times(area_name=None, area_id=None):
    # Replace 'YOUR_ACCESS_TOKEN' with your access token if required
    read_config = configparser.ConfigParser()
    read_config.read("ESP.ini")
    token = read_config.get("Creds", "Token")
    areaid_url = read_config.get("Creds", "ACTION_GET_AREAID_URL")
    areainfo_url = read_config.get("Creds", "ACTION_GET_AREAINFO_URL")

    headers = {
        'token': token,  # Replace with your access token
    }
    if area_name is None:
        area_name = read_config.get("Creds", "AREA_NAME")
    if area_id is None:
        area_id = read_config.get("Creds", "AREA_ID")
    # Make the API request with the specified zone if area_id is not provided
    if area_id is None:
        response = requests.get(areaid_url, headers=headers, params={'text': area_name})
        if response.status_code == 200:
            data = json.loads(response.content)
            if data:
                myArea = data["areas"][0]  # Assuming the first result is the next schedule
                area_id = myArea["id"]
            else:
                return None  # No zone found for the provided area_name
        else:
            return None  # Failed to retrieve load shedding data

    response2 = requests.get(areainfo_url, headers=headers, params={'id': area_id})
    if response2.status_code == 200:
        data2 = json.loads(response2.content)
        if data2:
            load_shedding_by_day = {}

            for event in data2["events"]:
                note = event.get("note", "")
                start_time = datetime.fromisoformat(event.get("start", ""))
                end_time = datetime.fromisoformat(event.get("end", ""))

                current_schedule = None
                for day_schedule in data2["schedule"]["days"]:
                    if day_schedule["date"] == start_time.strftime("%Y-%m-%d"):
                        current_schedule = day_schedule
                        break

                if current_schedule:
                    event_start_time = start_time.time()
                    event_end_time = end_time.time()
                    stage_index = int(note.split()[1]) - 1  # Extract stage number from note
                    stage_schedule = current_schedule["stages"][stage_index]  # Get the schedule for the specific stage
                    load_shedding_times = []

                    for time_range in stage_schedule:
                        if is_time_range_within_event(event_start_time, event_end_time, time_range):
                            load_shedding_times.append(time_range)

                    if load_shedding_times:
                        day_key = start_time.strftime("%A - %m/%d/%Y")
                        if day_key not in load_shedding_by_day:
                            load_shedding_by_day[day_key] = []

                        for time_slot in load_shedding_times:
                            load_shedding_by_day[day_key].append(f"{time_slot} - {note}")
                else:
                    print(f"No schedule found for Event: {note}")

            return load_shedding_by_day

    else:
        return None  # Failed to retrieve load shedding data

# Example usage:
# load_shedding_times = get_load_shedding_times(area_name="YourAreaName")
# if load_shedding_times:
#     for day, times in load_shedding_times.items():
#         print(day)
#         for time_slot in times:
#             print(time_slot)
#         print()
