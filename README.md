# 台南吃什麼(FindFoodTainan-Chatbot)

## 前言
因為發現生活周遭的人常常為了等一下吃什麼感到困擾，所以就藉此機會結合爬蟲做了一點簡單的小應用。

## 構想
主要有3個功能
#### 1. 我想找吃的
爬取[愛食記](https://ifoodie.tw/)網站的資料，並將資料稍作整合後以LineBOT推回給用戶。
#### 2. 猜猜我想吃什麼
整理台灣常見的食物，然後藉由幾個問題，推測你想吃什麼。
#### 3. 地下城小遊戲
地下城中會觸發一些事件，可以於點餐後等餐點來前殺時間用。
## 環境
- Windows 11
- python 3.7.7

## 技術
- Beautifulsoup4
    - 爬取[愛食記](https://ifoodie.tw/)網站的資料

## 使用教學(本地端Windows版)
1. 先下載 [`Graphviz`](https://graphviz.org/download/)並將其解壓縮到專案目錄下，並在「app.py」裡面時加上
```python3=
os.environ['PATH'] =  os.pathsep + './Graphviz/bin/'
```
2. install 所需套件
```python3!
pip install -r requirements.txt
```
4. 下載並安裝 [ngrok](https://ngrok.com/download)
5. 打開ngrok，並輸入以下指令後，ngrok會給你一串網址
(ex.https://XXXX-XXX-XXX-XX-XX.XX.ngrok.io):
```shell!
ngrok http 8000
```
6. 在專案目錄下產生出一個`.env`檔案，並填入以下四個資訊
```python3=
LINE_CHANNEL_SECRET='這裡填linebot的 Channel secret'
LINE_CHANNEL_ACCESS_TOKEN='這裡填linebot的 Channel access token'
PORT=8000
MAIN_WEB_URL='ngrok給你的網址'
```
7. 記得將Line developer裡的webhook改成你目前的ngrok網址並啟用webhook，然後在專案目錄下輸入指令:
```shell!
python3 app.py 
或 
python app.py
```
8. 用LINE測試能否使用~
## 使用說明
- 基本操作
    - 跟著按鈕按就可以了，大部分情況不需要自己輸入字
    - 若輸入事件判定外的字會重傳一次當前狀態的事件
    - 以下兩個指令皆可隨時輸入(在地下城除外)
        - `返回主選單`
            - 返回主選單
        - `fsm`
            - 傳回有限狀態圖
- 架構圖 
    - 主選單跳三個選項`我想找吃的`、`猜猜我想吃什麼`、`地下城小遊戲`
    1. 我想找吃的
        ---
        1. 先選擇區域
              - 目前:區域(X/3) : 告知你目前的頁數
              - 其他區域 : 看其他區域
              - 返回主選單
        ---
        2. 選擇時段
              - 早餐
              - 午餐
              - 晚餐
              - 宵夜
              - 返回地區選單
              - 返回主選單
        ---
        3. 選擇預算
            - NT$150以內
            - NT$150~NT$600
            - NT$600~NT$1200
            - 都可以
            - 返回時段選單
            - 返回主選單
        ---
        4. 爬蟲並將結果推送給用戶
            - 點我要其他推薦 : 可以用相同條件再推幾間餐廳給你 
            - 回上一頁
            - 返回主選單
        ---
    2. 猜猜我想吃什麼
        ---
        1. 你覺得渴嗎
            - 是
            - 否
            - 返回主選單
        ---
        2. 你想吃熱的嗎
            - 是
            - 否
            - 回上一步
            - 返回主選單
        ---
        3. 你想吃肉嗎
            - 是
            - 否
            - 回上一步
            - 返回主選單
        ---
        4. 結果
            - 回上一步
            - 返回主選單
        ---
    3. 地下城小遊戲(可以拿來殺時間)
       ---
       遊戲機制，玩家可以選擇進入地下城，並不斷向前探查，
       隨著層數下降，遇到的怪物會越來越強，獎勵也會越來越豐厚。
       而探查可能會觸發三種以下事件:
       1. 空事件:不會發生任何事
       2. 怪物事件:遇到怪物，打贏了可以獲得經驗值、金幣，並將層數下降一層，打輸了目前不會有懲罰XD
       3. 寶物事件:獲得寶物，可以為角色帶來增益
       ---
       1. 進入地下城
          - 向前探查:觸發新事件
          - 返回地下城選單:離開地下城
       ---
       2. 查看角色資訊
          - 會傳回角色的基本資訊
           ```
           最初始角色狀態
           生命: 15/15
           傷害: 5
           防禦: 5
           層數: 1
           金錢: 0
           等級: 1 (0/5)
       ---
       3. 返回主選單
       ---
## 使用示範
### 主選單
![](https://i.imgur.com/rpGQYbe.jpg)
### 找吃的
![](https://i.imgur.com/2iM2Ca5.jpg)
![](https://i.imgur.com/kgTQ5qw.jpg)
![](https://i.imgur.com/SOhrRlJ.jpg)
![](https://i.imgur.com/3w8Pyc3.jpg)
### 猜猜吃什麼
![](https://i.imgur.com/tlc7bAV.jpg)
![](https://i.imgur.com/cfczvET.jpg)
### 地下城
![](https://i.imgur.com/YZg0gLf.jpg)
## FSM
![](https://i.imgur.com/m6IqNC6.png)
### state說明
user: 主選單
***
`有關「我想找吃的」的States`
- inputArea: 選擇要搜尋的區域
- inputArea2: 選擇要搜尋的區域(差別在於有其他的地區選項)
- inputArea3: 選擇要搜尋的區域(差別在於有其他的地區選項)
- inputType: 選擇要吃早餐、午餐、晚餐還是宵夜
- inputPrice: 選擇預算
- startSearch: 推薦餐廳給你
---
`有關「猜猜我想吃什麼」的States`    
- GuessStart: 根據引導做出是或否的選擇
- Guess2: 根據引導做出是或否的選擇
- Guess3: 根據引導做出是或否的選擇
- GuessResult: 給予推薦的食物
---
`有關「地下城小遊戲」的States`
- PlayMenu: 地下城小遊戲的選單
- PlayerStatus: 展示角色資訊
- Advanture: 可以選擇要不要繼續冒險或退出到地下城選單
- Nothing: 什麼事也沒發生
- MeetMob: 遇到怪物事件
- GetTreasure: 獲得寶物事件
- Combating: 戰鬥並計算結果
- CombatResultWin: 戰鬥勝利
- CombatResultLose: 戰鬥失敗
***
## 部屬到 Render

1. 註冊Render的帳號
2. 選擇Web Service
3. 把auto deploy關掉
4. 將原本打在.env檔裡面的環境變數資訊加到environment variables裡面
5. build command那邊打pip install -r requirements.txt , run command那邊則是python app.py
6. 等它跑好，測試機器人~


## 相關資源 
[TOC-Project-2020](https://github.com/NCKU-CCS/TOC-Project-2020) ❤️ [@winonecheng](https://github.com/winonecheng)

Flask Architecture ❤️ [@Sirius207](https://github.com/Sirius207)

[愛食記](https://ifoodie.tw/)

[Line line-bot-sdk-python](https://github.com/line/line-bot-sdk-python/tree/master/examples/flask-echo)

圖片皆來自網路
