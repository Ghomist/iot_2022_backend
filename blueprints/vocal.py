import json
import requests
import base64
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from blueprints import order

from config import sis_api_host, sis_dialect
from utils import hw, iot_cmd

import logging
logger = logging.getLogger(__name__)

bp = Blueprint('vocal_cmd', __name__, url_prefix='/vocal')


def _parse_text_(aac_base64_data) -> (str, str, int):
    ret = '', '', -1
    # scan every dialect
    for dialect in sis_dialect:
        header = {'X-Auth-Token': auth.get_token(), 'Content-Type': 'application/json'}
        data = {
            'config': {
                'property': f'{dialect}_16k_common',
                'audio_format': 'aac',
            },
            # 'data': str(base64.b64encode(bytes(vocal.encode())), 'utf-8')
            'data': aac_base64_data
        }
        response = requests.post(url=sis_api_host, headers=header, data=json.dumps(data))

        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            data = data['result']
            score = data['score']
            if score > ret[2]:
                ret = dialect, data['text'], score
        else:
            logger.error('SIS aac parse error')
            logger.debug(response.content)
            return ret

    return ret


@bp.route('/upload', methods=['POST'])
def upload():
    # print(request.form)
    vocal = request.form['vocal']
    dialect, text, score = _parse_text_(vocal)
    if text and score != -1:
        data = {
            'dialect': dialect,
            'text': text,
            'score': score
        }
        logger.debug(data)

        if '下单充电' in text:
            command.book('bear-esp')
            command.lock_open('bear-esp')
            command.power_on('bear-esp', 'test')
        elif '下单' in text:
            command.book('bear-esp')
        elif '结束' in text or '停止' in text:
            command.power_off('bear-esp', 'test')
            command.lock_open('bear-esp')
        elif '开始' in text:
            command.lock_open('bear-esp')
            command.power_on('bear-esp', 'test')

        return json.dumps(data), 200
    else:
        return '', 400
