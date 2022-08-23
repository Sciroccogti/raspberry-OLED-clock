import requests
import json
import hashlib
from privateAPI import private

def GetWeatherInfo():
    '''
    返回fore、now、text
    若text为''，则无报错
    '''
    hlIP = hashlib.md5(private.encode("utf-8")).hexdigest()
    urlip = "https://restapi.amap.com/v3/ip?key=2f84cf79e4e4e7b7b055fdb65bdb7d2c&sig=" + hlIP
    text = ''
    try:
        respond = requests.get(urlip)
        locate = json.loads(respond.text)
        adcode = locate['adcode']
    except Exception as error:
        adcode = 320115 # 南京
        text += '%s ' % error

    hlAll = hashlib.md5(("city=%s&extensions=all" % adcode + private).encode("utf-8")).hexdigest()
    hlBase = hashlib.md5(("city=%s&extensions=base" % adcode + private).encode("utf-8")).hexdigest()
    urlfore = "https://restapi.amap.com/v3/weather/weatherInfo?key=2f84cf79e4e4e7b7b055fdb65bdb7d2c&city=%s&extensions=all&sig=" % adcode + hlAll
    urlnow = "https://restapi.amap.com/v3/weather/weatherInfo?key=2f84cf79e4e4e7b7b055fdb65bdb7d2c&city=%s&extensions=base&sig=" % adcode + hlBase
    # 昆山：320583
    try:
        respond = requests.get(urlfore)
        fore = json.loads(respond.text)

        respond = requests.get(urlnow)
        now = json.loads(respond.text)
        # #将JSON编码的字符串转换回Python数据结构
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
