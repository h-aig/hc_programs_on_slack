# TODO move these todos to linear
# TODO move into carousels to look nice. each can contain 10 cards, before you would need a new one. see carouselpayload.json
# TODO DELETE non-tiled images once done with pillows centering
# TODO will need to find a way to update the files every day on a schedule: cron job?
 #TODO LITERALLY THE SAME AS ABOVE? MAYBE JUST CHECK IF ALL FILES ARE THERE ^^ #TODO make sure all the meta stuff is there, and by all i mean literally just how many of each is running. eg if only ongoing (selected) is default it says 53 programs, if ongoing and upcoming it says 54 programs; 53 ongoing, 1 upcoming etc.
# check exceptfileexistseorror   

# TODO ADD FILE NUKING EVERY TIME THIS IS RUN BECAUSE I'M LAZY AND CBA WITH PARTIAL UPDATES? MIGHT NEED TO USE ID TO DETECT RATHER THAN SLUG
# TODO STICK ALL THE FILE GRABBING AND WHATNOT IN HERE
# TODO FIGURE OUT HOW TO HANDLE MOVING FROM ONGOING -> ENDED FOR EXAMPLE. OR JUST BE LAZY AND REGRAB EVERYTHING EVERY TIME. I DON'T CARE.
# TODO judge if i need the import error from pillow (probs not as it's a subclass of oserror)
# TODO make button colour reactive to the primary logo color-- just analyse with pillow then change
# TODO filters and search at top, pinned items go at the top (limit to 1?) then rest in carousel. check different types of searches-- can i store all events?
# TODO ability to dismiss any pinned items and hide under a menu
# TODO add ability to favorite events with a button and add to another carousel at the top.
# TODO pinned item at the top with width-spanning banner
# TODO only render selected events
# TODO implement everything from the page itself
# TODO have i said refactor?
# TODO at first just load ongoing
# TODO numbers makes no sense in the for loop
import os
import json
import urllib.request
import requests
import shutil
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from PIL import Image, ImageOps, UnidentifiedImageError
from dotenv import load_dotenv, dotenv_values
load_dotenv()

stati = ["upcoming", "ongoing", "ended"] # plural of status (this is not true)
shutil.rmtree("upcoming")
shutil.rmtree("ongoing")
shutil.rmtree("ended")

os.mkdir("upcoming")
os.mkdir("ongoing")
os.mkdir("ended")

os.remove("blocks.json")
with open("blocks.json", "w") as f: pass # create file and close when done

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

for numbers in range(len(stati)): # for all possible stati... it will dump into three seperate folders, convenient!
    payload = {'status': stati[numbers]}
    r = requests.get('https://hackclub.com/api/v1/events', params=payload) # get list of all hack club events
    event_storage = open(f"events_{stati[numbers]}.json", "w") # object to be dumped into events.json
    json.dump(r.json(), event_storage, indent=6) # dump r.json into event_storage (representing the json file) 
    
    data = json.loads(r.text) # convert json data to python object
    
    # for each EVENT within a given stati (eg. for all upcoming events, then for all oncoming events... etc...)
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
        
        try:
            tile_background = Image.open(f'{directory}/{item['slug']}_background.webp').convert("RGBA") # open image (background), .convert("RGBA") preserves transparrency
            tile_logo = Image.open(f'{directory}/{item['slug']}_logo.webp').convert("RGBA") # open image (logo)
            tile = tile_background.copy()
        
            logo_max_width = int(tile_background.width * 0.5) # logo can't be more than 50% of background 
            logo_max_height = int(tile_background.height * 0.5) 
            tile_logo = ImageOps.contain(tile_logo, (logo_max_width, logo_max_height)) # resize according to above

            x = (tile_background.width - tile_logo.width) // 2 # prepare to center logo horizontally
            y = (tile_background.height - tile_logo.height) // 2 # prepare to center logo horizontally
    
            tile.paste(tile_logo, (x, y), tile_logo) # paste logo on background, centered. adding ,tile_logo uses it as the transparrency mask to keep it transparrent.
            tile.save(f'{directory}/{item['slug']}_tile.webp')
        except (UnidentifiedImageError, OSError):
            os.symlink('tile_fallback.webp', f'{directory}/{item['slug']}_tile.webp')
        finally:
            print(f"{item['slug']} ({stati[numbers]}) resource download, completed!")
    
    if numbers == 2: # TODO this is embarrassingly inefficient
        with open("blocks.json", "a") as f:
            l = '''{
            "type": "card",
            "block_id": "EVENT",
            "title": {
            "type": "mrkdwn",
            "text": "EVENT",
            "verbatim": false
            },
            "subtitle": {
            "type": "mrkdwn",
            "text": "Ends END_DATE"
            "verbatim": false
            },
            "hero_image": {
            "type": "image",
            "image_url": "IMAGE_URL",
            "alt_text": "EVENT logo"
            },
            "body": {
            "type": "mrkdwn",
            "text": "DESCRIPTION",
            "verbatim": false
            },
            "actions": [
            {
            "type": "button",
            "text": {
            "type": "plain_text",
            "text": "Go To Channel",
            "emoji": false
            },
            "action_id": "ID",
            "url": "SLACK_URL"
            },
            {
            "type": "button",
            "text": {
            "type": "plain_text",
           "text": "Start Now",
            "emoji": false
            },
            "style": "primary",
            "action_id": "SECONDID",
            "url": "WEBSITE_URL"
            }
            ]
            }'''

            l = l.replace("EVENT", item["slug"])
            l = l.replace("END_DATE", item["endDate"])
            l = l.replace("IMAGE_URL", item["slug"]) # TODO
            l = l.replace("DESCRIPTION", item["description"])
            l = l.replace("SLACK_URL", item["slackUrl"])
            l = l.replace("SECONDID", item["slug"]) # TODO
            l = l.replace("WEBSITE_URL", item["url"])

            finished = l + ","
            f.write(finished)


            


    event_storage.close() # close the file



# initializes your app with your bot token and socket mode handler
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()


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
