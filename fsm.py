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
from utils import send_carousel_message
from utils import send_button_message 
from utils import send_image_message
from utils import send_video_message
from utils import send_text_multiple_message
from bs4 import BeautifulSoup

import os
main_url = os.getenv("MAIN_WEB_URL",None)

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
        return text == '我想找吃的' 
    def is_going_to_inputArea2(self, event):
        reply_token = event.reply_token
        text = event.message.text
        return text == '其他區域' 
    def on_enter_inputArea2(self, event):
        reply_token = event.reply_token
        title = '請點選您要查找的區名~'
        col = []
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/1.png',
            title=title,
            text='其他功能',
            actions=[
                PostbackAction(
                    label=f'目前:區域(2/3)',
                    data='action=none'    
                ),MessageAction(
                    label=f'返回區域(1/3)',
                    text =f'返回區域(1/3)'
                ),MessageAction(
                    label=f'其他區域',
                    text =f'其他區域'           
                )
            ]
        ))
        for i in range(4):
            action = []
            for j in range(3):
                action.append(MessageAction(
                    label=f'{inputAreaDict[12+i*3+j]}',
                    text =f'{inputAreaDict[12+i*3+j]}'   
                ))    
            col.append(CarouselColumn(
                thumbnail_image_url=f'{main_url}/img/1.png',
                title=title,
                text='請點選任一區',
                actions=action
            ))
        send_carousel_message(reply_token, col)
    def inputArea2_going_to_inputArea(self, event):
        reply_token = event.reply_token
        text = event.message.text
        return text == '返回區域(1/3)'
    def inputArea3_going_to_inputArea2(self, event):
        reply_token = event.reply_token
        text = event.message.text
        return text == '返回區域(2/3)'
    def is_going_to_inputArea3(self, event):
        reply_token = event.reply_token
        text = event.message.text
        return text == '其他區域' 
    def on_enter_inputArea3(self, event):
        reply_token = event.reply_token
        title = '請點選您要查找的區名~'
        col = []
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/1.png',
            title=title,
            text='其他功能',
            actions=[
                PostbackAction(
                    label=f'目前:區域(3/3)',
                    data='action=none'    
                ),MessageAction(
                    label=f'返回區域(2/3)',
                    text =f'返回區域(2/3)'
                ),MessageAction(
                    label=f'{inputAreaDict[24]}',
                    text =f'{inputAreaDict[24]}'           
                )
            ]
        ))
        for i in range(4):
            action = []
            for j in range(3):
                action.append(MessageAction(
                    label=f'{inputAreaDict[25+i*3+j]}',
                    text =f'{inputAreaDict[25+i*3+j]}'   
                ))    
            col.append(CarouselColumn(
                thumbnail_image_url=f'{main_url}/img/1.png',
                title=title,
                text='請點選任一區',
                actions=action
            ))
        send_carousel_message(reply_token, col)
    def on_enter_inputArea(self, event):
        reply_token = event.reply_token
        title = '請點選您要查找的區名~'
        col = []
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/1.png',
            title=title,
            text='其他功能',
            actions=[
                PostbackAction(
                    label=f'目前:區域(1/3)',
                    data='action=none'    
                ),MessageAction(
                    label=f'其他區域',
                    text =f'其他區域'
                ),MessageAction(
                    label=f'返回主選單',
                    text =f'返回主選單'           
                )
            ]
        ))
        for i in range(4):
            action = []
            for j in range(3):
                action.append(MessageAction(
                    label=f'{inputAreaDict[i*3+j]}',
                    text =f'{inputAreaDict[i*3+j]}'   
                ))    
            col.append(CarouselColumn(
                thumbnail_image_url=f'{main_url}/img/1.png',
                title=title,
                text='請點選任一區',
                actions=action
            ))
        send_carousel_message(reply_token, col)
    def is_going_to_inputType(self, event):
        global inputArea
        text = event.message.text
        reply_token = event.reply_token
        if text in inputAreaDict:
            inputArea = text   
            return True
        return False
    def go_back_to_price(self, event):
        global inputArea
        text = event.message.text
        reply_token = event.reply_token
                
        return text == '返回預算選單'
    def go_back_to_area(self, event):
        text = event.message.text
        reply_token = event.reply_token
                
        return text == '返回地區選單'
    def go_back_to_type(self, event):
        text = event.message.text
        reply_token = event.reply_token
                
        return text == '返回時段選單'    
    def on_enter_inputType(self, event):
        reply_token = event.reply_token
        print('enter inputtype')
        global inputType
        title = f'您選擇的區域是 \"{inputArea}\", 您希望用餐的時段是何時呢?'
        text = '請選擇任一時段'
        col = []
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/2.png',
            title=title,
            text='請選擇任一時段',
            actions=[
                MessageAction(
                    label = '早餐',
                    text ='早餐'
                ),
                MessageAction(
                    label = '午餐',
                    text = '午餐'
                ),
                MessageAction(
                    label = '晚餐',
                    text = '晚餐'
                )
            ]
        ))
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/2.png',
            title=title,
            text='請選擇任一時段',
            actions=[
                MessageAction(
                    label = '宵夜',
                    text = '宵夜'
                ),MessageAction(
                    label=f'返回地區選單',
                    text =f'返回地區選單'
                ),MessageAction(
                    label=f'返回主選單',
                    text =f'返回主選單'           
                )
            ]
        ))

        send_carousel_message(reply_token, col)
 
    def is_going_to_inputPrice(self, event):
        global inputType
        text = event.message.text
        reply_token = event.reply_token
        if text in inputTypeDict:
            inputType = text   
            return True
        return False
    def on_enter_inputPrice(self, event):
        reply_token = event.reply_token
        print('enter inputtype')
        global inputPrice
        title = f'您選擇的區域是 \"{inputArea}\", 用餐的時段是\"{inputType}\",那預算方面如何呢?'
        col = []
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/2.png',
            title=title,
            text='下方選擇您的預算',
            actions=[
                MessageAction(
                    label = 'NT$150以內',
                    text ='NT$150以內'
                ),
                MessageAction(
                    label = 'NT$150~NT$600',
                    text = 'NT$150~NT$600'
                ),
                MessageAction(
                    label = 'NT$600~NT$1200',
                    text = 'NT$600~NT$1200'
                )
            ]
        ))
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/2.png',
            title=title,
            text='下方選擇您的預算',
            actions=[
                MessageAction(
                    label = '都可以',
                    text = '都可以'
                ),
                MessageAction(
                    label = '返回時段選單',
                    text ='返回時段選單'
                ),
                MessageAction(
                    label = '返回主選單',
                    text = '返回主選單'
                )
            ]
        ))

        send_carousel_message(reply_token, col)
        
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
        textPrice = "無資料"
        if inputPrice == '1':
            textPrice = 'NT$150以內'
        elif inputPrice == '2':
            textPrice = 'NT$150~NT$600'
        elif inputPrice == '3':
            textPrice = 'NT$600~NT$1200'
        elif inputPrice == '0':
            textPrice = '都可以'

        title = f'根據您的"{inputArea}, {inputType}, {textPrice}"需求為您提供{len(foodList)}間餐廳' if len(foodList) > 0 else f'很抱歉,我找不到資料'
        col = []
        c = CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/3.png',
            title=title,
            text='請慢用~',
            actions=[
                MessageAction(
                    label='點我要其他推薦',
                    text='再給我其他的'
                ),
                MessageAction(
                    label='回上一頁',
                    text='返回預算選單'
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
            des = f'消費: {t.priceInfo} 營業資訊: {t.openInfo}'
            if len(des) > 60 :
                des = des[0:56]+'...略'
            
            c = CarouselColumn(
            thumbnail_image_url= f'{t.img_src}',
            title = f'{t.name}({t.starInfo}★)',
            text=f'{des}',
            actions=[
                URIAction(
                    label='查看更多',
                    uri=f'{t.web_src}'
                ),
                PostbackAction(
                    label=f'{t.locInfo}',
                    data='action=none'
                ),PostbackAction(
                    label=f'★☆★☆★☆★☆★☆★☆★',
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
        reply_token = event.reply_token
        title = '我是主選單~'
        col = []
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/4.png',
            title=title,
            text='請點選功能',
            actions=[
                MessageAction(
                    label=f'我想找吃的',
                    text =f'我想找吃的' 
                ),MessageAction(
                    label=f'猜猜我想吃什麼',
                    text =f'猜猜我想吃什麼'
                ),MessageAction(
                    label=f'敬請期待',
                    text =f'敬請期待'
                )
            ]
        ))
        send_carousel_message(reply_token, col)

# 1.你想要 解渴?
# 2.你想要 熱的?
# 3.你想要 吃肉?
guessDict = {
    '是': {'是' : {'是' : ['牛肉麵','藥燉排骨','蚵仔麵線','麻辣火鍋','魚湯','魚丸湯'],
                   '否' : []},
           '否' : {'是' : [],
                   '否' : []}},
    '否': {'是' : {'是' : ['滷肉飯','便當','肉圓','炸雞','鼎泰豐小籠包','鵝肉','加熱滷味','三杯雞','蚵仔煎','雞翅飯捲','超大貢丸','生煎包'],
                   '否' : []},
           '否' : {'是' : [],
                   '否' : []}}
}
1.否 2.是 3.否
甜不辣
臭豆腐
蔥抓餅
地瓜
擔仔麵
筒仔米糕
粄條
蒸春捲

1.否 2.否 3.是
卦包
1.否 2.否 3.否
胡椒餅
麻糬
鐵蛋
三明治
皮蛋豆腐
鳳梨酥
麵包
燒餅油條
1.是 2.否 3.是
猜不到
1.是 2.否 3.否
珍珠奶茶
剉冰
愛玉

1.是 2.是 3.否
甜不辣
鼎邊銼
豬血湯

    # def on_exit_state1(self):
    #     print("Leaving state1")

    # def on_exit_state2(self):
    #     print("Leaving state2")
