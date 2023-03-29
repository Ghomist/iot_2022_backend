from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import json
from utils import db, iot_cmd, wx
import logging
logger = logging.getLogger(__name__)

bp = Blueprint('charge_data', __name__, url_prefix='/charge')


@bp.route('/up_data', methods=['POST'])
def upload_data():
    """
    订单结束，充电数据上传
    """
    data = request.get_json()
    data = data['notify_data']['body']['content']
    if not data:
        logger.error('Receive data error')
        return '', 400

    device_id = data['id']
    oid = data['oid']
    logger.info(f'Receive charge data from device({device_id}) of order {oid}')

    with open(f'./data/{oid}.json', 'w+') as f:
        json.dump(data, f)
        logger.info(f'Data from device({device_id}) saved')

    return '', 200


@bp.route('/up_msg', methods=['POST'])
def at_warning():
    """
    设备消息上报
    """
    data = request.get_json()
    data = data['notify_data']['body']['content']
    if not data:
        logger.error('Receive message error')

    msg = data['msg']
    device_id = data['id']

    if msg == 'upload_location':
        logger.info(f'Receive position of device({device_id})')
        db.update_pile(device_id, data['longi'], data['lati'])
        return '', 200

    order = db.get_active_order_by_device(device_id)
    if msg == 'login':
        if order:
            iot_cmd.power_on_delay(device_id, order.oid, 5)
            logger.info(f'Device({device_id}) login, power on later')
        else:
            logger.warning(f'Device({device_id}) login, no order found')
        return '', 200

    logger.debug(msg)
    if not order:
        logger.error(f'No order found of device({device_id})')
        return '', 400

    if msg == 'smoke':
        iot_cmd.power_off(device_id, order.oid)
    elif msg == 'undetected':
        pass
    elif msg == 'finished':
        iot_cmd.power_off(device_id, order.oid)
    elif msg == 'overload':
        iot_cmd.power_off(device_id, order.oid)

    wx.websocket_info(order.owner, msg)
    return '', 200


@bp.route('/get/data', methods=['POST'])
def get_data():
    '''
    获取某次订单的充电数据
    '''
    # 默认直接返回预制的数据 json，后面注释掉的是根据数据库索引到真正的数据（不确保能用）
    return open('./data/esp-default.json').read(), 200
    # if not request.form.get('oid'):
    #     print('no oid in charge data request')
    #     return '{"err":"no oid in charge_data request"}', 400
    # oid = request.form['oid']
    # order = db.get_order_by_oid(oid)
    # if not order:
    #     print(f'no found of {oid}')
    #     return '', 400
    # data_file = order.data_file
    # try:
    #     with open(data_file) as f:
    # return f.read(), 200
    # except:
    #     print(f'file no found({oid}), return default')
    #     return open('./data/esp-std.json').read(), 200


@bp.route('/get/energy', methods=['POST'])
def get_energy():
    '''
    获取用电量以及电费
    '''
    response = iot_cmd.get_energy()
    response['properties']['cost'] = response['properties']['value']*0.6  # 此处电费单价写死 0.6，实际上应该动态获取
    response['properties']['cost_per_mAh'] = 0.6
    return json.dumps(response)
