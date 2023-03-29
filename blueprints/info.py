from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from utils import db
import json

bp = Blueprint('info', __name__, url_prefix='/info')


@bp.route('/get_piles')
def get_piles():
    # from database.db import Pile
    ret = []
    for pile in db.get_all_piles():
        # pile: Pile
        ret.append({
            'id': pile.device_id,
            'longitude': pile.longitude,
            'latitude': pile.latitude
        })
    return json.dumps(ret), 200
