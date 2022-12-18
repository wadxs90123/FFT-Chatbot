from transitions.extensions import GraphMachine

import random
import requests
import re
from spider import ScratchPages
from spider import Store
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageAction,MessageEvent, TextMessage, TextSendMessage, VideoSendMessage
from linebot.models import PostbackAction,URIAction, CarouselColumn,ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from utils import send_text_message
from utils import send_text_message_AI
from utils import send_carousel_message
from utils import send_button_message 
from utils import send_image_message
from utils import send_video_message
from utils import send_text_multiple_message
from bs4 import BeautifulSoup


# searchWeb = 'list?priceLevel=2'
# mainWeb = 'https://ifoodie.tw/explore/%E5%8F%B0%E5%8D%97%E5%B8%82/%E5%AE%89%E5%8D%97%E5%8D%80/list?priceLevel=2'
# searchWeb = '{mainWeb}/XX區/list/xx餐{?priceLevel=消費模式}'
searchWeb = 'https://ifoodie.tw/explore/台南市'
inputAreaGreetingDict = ['好的, 您想在哪區吃呢?']
inputAreaDict = ['新營區','鹽水區','白河區','柳營區','後壁區','東山區','麻豆區','下營區','六甲區','官田區'
                ,'大內區','佳里區','學甲區','西港區','七股區','將軍區','北門區','新化區','新市區','善化區'
                ,'安定區','山上區','玉井區','楠西區','南化區','左鎮區','仁德區','歸仁區','關廟區','龍崎區'
                ,'永康區','東區','南區','中西區','北區','安南區','安平區']
inputTypeDict = ['早餐', '午餐', '晚餐', '宵夜']
inputArea = ""
inputType = ""
inputPrice = ""
class TocMachine(GraphMachine):
    
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
    def is_going_to_inputArea(self, event):
        reply_token = event.reply_token
        text = event.message.text
        return text.lower().strip() == 'start' 
    def on_enter_inputArea(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, '請告訴我區名, 例如: 東區')
    def is_going_to_inputType(self, event):
        global inputArea
        text = event.message.text
        reply_token = event.reply_token
        if text in inputAreaDict:
            inputArea = text   
            return True
        return False
    def on_enter_inputType(self, event):
        print('enter inputtype')
        global inputArea
        title = f'您選擇的區域是 \"{inputArea}\", 您希望用餐的時段是何時呢?'
        text = '下方點選任一時段'
        btn = [
            MessageTemplateAction(
                label = '早餐',
                text ='早餐'
            ),
            MessageTemplateAction(
                label = '午餐',
                text = '午餐'
            ),
            MessageTemplateAction(
                label = '晚餐',
                text = '晚餐'
            ),
            MessageTemplateAction(
                label = '宵夜',
                text = '宵夜'
            ),
        ]
        url = 'https://img.88icon.com/download/jpg/20200727/c4c0f97e4eeb527d1708adb8bd8ee671_512_512.jpg!88con'
        send_button_message(event.reply_token, title, text, btn, url)
    def is_going_to_inputPrice(self, event):
        global inputType
        text = event.message.text
        reply_token = event.reply_token
        if text in inputTypeDict:
            inputType = text   
            return True
        return False
    def on_enter_inputPrice(self, event):
        title = f'您選擇的區域是 \"{inputArea}\", 用餐的時段是\"{inputType}\",那預算方面如何呢?'
        text = '下方選擇您的預算'
        btn = [
            MessageTemplateAction(
                label = 'NT$150以內',
                text ='NT$150以內'
            ),
            MessageTemplateAction(
                label = 'NT$150~NT$600',
                text = 'NT$150~NT$600'
            ),
            MessageTemplateAction(
                label = 'NT$600~NT$1200',
                text = 'NT$600~NT$1200'
            ),
            MessageTemplateAction(
                label = '都可以',
                text = '都可以'
            )
        ]
        url = 'https://img.88icon.com/download/jpg/20200727/c4c0f97e4eeb527d1708adb8bd8ee671_512_512.jpg!88con'
        send_button_message(event.reply_token, title, text, btn, url)
    def is_going_to_startSearch(self, event):
        global inputPrice
        text = event.message.text
        reply_token = event.reply_token
        if text == 'NT$150以內':
            inputPrice = '1'
            return True
        elif text == 'NT$150~NT$600':
            inputPrice = '2'
            return True
        elif text == 'NT$600~NT$1200':
            inputPrice = '3'
            return True
        elif text == '都可以':
            inputPrice = '0'
            return True
        return False
    def on_enter_startSearch(self, event):
        text = event.message.text
        reply_token = event.reply_token
        print("onenter_startSearch " + text)
        foodList = ScratchPages(inputArea, inputType, inputPrice, 4)
        title = f'根據您的需求為您提供{len(foodList)}間餐廳' if len(foodList) > 0 else f'很抱歉,我找不到資料'
        col = []
        c = CarouselColumn(
            thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRiEVEBZnM-1NBig3_7tuHlH9KZVn38FUoN8Nazo_ty1y4BzaqIICnU7wGr4sEFMoLZB8A&usqp=CAU',
            title=title,
            text='請慢用~',
            actions=[
                MessageAction(
                    label='點我要其他推薦',
                    text='再給我其他的'
                ),
                MessageAction(
                    label='返回主選單',
                    text='返回主選單'
                )
            ]
        )
        col.append(c)
        print("foodList : "+str(len(foodList)))
        for i in range(len(foodList)):
            t = foodList[i]
            c = CarouselColumn(
            thumbnail_image_url= f'{t.img_src}',
            title = f'{t.name}({t.starInfo}★)',
            text=f'消費: {t.priceInfo} 營業資訊: {t.openInfo}',
            actions=[
                URIAction(
                    label='查看更多',
                    uri=f'{t.web_src}'
                ),
                PostbackAction(
                    label=f'{t.locInfo}',
                    data='action=none'
                )
            ]
            )
            col.append(c)
        send_carousel_message(reply_token, col)
    def is_back_to_user(self, event):
        print("in user")
        return event.message.text == '返回主選單'
    def want_more(self, event):
        print('want more')
        return event.message.text == '再給我其他的'
    def on_enter_user(self, event):
        text = event.message.text
        reply_token = event.reply_token
        global inputArea,inputType,inputPrice
        inputArea = ""
        inputType = ""
        inputPrice = ""
        send_text_message(reply_token, "請輸入\"start\"來開始查找食物")
    # def on_exit_state1(self):
    #     print("Leaving state1")

    # def on_exit_state2(self):
    #     print("Leaving state2")
