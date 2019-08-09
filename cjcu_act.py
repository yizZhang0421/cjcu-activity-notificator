import requests as req
from bs4 import BeautifulSoup
import json, re, copy
first_time=True
flex_item_layout=   {
                       "type":"bubble",
                       "styles":{
                          "footer":{
                             "separator":True
                          }
                       },
                       "body":{
                          "type":"box",
                          "layout":"vertical",
                          "contents":[
                             {
                                "type":"text",
                                "text":"活動名稱",
                                "weight":"bold",
                                "size":"sm",
                                "margin":"md"
                             },
                             {
                                "type":"separator",
                                "margin":"xxl"
                             },
                             {
                                "type":"box",
                                "layout":"vertical",
                                "margin":"xxl",
                                "spacing":"sm",
                                "contents":[
                                   {
                                      "type":"box",
                                      "layout":"horizontal",
                                      "contents":[
                                         {
                                            "type":"text",
                                            "text":"報名狀態",
                                            "size":"sm",
                                            "color":"#555555",
                                            "flex":0
                                         },
                                         {
                                            "type":"text",
                                            "text":"準備中",
                                            "size":"sm",
                                            "color":"#111111",
                                            "align":"end"
                                         }
                                      ]
                                   },
                                   {
                                      "type":"box",
                                      "layout":"vertical",
                                      "margin":"lg",
                                      "spacing":"sm",
                                      "contents":[
                                         {
                                            "type":"button",
                                            "style":"link",
                                            "height":"sm",
                                            "action":{
                                               "type":"uri",
                                               "label":"LINK",
                                               "uri":"https://linecorp.com"
                                            }
                                         }
                                      ]
                                   }
                                ]
                             }
                          ]
                       }
                    }
broadcast_layout_carousel=   {
                       "type":"flex",
                       "altText":"this is a flex message",
                       "contents":{
                          "type":"carousel",
                          "contents":[]
                       }
                    }
broadcast_layout=   {
                       "type":"flex",
                       "altText":"this is a flex message",
                       "contents":{}
                    }
from mysql import connector
def do(command):
    db=connector.connect(host="***.***.***.***",database='********',user="****",passwd="***********")
    cursor=db.cursor()
    try:
        cursor.execute(command)
        if cursor.description==None:#not query
            db.commit()
            db.close()
            return 'ok'
        columns = [col[0] for col in cursor.description]
        dictionary = [dict(zip(columns, row)) for row in cursor.fetchall()]
        db.close()
        return dictionary
    except connector.IntegrityError as err:
        #error no reference: https://dev.mysql.com/doc/refman/8.0/en/server-error-reference.html
        db.close()
        return str(err.errno)
def broadcast(act):
    item=copy.deepcopy(flex_item_layout)
    item['body']['contents'][0]['text']=act['name']
    item['body']['contents'][2]['contents'][0]['contents'][1]['text']=act['status']
    item['body']['contents'][2]['contents'][1]['contents'][0]['action']['uri']=act['link']
    wraper=copy.deepcopy(broadcast_layout)
    wraper['contents']=item
    req.post(
            url='https://api.line.me/v2/bot/message/broadcast', 
            headers={
                    'Authorization': 'Bearer ****************************************************************************************************************************************************************************',
                    'Content-Type': 'application/json'
                    },
            data=json.dumps({'messages':[wraper]})
    )
def crawler():
    for i in range(1000):
        res=req.post(
                url='https://act.cjcu.edu.tw/ActiveSite/Manager/WS0001.asmx/GetActiveOpenALLAndClass',
                data="{'page':'"+str(i)+"','dep':'','actclass':''}",
                headers={
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
                        'Connection': 'keep-alive',
                        'Content-Length': '33',
                        'Content-Type': 'application/json; charset=UTF-8',
                        'Cookie': '_ga=GA1.3.1239890859.1551587059; G_ENABLED_IDPS=google; ASP.NET_SessionId=bkserr3yyrsmyph3zeihwaqm',
                        'Host': 'act.cjcu.edu.tw',
                        'Origin': 'https://act.cjcu.edu.tw',
                        'Referer': 'https://act.cjcu.edu.tw/ActiveSite/ActiveList.aspx',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                        'X-Requested-With': 'XMLHttpRequest'
                        })
        data=json.loads(res.text)
        data=json.loads(data['d'])
        if len(data)==0:
            break
        for j in data:
            if j['Student_limit']=='1' and j['Status']!='ending':
                if len(do('select * from record where `id`="'+str(j['ID'])+'"'))!=0:
                    do('update record set `status`="'+str(j['Status'])+'" where `id`="'+str(j['ID'])+'"')
                    continue
                else:
                    do('insert into record values("'+str(j['ID'])+'","'+str(j['Name'])+'","'+str(j['Status'])+'","'+'https://act.cjcu.edu.tw/ActiveSite/act.aspx?id='+str(j['ID'])+'")')
                    if first_time==False:
                        broadcast({'name': str(j['Name']),'status': str(j['Status']),'link': 'https://act.cjcu.edu.tw/ActiveSite/act.aspx?id='+str(j['ID'])})
            else:
                do('delete from record where `id`="'+str(j['ID'])+'"')
    
    for i in range(1, 1000):
        res=req.post(url='https://act.cjcu.edu.tw/ActiveSite/MicroCreditsList.aspx?page='+str(i))
        soup=BeautifulSoup(res.text, 'html.parser')
        soup=soup.find(name='div', attrs={'id':'exp'})
        if len(soup.findChildren(recursive=False))==0:
            break
        for j in soup.findChildren(recursive=False):
            for k in j.findChildren(recursive=False):
                if k.find_all('li')[4].text.split('\xa0')[1]!='已截止':
                    id=re.search('\d+$', ('https://act.cjcu.edu.tw/ActiveSite/'+k.find('a', attrs={'class':'act_link'})['href'])).group(0)
                    if len(do('select * from record where `id`="'+str(id)+'"'))!=0:
                        do('update record set `status`="'+str(k.find_all('li')[4].text.split('\xa0')[1])+'" where `id`="'+str(id)+'"')
                        continue
                    else:
                        do('insert into record values("'+str(id)+'","'+str(k.find('h5').text)+'","'+str(k.find_all('li')[4].text.split('\xa0')[1])+'","'+'https://act.cjcu.edu.tw/ActiveSite/'+k.find('a', attrs={'class':'act_link'})['href']+'")')
                        if first_time==False:
                            broadcast({'name': k.find('h5').text,'status': k.find_all('li')[4].text.split('\xa0')[1],'link': 'https://act.cjcu.edu.tw/ActiveSite/'+k.find('a', attrs={'class':'act_link'})['href']})
                else:
                    id=re.search('\d+$', ('https://act.cjcu.edu.tw/ActiveSite/'+k.find('a', attrs={'class':'act_link'})['href'])).group(0)
                    do('delete from record where `id`="'+str(id)+'"')

import threading, time
def t_job():
    global first_time
    global flex_item_layout
    global broadcast_layout_carousel
    global broadcast_layout
    while 1:
        crawler()
        first_time=False
        time.sleep(60)
t = threading.Thread(target = t_job)
t.start()

from flask import Flask, request

app = Flask(__name__)
@app.route('/db', methods=['GET'])
def db():
    return json.dumps(do('select * from record'))

@app.route('/', methods=['POST'])
def hello():
    global first_time
    global flex_item_layout
    global broadcast_layout_carousel
    global broadcast_layout
    body = request.data
    body=json.loads(body)
    print(body['events'][0]['message']['text'])
    page=re.match('(\\d+)', body['events'][0]['message']['text'])
    if page!=None:
        page=page.group(0)
        page=int(page)
        wraper=copy.deepcopy(broadcast_layout_carousel)
        wraper['contents']['contents']=list()
        for act in do('select * from record')[(page*10)-10:page*10]:
            item=copy.deepcopy(flex_item_layout)
            item['body']['contents'][0]['text']=act['name']
            item['body']['contents'][2]['contents'][0]['contents'][1]['text']=act['status']
            item['body']['contents'][2]['contents'][1]['contents'][0]['action']['uri']=act['link']
            wraper['contents']['contents'].append(item)
        if len(wraper['contents']['contents'])!=0:
            req.post(
                    url='https://api.line.me/v2/bot/message/reply',
                    headers={
                            'Content-Type':'application/json',
                            'Authorization': 'Bearer ****************************************************************************************************************************************************************************'
                            },
                    data=json.dumps({
                            'replyToken': body['events'][0]['replyToken'],
                            'messages': [wraper]
                            }))
        else:
            req.post(
                    url='https://api.line.me/v2/bot/message/reply',
                    headers={
                            'Content-Type':'application/json',
                            'Authorization': 'Bearer ****************************************************************************************************************************************************************************'
                            },
                    data=json.dumps({
                            'replyToken': body['events'][0]['replyToken'],
                            'messages': [{'type':'text', 'text':'空頁'}]
                            }))
    return 'OK'
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)


