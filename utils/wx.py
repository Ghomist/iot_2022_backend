import requests
import json
import asyncio
import websockets
from threading import Thread

from config import (wx_appid, wx_secret, websocket_ip, websocket_port)

import logging
logger = logging.getLogger(__name__)


def get_openid(code) -> None | dict:
    """
    通过小程序发来的 code 获取用户鉴权数据
    API: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
    """
    params = {
        'appid': wx_appid,
        'secret': wx_secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.get(url='https://api.weixin.qq.com/sns/jscode2session', params=params)
    response = json.loads(response.content.decode('utf-8'))

    err = response['errcode']
    msg = response['msg']
    if int(err) == 0:
        logger.info(f'User: "{code}" login')
    else:
        logger.error(f'"{msg}" with error code: "{err}"')
        response = None

    return response


ws_users = {}


def websocket_initialize():
    async def _register_(websocket):
        try:
            openid = await websocket.recv()
            logger.info(f'New websocket client({openid})')
            # await websocket.send(f'hello! {name}')

            _socket = ws_users.get(openid)
            if _socket:
                await _socket.close()

            ws_users[openid] = websocket
            logger.debug(ws_users)

            # keep alive
            await websocket.wait_closed()
        except OSError:
            logger.warning(f'Websocket client({openid}) disconnected')

    async def _server_():
        async with websockets.serve(_register_, websocket_ip, websocket_port):
            await asyncio.Future()  # run forever

    def run_server():
        asyncio.run(_server_())

    Thread(target=run_server).start()


def websocket_info(openid, msg):
    async def _info_(openid, msg):
        websocket = ws_users.get(openid, None)
        if not websocket:
            logger.error(f'No found client when info to {openid}')
            logger.debug(ws_users)
            return

        await websocket.send(msg)
        logger.info(f'Info to websocket client({openid})')

    asyncio.run(_info_(openid, msg))
