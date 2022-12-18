import os
import sys
import json 

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import PostbackAction,URIAction,CarouselColumn,MessageEvent,MessageAction, TextMessage, TextSendMessage

from fsm import TocMachine
from fsm import inputArea, inputType, inputPrice
from spider import ScratchPages
from spider import Store
from utils import send_text_message
from utils import send_text_message_AI
from utils import send_carousel_message
from utils import send_button_message 
from utils import send_image_message
from utils import send_video_message

load_dotenv()

hash_map = dict()

# machine = TocMachine(
    # states=[
    #     "user", 
    #     "inputArea",
    #     "inputType",
    #     "inputPrice",
    #     "startSearch"
    #     ],
    # transitions=[
    #         {"trigger": "advance", "source": "user", "dest": "inputArea",      "conditions": "is_going_to_inputArea"},
    #         {"trigger": "advance", "source": "inputArea", "dest": "inputType", "conditions": "is_going_to_inputType"},
    #         {"trigger": "advance", "source": "inputType", "dest": "inputPrice", "conditions": "is_going_to_inputPrice"},
    #         {"trigger": "advance", "source": "inputPrice", "dest": "startSearch", "conditions": "is_going_to_startSearch"},
    #         {"trigger": "advance", "source": "startSearch", "dest": "startSearch", "conditions": "want_more"},
    #         # {"trigger": "advance", "source": "startSearch", "dest": "user", "condition":"is_going_to_user_from_startSearch"},
    #         {"trigger": "go_back", "source": ["inputPrice","inputType","inputArea","startSearch"], "dest": "user","conditions":"is_back_to_user"},
    # ],
    # initial="user",
    # auto_transitions=False,
    # show_conditions=True,
# )

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

@app.route("/", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    
    data = json.loads(body)

    userId = data['events'][0]['source']['userId']
    print("userid : "+userId)
    machine = hash_map.setdefault(userId,TocMachine(
            states=[
                    "user", 
                    "inputArea",
                    "inputType",
                    "inputPrice",
                    "startSearch"
            ],
            transitions=[
                    {"trigger": "advance", "source": "user", "dest": "inputArea",      "conditions": "is_going_to_inputArea"},
                    {"trigger": "advance", "source": "inputArea", "dest": "inputType", "conditions": "is_going_to_inputType"},
                    {"trigger": "advance", "source": "inputType", "dest": "inputPrice", "conditions": "is_going_to_inputPrice"},
                    {"trigger": "advance", "source": "inputPrice", "dest": "startSearch", "conditions": "is_going_to_startSearch"},
                    {"trigger": "advance", "source": "startSearch", "dest": "startSearch", "conditions": "want_more"},
                    # {"trigger": "advance", "source": "startSearch", "dest": "user", "condition":"is_going_to_user_from_startSearch"},
                    {"trigger": "go_back", "source": ["inputPrice","inputType","inputArea","startSearch"], "dest": "user","conditions":"is_back_to_user"},
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
            if machine.state != 'user' and event.message.text=='返回主選單':
                machine.go_back(event)
            elif machine.state == 'user':
                send_text_message(reply_token, "請輸入\"start\"來開始查找食物")
            elif machine.state == 'inputArea':
                send_text_message(reply_token, "抱歉, 我找不到這個區, 請您確認好再跟我說一次(ex: 東區)")
            elif machine.state == 'inputType' or machine.state == 'inputPrice':
                send_text_message(reply_token, "抱歉, 請輸入菜單上有的選項")
                
    return "OK"
 
@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
