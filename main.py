import datetime
import os.path
from tkinter import *
from tkinter.ttk import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

root = Tk()
root.title("Décompte avant la mort")

lbl = Label(root, font=('calibri', 100, 'bold'),
            background='white',
            foreground='black')

lbl.pack(anchor='center')

def clock(time_left, event_time, event_end, status):
    if status == 1:
        lbl.config(text=str(f"Time before: {time_left}"))
    elif status == 2:
        lbl.config(text=str(f"Time left: {time_left}"))
    lbl.after(1000, lambda: update_clock(event_time, event_end))

def update_clock(event_time, event_end):
    current_time = datetime.datetime.utcnow().replace(microsecond=0)
    time_left = event_time - current_time
    if time_left < datetime.datetime(2018,12,1)-datetime.datetime(2018,12,1):
        time_left = event_end - current_time
        clock(time_left, event_time, event_end, 2)
    else:
        clock(time_left, event_time, event_end, 1)

def main():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:

            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = (
            service.events()
            .list(
                calendarId="n8t99kbton3tffah1ec0jgudtia4o9sk@import.calendar.google.com",
                timeMin=now,
                maxResults=50,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        for event in events:
            if event["summary"] == "Math. - SN 5-00095":
                raw_date_data = event["start"]
                raw_date = raw_date_data['dateTime']
                raw_end_data = event["end"]
                raw_end = raw_end_data["dateTime"]
                
                event_time = datetime.datetime.fromisoformat(raw_date[:-1]).replace(microsecond=0)
                event_end = datetime.datetime.fromisoformat(raw_end[:-1]).replace(microsecond=0)
                
                update_clock(event_time, event_end)
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
    root.mainloop()