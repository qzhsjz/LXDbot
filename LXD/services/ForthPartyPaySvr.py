import nonebot
from aiocqhttp.exceptions import ActionFailed
from LXD.services.DBSvr import DB
import aiohttp
import config
import hashlib
import base64
import time

class ForthPaySvr:
    __db__ = None
    __QQbot__ = nonebot.get_bot()

    def __init__(self):
        self.__db__ = DB()

    async def getPayQRcode(self, price, type, orderuid, goodsname):
        orderid = repr(int(time.time())) + orderuid
        postdata = {
            'identification': config.pay_identification,
            'price': price,
            'type': type,
            'notify_url': config.pay_notify_url,
            'return_url': config.pay_return_url,
            'orderid': orderid,
            'orderuid': orderuid,
            'goodsname': goodsname,
        }
        keystr = goodsname + config.pay_identification + config.pay_notify_url + orderid + orderuid + price + config.pay_return_url + config.pay_token + type
        postdata['key'] = hashlib.md5(keystr.encode('utf-8')).hexdigest()
        async with aiohttp.ClientSession() as session:
            async with session.post('https://data.020zf.com/index.php?s=/api/pp/index_show.html', data=postdata) as response:
                r = await response.json()
                if r['code'] == 200:
                    async with aiohttp.ClientSession() as QRsession:
                        async with QRsession.get('https://data.020zf.com/api.php/pp/scerweima2?url=' + r['data']['qrcode']) as resp:
                            return base64.b64encode(await resp.read()).decode()
                else:
                    try:
                        await self.__QQbot__.send_group_msg_rate_limited(group_id=869494996, message='020支付接口返回错误：' + repr(r))
                    except ActionFailed as e:
                        print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
                    return None

