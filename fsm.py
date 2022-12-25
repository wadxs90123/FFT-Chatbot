from transitions.extensions import GraphMachine

import random
import requests
import re
from spider import ScratchPages
from spider import Store
from linebot import LineBotApi, WebhookParser
from linebot.models import QuickReplyButton,MessageAction,MessageEvent, TextMessage, TextSendMessage, VideoSendMessage
from linebot.models import PostbackAction,URIAction, CarouselColumn,ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from utils import send_text_message 
from utils import send_carousel_message
from utils import send_button_message 
from utils import send_image_message
from utils import send_video_message
from utils import send_text_multiple_message
from utils import send_quick_reply
from bs4 import BeautifulSoup

import os
main_url = os.getenv("MAIN_WEB_URL",None)
import math

class Mob:
    def __init__(self, stage) -> None:
        name = ['史萊姆','殭屍','骷髏']
        self.HP = math.floor(stage*2+stage+1+random.randint(0,stage*10))
        self.name = random.sample(name,1)[0]
        self.LV = random.randint(stage-1,stage+3)
        self.Damage = math.floor(5 + random.randint(0, stage*10))
        self.Armor = math.floor(5 + random.randint(0, stage*10))
        self.exp = math.floor(2+random.randint(0,stage*15))
        self.coins = math.floor(2+random.randint(0,stage*20))
class player:
    def __init__(self) -> None:
        self.HP = 15
        self.nowHp = 15
        self.EXP = 0
        self.Damage = 5
        self.Armor = 5
        self.LV = 1
        self.Stage = 1
        self.coin = 0
        self.mob = None
        self.lvUpEXP = self.LV**2+self.LV*3+1
    def levelUpCal(self):
        return self.LV**2+self.LV*3+1
    def update(self):
        msg = ['你死了', '你升級了','你殺死怪物']
        res = []
        if (self.mob is not None) and self.mob.HP <= 0:
            res.append(msg[2])
            res.append(self.mob.name)
            res.append(self.mob.exp)
            res.append(self.mob.coins)
            self.EXP += self.mob.exp
            self.coin += self.mob.coins
            self.Stage+=1
            self.mob = None
        if self.EXP >= self.lvUpEXP:
            self.LV+=1
            self.EXP-=self.lvUpEXP
            self.lvUpEXP = self.levelUpCal()
            self.HP += 2
            self.nowHp = self.HP   
            self.Damage += 2
            self.Armor += 2
            res.append(msg[1])
        if self.nowHp <= 0:
            self.nowHp = self.HP
            res.append(msg[0]) 
        return res 
    def findTreasure(self):
        hp = random.randint(0, 10*(self.Stage))        
        self.HP += hp
        dp = random.randint(0, 10*(self.Stage))
        self.Damage += dp
        
        ar = random.randint(0, 10*(self.Stage))        
        self.Armor += ar
        return f'生命 +{hp} 傷害 +{dp} 防禦 +{ar}'
    def meetMob(self):
        self.mob = Mob(self.Stage)
    def damageToMob(self):
        totaldamage = self.Damage - self.mob.Armor
        if totaldamage <= 0:
            totaldamage = 1
        self.mob.HP-=totaldamage
    def damageFromMob(self):
        totaldamage = self.mob.Damage - self.Armor
        if(totaldamage <= 0):
            totaldamage =1
        self.nowHp -= totaldamage
    def combat(self):
        while True:
            self.damageToMob()
            log = self.update()
            if '你殺死怪物' in log:
                s = [f'殺死怪物{log[1]}',f'地下{self.Stage-1}層:挑戰成功!',f'獲得 {log[2]} 經驗值,及 {log[3]} 金幣'] 
                if '你升級了' in log:
                    s.append('你升級了')
                return s
            self.damageFromMob()
            log = self.update()
            if '你死了' in log:
                return '挑戰失敗'
            
searchWeb = 'https://ifoodie.tw/explore/台南市'
guessDict = {
    '是': {'是' : {'是' : ['牛肉麵','藥燉排骨','蚵仔麵線','麻辣火鍋','魚湯','魚丸湯'],
                   '否' : ['甜不辣','鼎邊銼','豬血湯']},
           '否' : {'是' : ['抱歉，你的心思難以捉摸，我無法提供您滿意的回答'],
                   '否' : ['珍珠奶茶','剉冰','愛玉']}},
    '否': {'是' : {'是' : ['滷肉飯','便當','肉圓','炸雞','鼎泰豐小籠包','鵝肉','加熱滷味','三杯雞','蚵仔煎','雞翅飯捲','超大貢丸','生煎包'],
                   '否' : ['甜不辣','臭豆腐','蔥抓餅','地瓜','擔仔麵','筒仔米糕','粄條','蒸春捲']},
           '否' : {'是' : ['卦包'],
                   '否' : ['胡椒餅','麻糬','鐵蛋','三明治','皮蛋豆腐','鳳梨酥','麵包','燒餅油條']}}
}
inputAreaGreetingDict = ['好的, 您想在哪區吃呢?']
inputAreaDict = ['新營區','鹽水區','白河區','柳營區','後壁區','東山區','麻豆區','下營區','六甲區','官田區'
                ,'大內區','佳里區','學甲區','西港區','七股區','將軍區','北門區','新化區','新市區','善化區'
                ,'安定區','山上區','玉井區','楠西區','南化區','左鎮區','仁德區','歸仁區','關廟區','龍崎區'
                ,'永康區','東區','南區','中西區','北區','安南區','安平區']
inputTypeDict = ['早餐', '午餐', '晚餐', '宵夜']

class TocMachine(GraphMachine):
    
    def __init__(self, **machine_configs):
        self.player = player()
        self.inputArea = ''
        self.inputType = ''
        self.inputPrice = ''
        self.firstGuess = ''
        self.SecondGuess = ''
        self.ThirdGuess = ''
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
        self.inputArea = ''
        self.inputType = ''
        self.inputPrice = ''
        self.firstGuess = ''
        self.SecondGuess = ''
        self.ThirdGuess = ''
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
                    label=f'地下城小遊戲',
                    text =f'地下城小遊戲'
                )
            ]
        ))
        send_carousel_message(reply_token, col)
    def is_going_to_PlayMenu(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '地下城小遊戲'
    def is_going_to_PlayerStatus(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '查看角色資訊'
    def is_going_to_Advanture(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '進入地下城'
    def is_going_to_GetTreasure(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '向前探查' and self.Dice == 2
    def is_going_to_Nothing(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '向前探查' and self.Dice == 0
    def is_going_to_MeetMob(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '向前探查' and self.Dice == 1
    def on_enter_PlayerStatus(self, event):
        text = event.message.text
        reply_token = event.reply_token
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="返回地下城選單", text="返回地下城選單")
            ),
        ]
        send_quick_reply(reply_token, f"能力值: 等級:{self.player.LV}({self.player.EXP}/{self.player.lvUpEXP}) 生命:{self.player.nowHp}/{self.player.HP} 傷害:{self.player.Damage} 防禦:{self.player.Armor} 金錢:{self.player.coin} 層數:{self.player.Stage}", buttons)
    def on_enter_PlayMenu(self, event):
        text = event.message.text
        reply_token = event.reply_token 
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="進入地下城", text="進入地下城")
            ),
            QuickReplyButton(
                action=MessageAction(label="查看角色資訊", text="查看角色資訊")
            ),
            QuickReplyButton(
                action=MessageAction(label="返回主選單", text="返回主選單")
            ),
        ]
        send_quick_reply(reply_token, f"您好，接下來有什麼打算呢?", buttons)
    def on_enter_Advanture(self, event):
        self.treasureFlag = False
        self.NothingFlag = False
        self.combatFlag = False
        self.meetFlag = False
        text = event.message.text
        reply_token = event.reply_token 
        self.Dice = random.randint(0,2)
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="向前探查", text="向前探查")
            ), 
            QuickReplyButton(
                action=MessageAction(label="返回地下城選單", text="返回地下城選單")
            ),
        ]
        send_quick_reply(reply_token, f"您好，接下來有什麼打算呢?(層數: 地下 {self.player.Stage} 層)", buttons)
    def on_enter_Nothing(self, event):
        text = event.message.text
        reply_token = event.reply_token
        text = event.message.text
        reply_token = event.reply_token 
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="返回主路線", text="返回主路線")
            ),
        ]
        msg_dict = ['你走進一個房間，發現空無一物']
    
        if self.NothingFlag == False:
            self.NothingFlag = True 
            self.NothingRndMsg = random.sample(msg_dict, 1)[0]

        player_inf = f'等級: {self.player.LV}({self.player.EXP}/{self.player.lvUpEXP}) 目前生命: {self.player.nowHp} / {self.player.HP}'
        send_quick_reply(reply_token, f"{player_inf}, {self.NothingRndMsg}，接下來有什麼打算呢?", buttons)
    def on_enter_MeetMob(self, event):
        if self.meetFlag == False:
            self.meetFlag = True
            self.player.meetMob()
        text = event.message.text
        reply_token = event.reply_token 
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="跟他打", text="跟他打")
            ),
            QuickReplyButton(
                action=MessageAction(label="返回主路線", text="返回主路線")
            ),
        ]
        player_inf = f'等級: {self.player.LV}({self.player.EXP}/{self.player.lvUpEXP}) 目前生命: {self.player.nowHp} / {self.player.HP}'
        send_quick_reply(reply_token, f"{player_inf}, 你遭遇到了怪物 {self.player.mob.name}(Lv.{self.player.mob.LV})(怪物資訊 生命:{self.player.mob.HP} 傷害:{self.player.mob.Damage}, 防禦:{self.player.mob.Armor})，接下來有什麼打算呢?", buttons)
    def on_enter_CombatResultWin(self, event):
        text = event.message.text
        reply_token = event.reply_token 
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="返回主路線", text="返回主路線")
            ),
        ]
        # s = [f'殺死怪物{log[1]}',f'地下{self.Stage-1}層:挑戰成功!',f'獲得 {log[2]} 經驗值,及 {log[3]} 金幣'] 
        #         if '你升級了' in log:
        #             s.append('你升級了')
        log = f'{self.combatResult[2]}'
        if self.combatResult[-1] =='你升級了':
            log+=f',恭喜升級,目前等級為 {self.player.LV}'
        send_quick_reply(reply_token, f"你打贏了,{log},接下來有什麼打算呢?", buttons)
    def on_enter_CombatResultLose(self, event):
        text = event.message.text
        reply_token = event.reply_token 
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="返回地下城選單", text="返回地下城選單")
            ),
        ]
        send_quick_reply(reply_token, f"你死了.", buttons)
    def on_enter_Combating(self, event):
        if self.combatFlag == False:
            self.combatFlag = True
            self.combatResult = self.player.combat()
        text = event.message.text
        reply_token = event.reply_token 
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="查看結果", text="查看結果")
            ),
        ]
        send_quick_reply(reply_token, f"你選擇戰鬥,結果如何呢...", buttons)
    def is_going_to_Combating(self, event):
        text = event.message.text
        return text == '跟他打'
    def is_going_to_CombatResultWin(self, event):
        text = event.message.text
        return self.combatResult != '挑戰失敗'
    def is_going_to_CombatResultLose(self, event):
        return self.combatResult == '挑戰失敗'
    def on_enter_GetTreasure(self, event):
        if self.treasureFlag == False: 
            self.treasurelog = self.player.findTreasure()
            self.treasureFlag = True 
        text = event.message.text
        reply_token = event.reply_token 
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="返回主路線", text="返回主路線")
            ),
        ]
        msg_dict = ['你找到了寶物']
        if self.treasureFlag == False: 
            self.treaRndMsg = random.sample(msg_dict, 1)[0]

        player_inf = f'等級: {self.player.LV}({self.player.EXP}/{self.player.lvUpEXP}) 目前生命: {self.player.nowHp} / {self.player.HP}'
        send_quick_reply(reply_token, f'{player_inf}, {self.treaRndMsg} 為你帶來增益 "{self.treasurelog}"，接下來有什麼打算呢?', buttons)
    def is_back_to_PlayMenu(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '返回地下城選單'
    def is_back_to_Advanture(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == '返回主路線'


    def is_going_to_GuessStart(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == "猜猜我想吃什麼"
    def is_going_to_Guess2(self, event):
        text = event.message.text
        reply_token = event.reply_token
        a = ['是','否']
        if text in a:
            self.firstGuess = text
            return True 
        return False
    def is_going_to_Guess3(self, event):
        text = event.message.text
        reply_token = event.reply_token
        a = ['是','否']
        if text in a:
            self.SecondGuess = text
            return True 
        return False
    def is_going_to_GuessResult(self, event):
        text = event.message.text
        reply_token = event.reply_token
        a = ['是','否']
        if text in a:
            self.ThirdGuess = text
            return True 
        return False
    def on_enter_GuessStart(self, event):
        text = event.message.text
        reply_token = event.reply_token  
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="是", text="是")
            ),
            QuickReplyButton(
                action=MessageAction(label="否", text="否")
            ),
            QuickReplyButton(
                action=MessageAction(label="返回主選單", text="返回主選單")
            ),
        ]
        send_quick_reply(reply_token, "你覺得渴嗎?", buttons)
    def is_back_to_GuessStart(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == "回上一步"
    def is_back_to_Guess2(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == "回上一步"
    def is_back_to_Guess3(self, event):
        text = event.message.text
        reply_token = event.reply_token
        return text == "回上一步"
    def on_enter_Guess2(self, event):
        text = event.message.text
        reply_token = event.reply_token  
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="是", text="是")
            ),
            QuickReplyButton(
                action=MessageAction(label="否", text="否")
            ),
            QuickReplyButton(
                action=MessageAction(label="回上一步", text="回上一步")
            ),
            QuickReplyButton(
                action=MessageAction(label="返回主選單", text="返回主選單")
            ),
        ]
        send_quick_reply(reply_token, "你想吃熱的嗎?", buttons)
    def on_enter_Guess3(self, event):
        text = event.message.text
        reply_token = event.reply_token  
        buttons = [
            QuickReplyButton(
                action=MessageAction(label="是", text="是")
            ),
            QuickReplyButton(
                action=MessageAction(label="否", text="否")
            ),
            QuickReplyButton(
                action=MessageAction(label="回上一步", text="回上一步")
            ),
            QuickReplyButton(
                action=MessageAction(label="返回主選單", text="返回主選單")
            ),
        ]
        send_quick_reply(reply_token, "你想吃肉嗎?", buttons)
    def on_enter_GuessResult(self, event):
        text = event.message.text
        reply_token = event.reply_token
        print(self.firstGuess, self.SecondGuess, self.ThirdGuess)
        resList = guessDict[self.firstGuess][self.SecondGuess][self.ThirdGuess]
        a = random.sample(resList,1)
        title = '結果'
        col = []
        col.append(CarouselColumn(
            thumbnail_image_url=f'{main_url}/img/4.png',
            title=title,
            text=f'{a[0]}',
            actions=[
                MessageAction(
                    label=f'回上一步',
                    text =f'回上一步'
                ),MessageAction(
                    label=f'返回主選單',
                    text =f'返回主選單'
                )
            ]
        ))
        send_carousel_message(reply_token, col)
    def response_false(self, event):
        return True
# 1.你想要 解渴?
# 2.你想要 熱的?
# 3.你想要 吃肉?
 
 

    # def on_exit_state1(self):
    #     print("Leaving state1")

    # def on_exit_state2(self):
    #     print("Leaving state2")
