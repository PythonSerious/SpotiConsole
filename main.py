# SPOTICONSOLE
# Version: 1.0.1
# Author: python#0001 https://github.com/pythonserious
import json
import sys
import os
import time
import threading

os.system("cls")

try:
    import requests
    import termcolor
except ImportError:
    os.system(f"{sys.executable} -m pip install requests")
    import requests

    os.system(f"{sys.executable} -m pip install termcolor")
    import termcolor

    os.system("cls")
    termcolor.cprint("INSTALLED MODULES. RELAUNCHING...", "green")
    time.sleep(2)
    os.system("cls")


def get_new_token(config):
    print("In order to use this program properly, you need to generate an oauth token from spotify.\n"
          "Obtain a token here: https://developer.spotify.com/console/get-several-tracks/"
          "\nSet the following scopes in the token generator: user-read-playback-state, "
          "user-modify-playback-state, user-read-currently-playing, user-modify-playback-state"
          "\n\n")
    token = input(termcolor.colored("Enter your token here: ", "green"))
    config["token"] = token
    with open("config.json", "w") as config_raw:
        json.dump(config, config_raw)
        termcolor.cprint("TOKEN SAVED, LOADING...", "green")
        time.sleep(2)
        os.system("cls")


with open("config.json", "r") as config_raw:
    config = json.load(config_raw)
    if config["token"] == "":
        termcolor.cprint("NO TOKEN FOUND", "red")
        get_new_token(config)

    else:
        check_response = requests.get("https://api.spotify.com/v1/me/player", headers={
            "Authorization": f"Bearer {config['token']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        if check_response.status_code == 401:
            termcolor.cprint("INVALID TOKEN", "red")
            get_new_token(config)

token = config["token"]


def request_builder(method, url):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.request(method, url, headers=headers)
    if response.status_code == 204:
        termcolor.cprint("Nothings playing :)", "yellow")
        return response
    if response.status_code != 200:
        termcolor.cprint(f"REQUEST ERROR: CODE {response.status_code}", "red")
        print(response.text)

    return response


current_track = ()

repeat = False
shuffle = False
current_song = None
device = None
playback = False
volume = 0


def get_generals():
    global repeat
    global shuffle
    global volume
    global playback
    response = request_builder("GET", "https://api.spotify.com/v1/me/player")
    if response.status_code == 200:
        response = response.json()
        repeat = response["repeat_state"]
        shuffle = response["shuffle_state"]
        volume = response["device"]["volume_percent"]
        playback = response["is_playing"]


def get_device():
    global device
    response = request_builder("GET", "https://api.spotify.com/v1/me/player/devices")
    if response.status_code == 200:
        response = response.json()
        device = response["devices"][0]["name"]


def get_current_track():
    global current_track
    response = request_builder("GET", "https://api.spotify.com/v1/me/player/currently-playing")
    if response.status_code == 200:
        response = response.json()
        track = response["item"]["name"]
        artist = response["item"]["artists"][0]["name"]
        progress = response["progress_ms"]
        duration = response["item"]["duration_ms"]
        progress = progress / duration
        current_track = track, artist, progress, duration, response["progress_ms"]
    else:
        current_track = "NO TRACK", "NO ARTIST", 0, 0, 0


def update_console():
    get_generals()
    get_device()
    get_current_track()
    global current_track
    global repeat
    global shuffle
    global volume
    global device
    global playback

    track, artist, progress, progress_ms, duration = current_track

    progress_ms = progress_ms / 1000
    duration = duration / 1000
    progress_ms = int(progress_ms)
    duration = int(duration)
    progress_ms = time.strftime("%M:%S", time.gmtime(progress_ms))
    duration = time.strftime("%M:%S", time.gmtime(duration))
    final = f"{progress_ms} / {duration}"

    progress_bar = ""
    for i in range(0, 30):
        if i <= progress * 30:
            progress_bar += "█"
        else:
            progress_bar += "░"

    response = ""
    if playback:
        playback = "▶"
    else:
        playback = "⏸"
    if shuffle:
        shuffle = "🔀"
    else:
        shuffle = "🔁"
    if repeat == "track":
        repeat = "🔂"
    elif repeat == "context":
        repeat = "🔁"
    else:
        repeat = "🔁"
    if track is None:
        response += f"{termcolor.colored('SPOTICONSOLE', 'green')} | {termcolor.colored('NO TRACK', 'red')}\n"
    else:
        track_resp = termcolor.colored(f"{track} - {artist}", "cyan")
        response += f"{track_resp}\n{termcolor.colored(progress_bar + '   ' + final, 'cyan')}\n" \
                    f"{termcolor.colored(f'{device} | {volume}% | {shuffle} | {repeat} | {playback}', 'green')}\n\n" \
                    f"{termcolor.colored('S Pause | P Resume | N Next | B Back | E Exit', 'magenta')}"
    return response


def keyPressLoop():
    while True:
        user_action = input("")
        if user_action.lower() == "e":
            os.system("cls")
            termcolor.cprint("EXITING...", "red")
            os._exit(0)
        elif user_action.lower() == "p":
            request_builder("PUT", "https://api.spotify.com/v1/me/player/play")
        elif user_action.lower() == "s":
            request_builder("PUT", "https://api.spotify.com/v1/me/player/pause")
        elif user_action.lower() == "n":
            request_builder("POST", "https://api.spotify.com/v1/me/player/next")
        elif user_action.lower() == "b":
            request_builder("POST", "https://api.spotify.com/v1/me/player/previous")


threading.Thread(target=keyPressLoop).start()


def window_handler():
    new = ""
    while True:
        if new == "":
            os.system("cls")
        print(new)
        try:
            new = update_console()
        except:
            new = ""
            continue
        os.system("cls")


os.system("mode con: cols=50 lines=5")

# launch window handler
if __name__ == "__main__":
    window_handler()
