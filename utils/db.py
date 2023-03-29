import logging
from utils.orm import (Pile, User, Order)
from utils.orm import db
logger = logging.getLogger(__name__)


def get_user_by_uid(uid):
    '''
    使用 uid 获取用户
    '''
    return User.query.filter_by(uid=uid).first()


def add_user(uid) -> bool:
    '''
    为数据库初始化新用户
    '''
    _usr_ = get_user_by_uid(uid)
    if not _usr_:
        user = User(id=None, uid=uid)
        db.session.add(user)
        db.session.commit()
        logger.info(f'New user: {uid}')
        return True
    else:
        # logger.info(f'User {uid} has been exist')
        return False


def get_order_by_oid(oid) -> Order:
    return Order.query.filter_by(oid=oid).first()


def get_active_order_by_oid(oid) -> None | Order:
    order = get_order_by_oid(oid)
    if not order or order.end:
        return None
    else:
        return order


def get_active_order_by_device(device) -> Order:
    return Order.query.filter_by(device=device, end=False).first()


def get_all_order_by_owner(owner) -> list[Order]:
    return Order.query.filter_by(owner=owner).all()


def stop_order(oid):
    order = get_order_by_oid(oid)
    if not order:
        logger.info(f'No found order({oid}) when stop_order')
        return
    if order.start:
        logger.info(f'Stop order({oid})')
        order.end = True
        order.end_time = datetime.datetime.now()
        # order.energy = energy
        order.data_file = f'./data/{order.oid}.json'
        db.session.commit()
    else:
        pass
        # logger.debug('order cancel')


def set_order_energy(oid, energy):
    order = get_order_by_oid(oid)
    if not order:
        logger.error(f'No found order({oid}) when set_order_nrg')
        return
    if order.start:
        order.energy = energy
        db.session.commit()
    else:
        pass
        # logger.debug('order cancel')


def update_pile(id, longi, lati):
    '''
    更新充电桩的地理位置
    '''
    pile: Pile = Pile.query.filter_by(device_id=id).first()
    if not pile:
        db.session.add(Pile(
            device_id=id,
            longitude=longi,
            latitude=lati,
        ))
        db.session.commit()
    else:
        pile.longitude = longi
        pile.latitude = lati
        db.session.commit()


def get_all_piles():
    return Pile.query.all()
