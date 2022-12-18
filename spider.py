import requests
import re
import random
import math
from bs4 import BeautifulSoup


# inputArea  = '中西區'
# inputType  = '宵夜'
# inputPrice = '1'
searchWeb = 'https://ifoodie.tw'
subWebTitle_1 = '/explore/台南市'
Page = 1

class Store:
    def __init__(self, name, img_src, web_src, starInfo, priceInfo, openInfo, locInfo) -> None:
        self.name = name
        self.img_src = img_src
        self.web_src = web_src
        self.starInfo = starInfo
        self.priceInfo = priceInfo
        self.openInfo = openInfo
        self.locInfo = locInfo

def ScratchPages(inputArea:str, inputType:str, inputPrice:str, wantPickNum:int):
    subWeb = f'{searchWeb}'
    subWeb = subWeb+(f'{subWebTitle_1}/{inputArea}/list/{inputType}')
    if inputPrice != '0':
        subWeb = subWeb+f'?priceLevel={inputPrice}'
    mainpage = requests.get(subWeb)
    # searchWeb = '{mainWeb}/XX區/list/xx餐{?priceLevel=消費模式}'
    main = BeautifulSoup(mainpage.text, 'html.parser')
    # print(main.text)
    count_find = main.find('span', class_='jsx-694075194 text')
    k = re.findall('\d+',count_find.text)
    
    PageMax = math.ceil(int(k[0])/15)
    print('最多幾頁：'+str(PageMax))
    ansList = []
    # Page = 0
    Page = random.randint(1,PageMax)
    # while Page <= PageMax:
    subWeb = f'{searchWeb}'
    subWeb = subWeb+(f'{subWebTitle_1}/{inputArea}/list/{inputType}')
    if inputPrice != '0':
        subWeb = subWeb+f'?priceLevel={inputPrice}'
    if Page > 1:
        subWeb = subWeb+f'&page={Page}'
    print(f'網址: {subWeb}')
    mainpage = requests.get(subWeb)
    # searchWeb = '{mainWeb}/XX區/list/xx餐{?priceLevel=消費模式}'
    main = BeautifulSoup(mainpage.text, 'html.parser')
    # print(main.text)
    count_find = main.find('span', class_='jsx-694075194 text')
    
    k = re.findall('\d+',count_find.text)
    print(k)

    res_find = main.findAll('div',attrs={'class':'jsx-3292609844 restaurant-info'})#.find('a').find('img')
    
    idxes = main.findAll('span', attrs={'class':'jsx-3292609844 index'})
    idxes_list = []

    for idx in idxes:        
        idxText = re.findall('\d+',idx.text)
        idxes_list.append(int(idxText[0]))
    
    # maxCnt = idxes_list[-1]
    rescnt = idxes_list[0]        #爬蟲的地一筆資料idx
    maxPickSize = len(idxes_list) if len(idxes_list) < wantPickNum else wantPickNum
    
    randomList = random.sample(idxes_list, maxPickSize)        
    print('randomList : ')
    print(randomList)
    print('開始直 : '+str(rescnt))
    # while rescnt < maxCnt:
    #     if rescnt not in randomList:
    #         rescnt+=1
    #         print("not in "+str(rescnt))
    #         continue
        
    # return []
    for res in res_find:
        if rescnt not in randomList:
            rescnt+=1
            # print("not in "+str(rescnt))
            continue
        res_inside_website = res.find('a', attrs={'class':'jsx-3292609844'})
        #進去子網頁找他的圖片
        res_website = searchWeb+res_inside_website['href']
        # print(res_website)
        resWebPage = requests.get(res_website)
        resWeb = BeautifulSoup(resWebPage.text, 'html.parser')
        
        img_find = resWeb.find('img',attrs={'class':'jsx-3296965063 cover'})
        web_src_find = resWeb.find('a',attrs={'class':'jsx-3296965063 restaurant-name'})
        star_find = resWeb.find('div',attrs={'class': 'jsx-1207467136 text'})
        open_text_find = resWeb.find('div',attrs={'class': 'jsx-1969054371 open-text'})
        price_find = resWeb.find('div', attrs={'class': 'jsx-3296965063 price-outer'})
        location_find = resWeb.find('span', attrs={'class':'jsx-1969054371 detail'})


        img_src = img_find['src'] 
        web_src = web_src_find['href']
        star = star_find.text if star_find!=None else "無資料"
        open_text = open_text_find.text if open_text_find!=None else "無資料"
        price_text = price_find.text if price_find!=None else "無資料"
        name = web_src_find.text if web_src_find!=None else "無資料"
        loc_text = location_find.text if location_find!=None else "無資料"

        # print('名字 : '+name)
        # print('img_src = '+img_src)
        # print('web_src = '+web_src)
        # print('star = ' + star)
        # print(price_text)
        # print('營業 = '+ open_text)
        # print('地址 = ' + loc_text)
        t = Store(name, img_src, web_src, star, price_text, open_text, loc_text)
        ansList.append(t)
        rescnt+=1
    print(str(len(res_find))+'家')
    print('第'+str(Page)+'頁')
    return ansList
if __name__ == "__main__":
    inputArea  = '中西區'
    inputType  = '宵夜'
    inputPrice = '1'
    listA = ScratchPages(inputArea, inputType, inputPrice)
    print("listSize : "+str(len(listA)))
    print(listA[0])
    print(type(listA[0]))