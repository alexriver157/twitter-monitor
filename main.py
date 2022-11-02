import requests
import re
import time
import json
import random
from datetime import datetime
from threading import Thread
import webbrowser
from websocket_server import WebsocketServer
import os
import pytesseract
from ocr import OCR

past = " "

enOC= True

reg = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def onl(text):
    return re.sub('[\W_]+', '', text)


def parse(pull, rest_id):
    global past
    pfp = pull["globalObjects"]['users'][rest_id]['profile_image_url_https']
    pull = pull["globalObjects"]["tweets"]
    for tweet in pull:
        x = pull[tweet]
        d = datetime.strptime(x['created_at'], r'%a %b %d %H:%M:%S +0000 %Y')
        age = time.time() - (d - datetime(1970,1,1)).total_seconds()
        if (x["user_id_str"] == rest_id and age < 4 and x["full_text"] != past):
            z = x["full_text"]
            links=[]
            images=[]
            ocr=[]
            threads=[]
            ocrLinks=[]
            if ('urls' in x['entities']):
                for i, url in enumerate(x['entities']['urls']):
                    z = z.replace(x['entities']['urls'][i]['url'], x['entities']['urls'][i]['expanded_url'])
                    links.append(x['entities']['urls'][i]['expanded_url'])
           
            if ('media' in x['entities']):
                for i, image in enumerate(x['extended_entities']['media']):
                    t = image["media_url"]
                    if enOC:
                        img = (image["media_url"])
                        print(img)
                        def returnOcr (img):
                            orc = OCR(img)
                            if re.search('[a-zA-Z0-9]', orc):
                                ocr.append(orc)
                                ocrLink= re.findall(reg, orc)
                                if (ocrLink):
                                    ocrLinks.extend(ocrLink)
                        tt = Thread(target=returnOcr, args=(img,))
                        threads.append(tt)
                    images.append(t)
                    #Remove the image urls
                    z = z.replace(x['entities']['media'][i]['url'], "")
                for thread in threads:
                    thread.start()
                def sendOCR(threads):
                    for x in threads:
                        x.join()
                    server.send_message_to_all(json.dumps({"ocr":ocr, "ocrlink":ocrLinks}))
                if enOC: Thread(target=sendOCR, args=(threads,)).start()
            print(z)
            print(onl(z))
            past = x["full_text"]
           # print(age)
            l = f"https://twitter.com/user/status/{x['id_str']}"
            y = json.dumps({"name":names[rest_id], "url":l,"text":z,"link":links, "pfp":pfp, "img":images})
            print(y)
            server.send_message_to_all(y)
            print(datetime.now())
           

def genBear():
    #Take the bearer token from the site
    token_regex = re.compile(r"A{20}.{84}")
    bear = requests.get("https://abs.twimg.com/responsive-web/client-web/main.a8574df5.js")
    token = token_regex.findall(bear.text)
    #Make sure there is a token, else error
    assert len(token) == 1
    return f"Bearer {token}"

#constant token from twitter
headers = {"Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"}

#Needs to be regen every couple hours
def guestToken():
    resp = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers)
    
    headers["x-guest-token"] = json.loads(resp.text)["guest_token"]
    
    print("Genned guest token -", datetime.now())
    return {"Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA", "x-guest-token": json.loads(resp.text)["guest_token"]}


names={}
ids = []
def restId(users):
    global names
    for username in users:
        url = f"https://api.twitter.com/graphql/4S2ihIKfF3xhp-ENxvUAfQ/UserByScreenName?variables=%7B%22screen_name%22%3A%22{username}%22%2C%22withHighlightedLabel%22%3Atrue%7D"
        resp = requests.get(url, headers=headers)
        ids.append(resp.json()['data']['user']['rest_id'])
        names[resp.json()['data']['user']['rest_id']] = username





proxies = []

def tw(rest_id):
    hed = guestToken()
    while True:
        for _ in range(179):
            #prx = {"https": "https://"+proxies[random.randint(0,len(proxies)-1)]}
            urly = (f"https://api.twitter.com/2/timeline/profile/{rest_id}.json?count=2&tweet_mode=extended")
            #urly = "https://api.twitter.com/1.1/lists/statuses.json?list_id=1348071024965808129&count=2"
            resp = requests.get(urly, headers=hed,) #proxies=prx
            try: 
                parse(resp.json(), rest_id)
            except KeyError:
                print(resp.json())
                hed = guestToken()
                print(datetime.now())
        hed = guestToken()
            

#Startup
users = [""]


           


if __name__ == "__main__":
    webbrowser.open("file://"+os.path.realpath("index.html"), new=2)
    server = WebsocketServer(13254, host='localhost')
    guestToken()
    restId(users)
    for rest_id in ids:
        z = Thread(target=tw, args=(rest_id,))
        z.daemon = True
        z.start()
    #server.set_fn_new_client(new_client)
    server.run_forever()
