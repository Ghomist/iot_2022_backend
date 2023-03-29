import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from utils import db, iot_cmd

import logging
logger = logging.getLogger(__name__)

bp = Blueprint('order', __name__, url_prefix='/order')


@bp.route('/book', methods=['POST'])
def book():
    # logger.debug(request.form)
    openid = request.form['openid']
    device = request.form['device']
    oid = db.add_order(openid, device)
    if oid:
        iot_cmd.book(device)
        logger.info(f'Booked for device({device})')
        return json.dumps({'oid': oid}), 200
    else:
        return '', 400


@bp.route('/start', methods=['POST'])
def start():
    oid = request.form['oid']
    charge_type = request.form['type']
    if db.start_order(oid, charge_type):
        order = db.get_active_order_by_oid(oid)
        iot_cmd.lock_open(order.device)
        iot_cmd.power_on(order.device, order.oid)
        logger.info(f'Start order({oid}))')
        return '', 200
    else:
        return '', 400


@bp.route('/get', methods=['POST'])
def get():
    oid = request.form['oid']

    order = db.get_order_by_oid(oid)
    if not order:
        return '{"err":"NO ORDER FOUND"}', 400

    return json.dumps(order.to_json()), 200


@bp.route('/get_all', methods=['POST'])
def get_all():
    openid = request.form['openid']

    booked_list = []
    history_list = []
    charging_list = []

    for order in db.get_all_order_by_owner(openid):
        order_data = order.to_json()
        if order.end:
            history_list.append(order_data)
        elif order.start:
            charging_list.append(order_data)
        else:
            booked_list.append(order_data)

    return json.dumps({
        'booked': booked_list,
        'charging': charging_list,
        'history': history_list
    }), 200


@bp.route('/stop', methods=['POST'])
def cancel():
    # oid = request.form['oid']
    order = db.get_active_order_by_device('bear-esp')  # 此处应该用 order id 进行搜索 & 判断，这里是为了省事
    # order = db.get_active_order_by_oid(oid)
    if not order:
        return '{"err":"NO ORDER FOUND"}', 400

    iot_cmd.lock_open(order.device)
    if order.start:
        iot_cmd.power_off(order.device, order.oid)

    db.stop_order(order.oid)
    nrg_rpt = iot_cmd.get_energy()
    energy = nrg_rpt['properties']['value']
    db.set_order_energy(order.oid, energy)
    return '', 200
