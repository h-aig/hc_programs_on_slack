# TODO will need to find a way to update the files every day on a schedule: cron job?
 #TODO LITERALLY THE SAME AS ABOVE? MAYBE JUST CHECK IF ALL FILES ARE THERE ^^ #TODO make sure all the meta stuff is there, and by all i mean literally just how many of each is running. eg if only ongoing (selected) is default it says 53 programs, if ongoing and upcoming it says 54 programs; 53 ongoing, 1 upcoming etc.
# check exceptfileexistseorror   

# TODO ADD FILE NUKING EVERY TIME THIS IS RUN BECAUSE I'M LAZY AND CBA WITH PARTIAL UPDATES? MIGHT NEED TO USE ID TO DETECT RATHER THAN SLUG
# TODO STICK ALL THE FILE GRABBING AND WHATNOT IN HERE
# TODO FIGURE OUT HOW TO HANDLE MOVING FROM ONGOING -> ENDED FOR EXAMPLE. OR JUST BE LAZY AND REGRAB EVERYTHING EVERY TIME. I DON'T CARE.

import os
import json
import urllib.request
import requests
import shutil
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv, dotenv_values
load_dotenv()

stati = ["upcoming", "ongoing", "ended"] # plural of status (this is not true)
shutil.rmtree("upcoming")
shutil.rmtree("ongoing")
shutil.rmtree("ended")

os.mkdir("upcoming")
os.mkdir("ongoing")
os.mkdir("ended")

def downloadItem(directory, event, item, type):
    if item is not None:
            picture_name = str(f"{directory}/{event}_{type}.webp")
            urllib.request.urlretrieve(item, picture_name) # save as event-background.png or whatever
    else:
        link_path = os.path.join(f'{directory}', f'{event}_{type}.webp') # build path where symlink will live
        target_path = os.path.relpath(f'{type}_fallback.webp', start=f'{directory}') # calculate correct path to fallback image
        try:
            os.symlink(target_path, link_path)
        except FileExistsError:
            pass

for numbers in range(len(stati)): # for all possible stati... it will dump into three seperate files, convenient!
    payload = {'status': stati[numbers]}
    r = requests.get('https://hackclub.com/api/v1/events', params=payload) # get list of all hack club events
    event_storage = open(f"events_{stati[numbers]}.json", "w") # object to be dumped into events.json
    json.dump(r.json(), event_storage, indent=6) # dump r.json into event_storage (representing the json file) 
    
    data = json.loads(r.text) # convert json data to python object
    
    for item in data["data"]:
        directory = f"{stati[numbers]}/{item['slug']}"
        try:
            os.mkdir(directory)# make folder for each event to hold pictures and whatnot
        except FileExistsError:
            pass
        finally: 
            downloadItem(directory, item['slug'], item['logoUrl'], "logo")
            try:
                image_url = item.get('background', {}.get('imageUrl'))
                if image_url:
                    downloadItem(directory, item['slug'], item['background']['imageUrl'], "background")
                else:
                    link_path = os.path.join(f'{directory}', f'{item['slug']}_background.webp')
                    target_path = os.path.relpath(f'background_fallback.webp', start=f'{directory}')
                    try:
                        os.symlink(target_path, link_path)
                    except FileExistsError:
                        pass
            except KeyError:
                os.symlink('background_fallback.webp', f'{directory}/{item['slug']}_background.webp')
            print(f"{item['slug']} ({stati[numbers]}) resource download, completed!")
        
    event_storage.close() # close the file


# initializes your app with your bot token and socket mode handler
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# the below example material is commented out for informative purposes
#@app.message("hello") # listens to incoming messages that contain hello
#def message_hello(message, say): # say() sends a message to the channel where the event was truggered
#    # create section w/ text and button
#    say(
#            blocks=[ 
#                {
#                    "type": "section",
#                    "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
#                    "accessory": {
#                        "type": "button",
#                        "text": {"type": "plain_text", "text": "Click Me"},
#                        "action_id": "button_click"
#                        }
#                    }
#                ],
#            text=f"Hey there <@{message['user']}>!" # fallback/accessibility
#            )
#
#@app.action("button_click")
#def action_button_click(body, ack, say):
#    # acknowledge the action https://docs.slack.dev/tools/bolt-js/concepts/acknowledge/
#    ack()
#    say(f"<@{body['user']['id']}> clicked the button")

# start app



if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()

