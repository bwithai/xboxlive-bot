import asyncio
import sys
import json
import uuid
import requests
from datetime import datetime, timedelta

# 2535441904861027

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
        scheduled_times.append(now)
        now += timedelta(hours=.25)

    # Prompt the user to select a scheduled time
    print("Please choose a scheduled time from the following options:")
    for i, time in enumerate(scheduled_times):
        print(f"{i + 1}: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    scheduled_time = scheduled_times[int(input("Enter your choice: ")) - 1].strftime('%Y-%m-%dT%H:%M:%SZ')

    print("Please choose a game from the following options:")
    for i, (game_name, game_id) in enumerate(games):
        print(f"{i + 1}. {game_name}")
    game_index = int(input("Enter the index of your choice: ")) - 1
    gameId = games[game_index][1]

    session_id = str(uuid.uuid4())
    "xuid" == xuid,
    print(f"Session ID: {session_id}")

    game_name = games[game_index][0]
    with open(f'Games/{game_name}.txt', 'w') as f:
        f.write(f'Game_id="{gameId}"\n')
        f.write(f'Session_id="{session_id}"\n')
        f.write(f'Authorization="{auth}"\n')

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
    resp = requests.post(
        'https://sessiondirectory.xboxlive.com/handles/query?include=activityInfo,relatedInfo,roleInfo',
        headers=headers, data=json.dumps(payload))
    print(f"First API Request Status Code: {resp.status_code}")

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
                        "connection": "a776a20e-1f89-49e0-a764-57ee7e54b37f",
                        "subscription": {
                            "id": "c2a1e6a8-97c6-4f1a-b841-b7e23d35207a"
                        }
                    }
                }
            }
        },
        "roleTypes": {
            "lfg": {
                "ownerManaged": True,
                "roles": {
                    "confirmed": {
                        "target": 1
                    }
                }
            }
        }
    }
    resp2 = requests.put(
        f'https://sessiondirectory.xboxlive.com/serviceconfigs/{gameId}/sessiontemplates/global(lfg)/sessions/{session_id}',
        headers=headers, data=json.dumps(payload2))
    print(f"Second API Request Response: {resp2.content}")

    payload3 = {
        "version": 1,
        "type": "search",
        "sessionRef": {
            "scid": gameId,
            "templateName": "global(lfg)",
            "name": session_id
        },
        "searchAttributes": {
            "tags": ["DISCORDthefixerdude", "WEBSITEthefixerdudeCOM", "RealRecognizeReal"],
            "achievementIds": [],
            "locale": "en"
        }
    }
    resp3 = requests.post('https://sessiondirectory.xboxlive.com/handles?include=activityInfo,relatedInfo,roleInfo',
                          headers=headers, data=json.dumps(payload3))
    print(f"Third API Request Response: {resp3.content}")


asyncio.run(async_main())
