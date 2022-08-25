import requests
import json
import hashlib
from privateAPI import private, key, location

def GetWeatherInfo():
    '''
    返回fore、now、text
    若text为''，则无报错
    '''
#    hlIP = hashlib.md5(private.encode("utf-8")).hexdigest()
#    urlip = "https://restapi.amap.com/v3/ip?key=2f84cf79e4e4e7b7b055fdb65bdb7d2c&sig=" + hlIP
    text = ''
#    try:
#        respond = requests.get(urlip)
#        locate = json.loads(respond.text)
#        adcode = locate['adcode']
#    except Exception as error:
#        adcode = 320115 # 南京
#        text += '%s ' % error

    urlfore = "https://devapi.qweather.com/v7/weather/3d?key=%s&location=%s" % (key, location)
    urlnow = "https://devapi.qweather.com/v7/weather/now?key=%s&location=%s" % (key, location)
    # 昆山：320583
    try:
        respond = requests.get(urlfore)
        fore = json.loads(respond.text)

        respond = requests.get(urlnow)
        now = json.loads(respond.text)
    except Exception as error:
        text += '%s ' % error
        fore = now = None
    return fore, now, text

if __name__ == "__main__":
    fore, now, text = GetWeatherInfo()
    #a = fore['forecasts'][0]['casts']
    print(fore)
    #b = now['lives'][0]
    print(now)
    print(text)
