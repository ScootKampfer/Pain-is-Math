import datetime
import os.path
import os
from tkinter import *
from tkinter.ttk import *
import subprocess as sp

if os.path.exists("api-install.json"):
    print("Toutes les librairies sont installées")
else:
    sp.run("pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    with open("api-install.json", "w") as contri:
        contri.write("It's a-ok!")

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CLASSES = {"anglais":"AE5536-93", "français":"FRA506-51", "math":"MSN506-95", "mco":"MEDEC5-51", "programmation":"PRO544-91", "chimie":"CHI504-94", "physique":"PHY504-51", "éducation physique":"EDP502-51", "arts":"ART502-90", "paa":"PAA", "next":"next"}

root = Tk()
root.title("Décompte")

creds = None
class_id = None 
class_chosen = None
good_classes = []
index = 0
mode = 0

lbl = Label(root, font=('calibri', 40, 'bold'), background='white', foreground='black')
lbl.pack(anchor='center')

def clock(status):

    global event_time, event_end, class_chosen, events, time_left, mode

    if status == 1:
        lbl.config(text=str(f"Temps restant avant {class_chosen}: {time_left}"))
    elif status == 2:
        lbl.config(text=str(f"Il reste {int(time_left.total_seconds())} secondes avant la fin du cours de {class_chosen}"))
    lbl.after(1000, lambda: update_clock())

def update_clock():

    global event_time, event_end, class_chosen, events, time_left

    current_time = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    time_left = event_time - current_time

    if time_left < datetime.datetime(2018,12,1)-datetime.datetime(2018,12,1):
        time_left = event_end - current_time

        if time_left < datetime.datetime(2018,12,1)-datetime.datetime(2018,12,1):

            check_events()
            current_time = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
            time_left = event_time - current_time
            clock(1)
        else:
            clock(2)
    else:
        clock(1)

def check_events():

    global event_time, event_end, index, class_chosen

    next_class = good_classes[index]
    index += 1
    raw_date_data = next_class["start"]
    raw_date = raw_date_data['dateTime']
    raw_end_data = next_class["end"]
    raw_end = raw_end_data["dateTime"]
    
    if mode == 1:

        class_id = next_class["summary"]
        for class1 in CLASSES:
            if CLASSES[class1] == class_id:
                class_chosen = class1
            root.title(f"Décompte {class_chosen}")
    
    event_time = datetime.datetime.fromisoformat(raw_date).replace(microsecond=0)
    event_end = datetime.datetime.fromisoformat(raw_end).replace(microsecond=0)


def main():

    global class_chosen, events, event_time, event_end, creds, good_classes, mode

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
        
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "") + "Z"
        events_result = (service.events().list(calendarId="5577cff39e8fcdd31c49d99756dff9c5e069db949b55dfc5e0d4d4ce29265c06@group.calendar.google.com", timeMin=now, maxResults=100, singleEvents=True, orderBy="startTime").execute())
        events = events_result.get("items", [])

        if not events:

            print("Aucun évènement trouvé!")
            return
        
        while class_chosen not in CLASSES:
            
            class_chosen = input("Nom de la classe que tu souffres dedans: ").lower()

        root.title(f"Décompte {class_chosen}")

        if class_chosen == "next":

            good_classes = events
            mode = 1
            next_event = events[0]
            class_id = next_event["summary"]
            for class1 in CLASSES:
                if CLASSES[class1] == class_id:
                    class_chosen = class1
            if class1 not in CLASSES:
                class_chosen = "surprise!"
        
        else:

            class_id = CLASSES[class_chosen]

            for event in events:

                if event["summary"] == class_id:

                    good_classes.append(event)
        
        root.title(f"Décompte {class_chosen}")
        check_events()
        update_clock()
            
    except HttpError as error:

        print(f"Erreur: {error}")

if __name__ == "__main__":

    main()
    root.mainloop()