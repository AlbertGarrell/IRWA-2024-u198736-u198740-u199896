import json
import random
from datetime import datetime
import httpagentparser
import os
import csv

from myapp.analytics.util import get_location


class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """
    def __init__(self):
        self.fact_clicks = {}  # {doc_id: click_count}
        self.search_queries = []  # List of (query, timestamp, num_terms)
        self.session_data = {}  # {session_id: {data}}
        self.query_results_clicks = []  # List of (query, result_rank, doc_id, dwell_time)
        self.http_logs = []


    def save_query_terms(self, terms: str, session_id: str):
        """
        Save search query and related details.
        """
        num_terms = len(terms.split())
        
        print(f"Saved query: {terms}")

        file_path = "./data_storage/search_queries.csv"
        # Check if the file exists, and read the last event_id if it does
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                # If there are rows, get the last event_id
                if rows:
                    last_event_id = int(rows[-1][0])  # First column contains event_id
                else:
                    last_event_id = -1
        else:
            last_event_id = -1

        # Increment event_id
        event_id = last_event_id + 1

        # Prepare data to write into the CSV
        row = [
            event_id,
            terms,
            session_id,
            num_terms,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]

        # Write the data to the CSV in append mode
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if last_event_id == -1:
                writer.writerow(["event_id","query","session_id","num_terms", "timestamp"])
            # Append the new row
            writer.writerow(row)


    
    def save_click(self, doc_id: int, query: str, dwell_time=None):
        """
        Save a click action and its metadata.
        """
        file_path = "./data_storage/click_logs.csv"
        # Check if the file exists, and read the last event_id if it does
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                # If there are rows, get the last event_id
                if rows:
                    last_event_id = int(rows[-1][0])  # First column contains event_id
                else:
                    last_event_id = -1
        else:
            last_event_id = -1

        # Increment event_id
        event_id = last_event_id + 1

        # Prepare data to write into the CSV
        row = [
            event_id,
            query,
            doc_id,
            dwell_time
        ]

        # Write the data to the CSV in append mode
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if last_event_id == -1:
                writer.writerow(["event_id","query", "doc_id", "dwell_time"])
            # Append the new row
            writer.writerow(row)

    def save_session_data(self, session_id: str, user_agent: dict, ip_address: str, timestamp: datetime):
        """
        Save session data, including user context.
        """
        ip_adress_false = '95.23.82.164'
        country, city = get_location(ip_adress_false)


        agent = httpagentparser.detect(user_agent)  

        # Prepare session data
        session_info = {
            "session_id": session_id,
            "ip_address": ip_address,
            "OS": agent['platform']['name'],
            "browser": agent['browser']['name'],
            "country": country,
            "city": city,
            "start_time": timestamp
        }

        # Determine the file path
        file_path = "./data_storage/session_data.csv"

        # Check if the file exists, and read the last event_id if it does
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                # If there are rows, get the last event_id
                if rows:
                    last_event_id = int(rows[-1][0])  # First column contains event_id
                else:
                    last_event_id = -1
        else:
            last_event_id = -1

        # Increment event_id
        event_id = last_event_id + 1

        # Prepare data to write into the CSV
        row = [
            event_id, 
            session_info["session_id"],
            session_info["ip_address"],
            session_info["OS"],
            session_info["browser"],
            session_info["country"],
            session_info["city"],
            session_info["start_time"].strftime('%Y-%m-%d %H:%M:%S')
        ]

        # Write the data to the CSV in append mode
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if last_event_id == -1:
                writer.writerow(["event_id", "session_id", "IP", "OS", "Browser", "Country", "City", "timestamp_init"])
            # Append the new row
            writer.writerow(row)

        # Save session data to the dictionary
        self.session_data[session_id] = session_info

        print(f"Session data saved: {self.session_data[session_id]}")
    
    def save_http_log(self, ip, http_method, requested_url, http_version, response_status):
        """
        Save HTTP log data, including the response status.
        """
        log_entry = {
            "ip": ip,
            "http_method": http_method,
            "requested_url": requested_url,
            "http_version": http_version,
            "response_status": response_status,
            "timestamp": datetime.now(),
        }
        # Determine the file path
        file_path = "./data_storage/http_logs.csv"

        # Check if the file exists, and read the last event_id if it does
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                # If there are rows, get the last event_id
                if rows:
                    last_event_id = int(rows[-1][0])  # First column contains event_id
                else:
                    last_event_id = -1
        else:
            last_event_id = -1

        # Increment event_id
        event_id = last_event_id + 1

        # Prepare data to write into the CSV
        row = [
            event_id,
            log_entry["ip"],
            log_entry["http_method"],
            log_entry["requested_url"],
            log_entry["http_version"],
            log_entry["response_status"],
            log_entry["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
        ]

        # Write the data to the CSV in append mode
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if last_event_id == -1:
                writer.writerow(["event_id", "ip", "http_method", "requested_url", "http_version", "response_status", "timestamp"])
            # Append the new row
            writer.writerow(row)

        # Save the log entry to the internal list (optional)
        self.http_logs.append(log_entry)

        #print(f"Saved HTTP log: {log_entry}")

class HttpLog:
    def __init__(self, ip, http_method, requested_url, http_version, response_status, timestamp):
        self.ip = ip
        self.http_method = http_method
        self.requested_url = requested_url
        self.http_version = http_version
        self.response_status = response_status
        self.timestamp = timestamp

    def to_json(self):
        return {
            "ip": self.ip,
            "http_method": self.http_method,
            "requested_url": self.requested_url,
            "http_version": self.http_version,
            "response_status": self.response_status,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=4)


class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
