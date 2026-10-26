import os
import json
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

r = requests.get('https://hackclub.com/api/v1/events') # get list of all hack club events
event_storage = open("events.json", "w") # object to be dumped into events.json
json.dump(r.json(), event_storage, indent=6) # dump r.json into event_storage (representing the json file) 
event_storage.close() # close the file

# initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# start app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
