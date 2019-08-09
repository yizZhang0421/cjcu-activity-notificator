import requests as req
import json, re, copy
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
    db=connector.connect(host="***.***.***.***",database='********',user="***********",passwd="***********")
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

from flask import Flask, request
app = Flask(__name__)
@app.route('/db', methods=['GET'])
def db():
    return json.dumps(do('select * from record'))

@app.route('/', methods=['POST'])
def hello():
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
                            'Authorization': 'Bearer *****'
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
                            'Authorization': 'Bearer *****'
                            },
                    data=json.dumps({
                            'replyToken': body['events'][0]['replyToken'],
                            'messages': [{'type':'text', 'text':'空頁'}]
                            }))
    return 'OK'
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)


