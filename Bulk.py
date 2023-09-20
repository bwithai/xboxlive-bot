import asyncio
import sys
import json
import uuid
import requests
from datetime import datetime, timedelta

with open('auth.txt', 'r') as f:
    auth = f.read().strip()

with open('xuid.txt', 'r') as f:
    xuid = f.read().strip()

with open('descriptions.json', 'r') as f:
    data = json.load(f)
    descriptions = {k: v for k, v in data.items() if k != "__comment__"}

async def async_main():
    # Read the games from the Games.txt file
    games = []
    with open('Games.txt', 'r') as f:
        for line in f:
            game_name, game_id = line.strip().split(',')
            games.append((game_name, game_id))

    # Generate a list of scheduled times at the start of every hour, quarter hour, half hour, and three quarters of an hour from the current time until the end of the day
    now = datetime.now()
    now = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    end_of_day = now.replace(hour=23, minute=59, second=59)
    scheduled_times = []
    while now < end_of_day:
        scheduled_times.append(now.strftime('%Y-%m-%dT%H:%M:%SZ'))
        now += timedelta(hours=.25)

    session_ids = []

    # Loop over the list of games
    for game_index, (game_name, game_id) in enumerate(games):
        scheduled_time_index = game_index % len(scheduled_times)
        
        gameId = games[game_index][1]
        scheduled_time = scheduled_times[scheduled_time_index]
        
        session_id = str(uuid.uuid4())
        session_ids.append(session_id)
        
        print(f'Game: {game_name}')
        print(session_id)
        print(f'Scheduled Time: {scheduled_time}')
        
        
        with open(f'games/{game_name}.txt', 'w') as f:
            f.write(f'Game_id="{gameId}"\n')
            f.write(f'Session_id="{session_id}"\n')
            f.write(f'Authorization="{auth}"\n')
            f.write(f'XUID="{xuid}"\n')
            
        
        
        headers = {
            "x-xbl-contract-version": "107",
            "Accept": "application/json",
            "Accept-Language": "en-US, en",
            "Authorization": auth,
        }
        
        payload = {
            "communicatePermissionRequired": True,
            "includeScheduled": True,
            "type": "search",
            "filter": "tolower(session / templateName) eq 'global(lfg)' or (tolower(session/templateName) eq 'teamlfg' and tolower(session/scid) eq '7492baca-c1b4-440d-a391-b7ef364a8d40')",
            "sessionOwners": xuid,
            "orderBy": "suggestedLfg desc",
            "followed": False
        }
        resp = requests.post('https://sessiondirectory.xboxlive.com/handles/query?include=activityInfo,relatedInfo,roleInfo', headers=headers, data=json.dumps(payload))
        print(resp.status_code)
        
       
        
        payload2 = {
            "properties": {
                "system": {
                    "joinRestriction": "followed",
                    "readRestriction": "followed",
                    "description": {
                        "text": descriptions[gameId],
                        "locale": "en"
                    },
                    "scheduledTime": scheduled_time,
                    "searchHandleVisibility": "xboxlive"
                }
            },
            "members": {
                "me": {
                    "constants": {
                        "system": {
                            "initialize": True,
                            "xuid": xuid,
                        }
                    },
                    "properties": {
                        "system": {
                            "active": True,
                            "connection":"a776a20e-1f89-49e0-a764-57ee7e54b37f",
                            "subscription":{
                                "id":"c2a1e6a8-97c6-4f1a-b841-b7e23d35207a"
                            }
                        }
                    }
                }
            },
            "roleTypes":{
                "lfg":{
                    "ownerManaged":True,
                    "roles":{
                        "confirmed":{
                            "target":1
                        }
                    }
                }
            }
        }
        
        resp2 = requests.put(f'https://sessiondirectory.xboxlive.com/serviceconfigs/{gameId}/sessiontemplates/global(lfg)/sessions/{session_id}', headers=headers, data=json.dumps(payload2))
        
        print(resp2.content)
        
        payload3 = {
            "version": 1,
            "type":"search",
            "sessionRef":{
                "scid":gameId,
                "templateName":"global(lfg)",
                "name":session_id
            },
            "searchAttributes":{
                "tags":["DISCORDthefixerdude","WEBSITEthefixerdudeCOM","RealRecognizeReal"],
                "achievementIds":[],
                "locale":"en"
            }
        }
        
        resp3 = requests.post('https://sessiondirectory.xboxlive.com/handles?include=activityInfo,relatedInfo,roleInfo', headers=headers, data=json.dumps(payload3))
        
        print(resp3.content)
        
      
        

asyncio.run(async_main())

