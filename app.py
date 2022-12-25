import os
import sys
import json 

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import PostbackAction,URIAction,CarouselColumn,MessageEvent,MessageAction, TextMessage, TextSendMessage

from fsm import TocMachine
from spider import ScratchPages
from spider import Store
from utils import send_text_message
from utils import send_carousel_message
from utils import send_button_message 
from utils import send_image_message
from utils import send_video_message

load_dotenv()

hash_map = dict()


app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

main_url = os.getenv("MAIN_WEB_URL",None)

@app.route("/callback", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    
    data = json.loads(body)

    if data['events'] ==[]:
        print("Webhook Test!")
        return "OK"
    userId = data['events'][0]['source']['userId']
    print("userid : "+userId)
    machine = hash_map.setdefault(userId,TocMachine(
            states=[
                    "user", 
                    "inputArea",
                    "inputArea2",
                    "inputArea3",
                    "inputType",
                    "inputPrice",
                    "startSearch",
                    
                    "GuessStart",
                    "Guess2",
                    "Guess3",
                    "GuessResult",

                    "PlayerStatus",
                    "PlayMenu",
                    "Advanture",
                    "Nothing",
                    "MeetMob",
                    "Combating",
                    "CombatResultWin",
                    "CombatResultLose",
                    "GetTreasure",
            ],
            transitions=[
                    {"trigger": "advance", "source": "user", "dest": "inputArea",      "conditions": "is_going_to_inputArea"},
                    {"trigger": "advance", "source": "inputArea", "dest": "inputType", "conditions": "is_going_to_inputType"},
                    
                    {"trigger": "advance", "source": "inputArea", "dest": "inputArea2", "conditions": "is_going_to_inputArea2"},
                    {"trigger": "advance", "source": "inputArea2", "dest": "inputArea", "conditions": "inputArea2_going_to_inputArea"},
                    {"trigger": "advance", "source": "inputArea2", "dest": "inputArea3", "conditions": "is_going_to_inputArea3"},
                    {"trigger": "advance", "source": "inputArea3", "dest": "inputArea2", "conditions": "inputArea3_going_to_inputArea2"},
                    
                    {"trigger": "advance", "source": "inputType", "dest": "inputArea", "conditions": "go_back_to_area"},
                    {"trigger": "advance", "source": "inputPrice", "dest": "inputType", "conditions": "go_back_to_type"},

                    {"trigger": "advance", "source": "inputType", "dest": "inputPrice", "conditions": "is_going_to_inputPrice"},
                    {"trigger": "advance", "source": "inputPrice", "dest": "startSearch", "conditions": "is_going_to_startSearch"},
                    {"trigger": "advance", "source": "startSearch", "dest": "startSearch", "conditions": "want_more"},
                    {"trigger": "advance", "source": "startSearch", "dest": "inputPrice", "conditions": "go_back_to_price"},

                    {"trigger": "advance", "source": "user", "dest": "GuessStart", "conditions": "is_going_to_GuessStart"},
                    {"trigger": "advance", "source": "GuessStart", "dest": "Guess2", "conditions": "is_going_to_Guess2"},
                    {"trigger": "advance", "source": "Guess2", "dest": "Guess3", "conditions": "is_going_to_Guess3"},
                    {"trigger": "advance", "source": "Guess3", "dest": "GuessResult", "conditions": "is_going_to_GuessResult"},
                    
                    {"trigger": "advance", "source": "Guess2", "dest": "GuessStart", "conditions": "is_back_to_GuessStart"},
                    {"trigger": "advance", "source": "Guess3", "dest": "Guess2", "conditions": "is_back_to_Guess2"},
                    {"trigger": "advance", "source": "GuessResult", "dest": "Guess3", "conditions": "is_back_to_Guess3"},
                    
                      
                    {"trigger": "advance", "source": "user", "dest": "PlayMenu", "conditions": "is_going_to_PlayMenu"},
                    {"trigger": "advance", "source": "PlayMenu", "dest": "PlayerStatus", "conditions": "is_going_to_PlayerStatus"},
                    {"trigger": "advance", "source": "PlayMenu", "dest": "Advanture", "conditions": "is_going_to_Advanture"},
                    {"trigger": "advance", "source": "Advanture", "dest": "GetTreasure", "conditions": "is_going_to_GetTreasure"},
                    
                    {"trigger": "advance", "source": "MeetMob", "dest": "Combating", "conditions": "is_going_to_Combating"},
                    {"trigger": "advance", "source": "Combating", "dest": "CombatResultWin", "conditions": "is_going_to_CombatResultWin"},
                    {"trigger": "advance", "source": "Combating", "dest": "CombatResultLose", "conditions": "is_going_to_CombatResultLose"},
                    {"trigger": "advance", "source": "Advanture", "dest": "Nothing", "conditions": "is_going_to_Nothing"},
                    {"trigger": "advance", "source": "Advanture", "dest": "MeetMob", "conditions": "is_going_to_MeetMob"},
                    
                    {"trigger": "advance", "source": "Advanture", "dest": "PlayMenu", "conditions": "is_back_to_PlayMenu"},
                    {"trigger": "advance", "source": "GetTreasure", "dest": "Advanture", "conditions": "is_back_to_Advanture"},
                    {"trigger": "advance", "source": "Nothing", "dest": "Advanture", "conditions": "is_back_to_Advanture"},
                    {"trigger": "advance", "source": "MeetMob", "dest": "Advanture", "conditions": "is_back_to_Advanture"},
                    {"trigger": "advance", "source": "PlayerStatus", "dest": "PlayMenu", "conditions": "is_back_to_PlayMenu"},
                    {"trigger": "advance", "source": "CombatResultWin", "dest": "Advanture", "conditions": "is_back_to_Advanture"},
                    {"trigger": "advance", "source": "CombatResultLose", "dest": "PlayMenu", "conditions": "is_back_to_PlayMenu"},


                    {"trigger": "self_back","source": "GuessStart", "dest":"GuessStart", "conditions":"response_false"},
                    {"trigger": "self_back","source": "inputArea", "dest":"inputArea", "conditions":"response_false"},
                    {"trigger": "self_back","source": "inputArea2", "dest":"inputArea2", "conditions":"response_false"},
                    {"trigger": "self_back","source": "inputArea3", "dest":"inputArea3", "conditions":"response_false"},
                    {"trigger": "self_back","source": "inputType", "dest":"inputType", "conditions":"response_false"},
                    {"trigger": "self_back","source": "inputPrice", "dest":"inputPrice", "conditions":"response_false"},
                    {"trigger": "self_back","source": "startSearch", "dest":"startSearch", "conditions":"response_false"},
                    {"trigger": "self_back","source": "GuessStart", "dest":"GuessStart", "conditions":"response_false"},
                    {"trigger": "self_back","source": "Guess2", "dest":"Guess2", "conditions":"response_false"},
                    {"trigger": "self_back","source": "Guess3", "dest":"Guess3", "conditions":"response_false"},
                    {"trigger": "self_back","source": "GuessResult", "dest":"GuessResult", "conditions":"response_false"},
                    {"trigger": "self_back","source": "user", "dest":"user", "conditions":"response_false"},
                    
                    {"trigger": "self_back","source": "PlayerStatus", "dest":"PlayerStatus", "conditions":"response_false"},
                    {"trigger": "self_back","source": "PlayMenu", "dest":"PlayMenu", "conditions":"response_false"},
                    {"trigger": "self_back","source": "Advanture", "dest":"Advanture", "conditions":"response_false"},
                    {"trigger": "self_back","source": "Nothing", "dest":"Nothing", "conditions":"response_false"},
                    {"trigger": "self_back","source": "MeetMob", "dest":"MeetMob", "conditions":"response_false"},
                    {"trigger": "self_back","source": "GetTreasure", "dest":"GetTreasure", "conditions":"response_false"},

                    {"trigger": "go_back", "source": ["PlayMenu","GuessStart","Guess2","Guess3","GuessResult","inputPrice","inputType","inputArea","inputArea2","inputArea3","startSearch"], "dest": "user","conditions":"is_back_to_user"},
            ],
            initial="user",
            auto_transitions=False,
            show_conditions=True,
        )
    )
    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    if events == []:
        return "OK" 


    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        # print(f"REQUEST BODY: \n{body}")

        text = event.message.text
        reply_token = event.reply_token
        response = machine.advance(event)
        print("response : " + str(response))
        if response == False:
            if event.message.text.lower().strip() == 'fsm':
                send_image_message(event.reply_token, f'{main_url}/show-fsm/{userId}')
            elif machine.state != 'user' and event.message.text=='返回主選單':
                machine.go_back(event)
            else:
                machine.self_back(event)
                
    return "OK"
import os
# os.environ['PATH'] =  os.pathsep + './Graphviz/bin/'
@app.route("/show-fsm/<userID>", methods=["GET"])
def show_fsm(userID):
    machine = hash_map.get(userID)
    # machine.get_graph().draw(f"img/{userID}.png", prog="dot", format="png")
    return send_file(f"img/fsm.png", mimetype="image/png")
@app.route("/img/<imageName>", methods=['GET'])
def getImg(imageName):
    return send_file(f"img/{imageName}", mimetype='image/png')

if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
