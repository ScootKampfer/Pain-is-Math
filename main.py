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
CLASSES = {"anglais":"Anglais enr. 5-00093", "français":"Français 5-00051", "math":"Math. - SN 5-00095", "mco":None, "programmation":"Programmation 5-00091", "chimie":"Chimie-00094", "physique":"Physique-00051", "éducation Physique":"Éduc. phys. 5-00051", "arts plastiques":"Arts plast. 5-00090", "paa":"PAA005-00051"}

root = Tk()
root.title("Décompte")

creds = None
class_id1 = None
class_id2 = None
class_id3 = None

lbl = Label(root, font=('calibri', 40, 'bold'),
            background='white',
            foreground='black')

lbl.pack(anchor='center')

def clock(time_left, event_time, event_end, status, class_chosen, events):
    if status == 1:
        lbl.config(text=str(f"Temps restant avant {class_chosen}: {time_left}"))
    elif status == 2:
        lbl.config(text=str(f"Il reste {int(time_left.total_seconds())} secondes avant la fin du cours de {class_chosen}"))
    lbl.after(1000, lambda: update_clock(event_time, event_end, class_chosen, events))

def update_clock(event_time, event_end, class_chosen, events):
    current_time = datetime.datetime.utcnow().replace(microsecond=0)
    time_left = event_time - current_time
    if time_left < datetime.datetime(2018,12,1)-datetime.datetime(2018,12,1):
        time_left = event_end - current_time
        if time_left < datetime.datetime(2018,12,1)-datetime.datetime(2018,12,1):
            check_events()
        else:
            clock(time_left, event_time, event_end, 2, class_chosen, events)
    else:
        clock(time_left, event_time, event_end, 1, class_chosen, events)

def check_events():

    global event_time
    global event_end
    for event in events:
            if event["summary"] == class_id1 or event["summary"] == class_id2 or event["summary"] == class_id3:
                index_to_del = events.index(event)
                del events[0:index_to_del]
                raw_date_data = event["start"]
                raw_date = raw_date_data['dateTime']
                raw_end_data = event["end"]
                raw_end = raw_end_data["dateTime"]
                
                event_time = datetime.datetime.fromisoformat(raw_date[:-1]).replace(microsecond=0)
                event_end = datetime.datetime.fromisoformat(raw_end[:-1]).replace(microsecond=0)
                
                update_clock(event_time, event_end, class_chosen, events)
                break

def main():

    global class_chosen
    global events
    global class_id1
    global class_id2
    global class_id3
    class_chosen = None
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

        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId="n8t99kbton3tffah1ec0jgudtia4o9sk@import.calendar.google.com",
                timeMin=now,
                maxResults=1000,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("Aucun évènement trouvé!")
            return
        
        while class_chosen not in CLASSES:
            
            class_chosen = input("Nom de la classe que tu souffres dedans: ").lower()

        root.title(f"Décompte {class_chosen}")
        
        if class_chosen == "MCO":
            class_id1 = "Cult/cit. Qc 5-00051"
            class_id2 = "Éduc. finan. 5-00051"
            class_id3 = "Monde contem. 5-00051"
            
        else:
            class_id1 = CLASSES[class_chosen]
            class_id2 = "Professional edging class-00097"
            class_id3 = "How to be a good banker-00012"

        check_events()
            
    except HttpError as error:
        print(f"Erreur: {error}")

if __name__ == "__main__":
    main()
    root.mainloop()