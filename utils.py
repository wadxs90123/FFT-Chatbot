import os
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageAction,QuickReplyButton,QuickReply,VideoSendMessage,MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageCarouselColumn,CarouselTemplate, ImageCarouselTemplate, URITemplateAction, ButtonsTemplate, MessageTemplateAction, ImageSendMessage
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction

load_dotenv()

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"
def send_text_multiple_message(reply_token, textList):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, textList)
    return "OK"

def send_video_message(reply_token, videoUrl, preUrl):
    line_bot_api = LineBotApi(channel_access_token)
    message = VideoSendMessage(
        original_content_url = videoUrl,
        preview_image_url = preUrl
    )
    line_bot_api.reply_message(reply_token, message)
    return "OK"

def send_quick_reply(reply_token, text_, items_):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(
            text = text_,
            quick_reply=QuickReply(
                items=items_
            )
        )
    )
    return "OK"
                
def send_carousel_message(reply_token, col):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text = '*選單*',
        template = CarouselTemplate(columns = col)
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_button_message(reply_token, title, text, btn, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='button template',
        template = ButtonsTemplate(
            title = title,
            text = text,
            thumbnail_image_url = url,
            actions = btn
        )
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_image_message(reply_token, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"
