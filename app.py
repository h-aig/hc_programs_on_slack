# TODO will need to find a way to update the files every day on a schedule: cron job?

import os
import json
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv, dotenv_values
load_dotenv()

stati = ["upcoming", "ongoing", "ended"] # plural of status (this is not true)

for numbers in range(len(stati)): # for all possible stati... it will dump into three seperate files, convenient!
    payload = {'status': stati[numbers]}
    r = requests.get('https://hackclub.com/api/v1/events', params=payload) # get list of all hack club events
    event_storage = open(f"events_{stati[numbers]}.json", "w") # object to be dumped into events.json
    json.dump(r.json(), event_storage, indent=6) # dump r.json into event_storage (representing the json file) 
    event_storage.close() # close the file


# initializes your app with your bot token and socket mode handler
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.message("hello") # listens to incoming messages that contain hello
def message_hello(message, say): # say() sends a message to the channel where the event was truggered
    # create section w/ text and button
    say(
            blocks=[ 
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "action_id": "button_click"
                        }
                    }
                ],
            text=f"Hey there <@{message['user']}>!" # fallback/accessibility
            )

@app.action("button_click")
def action_button_click(body, ack, say):
    # acknowledge the action https://docs.slack.dev/tools/bolt-js/concepts/acknowledge/
    ack()
    say(f"<@{body['user']['id']}> clicked the button")

# start app
if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()

