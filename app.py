# TODO need to limit past events to however many it is limited to on /programs: in the past year maybe?

import os
import json
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv, dotenv_values
load_dotenv()

r = requests.get('https://hackclub.com/api/v1/events') # get list of all hack club events
event_storage = open("events.json", "w") # object to be dumped into events.json
json.dump(r.json(), event_storage, indent=6) # dump r.json into event_storage (representing the json file) 
event_storage.close() # close the file

# initializes your app with your bot token and socket mode handler
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.message("hello") # listens to incoming messages that contain hello
def message_hello(message, say): # say() sends a message to the channel where the event was truggered
    say(f"Hey there <@{message['user']}>!")

# start app
if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()

