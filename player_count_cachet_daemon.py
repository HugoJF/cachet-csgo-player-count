import valve.source
import valve.source.a2s
import valve.rcon
import time
import sys
import json
import os
import requests
import sentry_sdk
from urllib.request import urlopen
from dotenv import load_dotenv

# DotEnv loading
print('Loading env file...')
load_dotenv()

# Global variables
servers = []
last_update = 0

# DotEnv stuff
url = os.getenv('URL') + '/api/v1'
update_interval = int(os.getenv('UPDATE_INTERVAL'))
ip = os.getenv('IP')
metric_id = os.getenv('METRIC_ID')
api_key = os.getenv('API_KEY')
interval = os.getenv('INTERVAL')

# Cache
steam_api = 'http://api.steampowered.com/ISteamApps/GetServersAtAddress/v1/'
headers = {
    'X-Cachet-Token': api_key
}

# Sentry
sentry_sdk.init("https://56f764802db84f63a5b18351cd2973c0@sentry.io/1377393")

def update_server_list() -> None:
    # Clear server objects
    servers.clear()

    # Request from SteamAPI
    html = requests.get('{0}?addr={1}'.format(steam_api, ip))

    # Decode response to JSON
    res = json.loads(html.text)
    print('Response received from Steam')

    # Point to servers array
    servers_raw = res['response']['servers']

    # Build server tuples
    for sv in servers_raw:
        servers.append(tuple((ip, int(sv['gameport']))))

    # Debug
    print('Running on IP: {0} with {1} servers'.format(ip, len(servers)))
    sys.stdout.flush()


def check_for_update():
    global last_update

    d = time.time() - last_update

    if d > update_interval:
        last_update = time.time()
        update_server_list()
    else:
        print('{0} seconds remaining for update'.format(update_interval - int(d)))


while True:
    print()
    check_for_update()

    total_players = 0
    failed = False
    for sv in servers:
        try:
            with valve.source.a2s.ServerQuerier(sv) as query:
                info = query.info()
                pcount = int(info['player_count']) - int(info['bot_count'])
                total_players += pcount

        except valve.source.NoResponseError:
            failed = True

    # Build data to POST to Cachet
    print('Current players: {0}'.format(total_players))
    data = {
        'value': total_players,
        'timestamp': int(time.time()),
    }

    # Check if any server failed to respond
    if not failed:
        res = requests.post(url + '/metrics/{0}/points'.format(metric_id), data=data, headers=headers)
        print('Status code for POST: {0}'.format(res.status_code))
    else:
        print('Skipping post request')
    sys.stdout.flush()

    # Sleep
    time.sleep(int(interval))
