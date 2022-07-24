import os
import json

import pytz
import requests

from datetime import datetime
from dotenv import load_dotenv

# LOAD ENV VARS
load_dotenv()

X_RapidAPI_Key = os.getenv("X_RapidAPI_Key")
X_RapidAPI_Host = os.getenv("X_RapidAPI_Host")
telegram_token = os.getenv("telegram_token")
telegram_chat_ids = json.loads(os.getenv("danny_chat_ids"))

# FOOTBALL API DETAILS
football_api_url = 'https://' + X_RapidAPI_Host + '/v3/fixtures'

football_api_url_headers = {
	"X-RapidAPI-Key": X_RapidAPI_Key,
	"X-RapidAPI-Host": X_RapidAPI_Host
}

# TELEGRAM DETAILS
telegram_url = "https://api.telegram.org/bot" + telegram_token


def fetch_results():
    r = requests.request("GET", football_api_url, headers=football_api_url_headers, params={'date': datetime.today().strftime('%Y-%m-%d')})
    print('Football API response status:', r.status_code)
    return r.json()
    

def fake_fetch_results():
    with open("data/sample.json", "r") as f:
        response = f.read()
        return json.loads(response)

def find_glasgow_events(events):
    matched_events = []

    for entry in events['response']:        
        if (entry['fixture']['venue']['city']) == 'Glasgow':
            matched_events.append(entry)

    print('Number of events in Glasgow:', len(matched_events))
    return matched_events

def convert_timestamp(timestamp):
    utc_dt = datetime.fromtimestamp(timestamp)
    uk_tmz = pytz.timezone('Europe/London')

    return utc_dt.astimezone(uk_tmz).strftime("on %d/%m/%Y at %H:%M:%S")

def parse_message(event):
    return '''
    <b> Game Alert! </b>
    {homeTeam} - {awayTeam}
    {stadium}
    Kicks off {time}
    '''.format(homeTeam=event['teams']['home']['name'], awayTeam=event['teams']['away']['name'], stadium=event['fixture']['venue']['name'], time=convert_timestamp(event['fixture']['timestamp']))

def send_notifications(events):
    for event in events:

        message = parse_message(event)

        for chatId in telegram_chat_ids:
            r = requests.post(telegram_url + '/sendMessage', params={"chat_id": chatId}, json={'text': message, 'parse_mode': 'HTML'})
            print('Telegram response status:', r.status_code, "for chat ending in", str(chatId)[-3:], "- event", event['fixture']['id'])

def main():
    # events = fetch_results()
    events = fake_fetch_results()

    glasgow_events = find_glasgow_events(events)

    send_notifications(glasgow_events)

if __name__ == "__main__":  
    print("Starting run...")  
    main()
    print("Finished")  