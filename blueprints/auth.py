import json
from flask import Blueprint

import utils.db as db
from utils import wx


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/<code>', methods=['GET'])
def get_openid(code):
    data = wx.get_openid(code)

    if not data:
        return data, 400

    openid = data['openid']

    if not db.add_user(openid):
        pass

    return json.dumps({'openid': openid}), 200
