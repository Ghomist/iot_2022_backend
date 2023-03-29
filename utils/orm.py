import globe
from config import (mysql_database, mysql_host, mysql_port, mysql_protocol, mysql_pwd, mysql_usr)
from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Column, Integer, String, Float, Boolean, DateTime)
import datetime
import json
import logging
logger = logging.getLogger(__name__)


# 先建好 flask 全局变量！
if not hasattr(globe, 'db_init') or globe.db_init == False:
    globe.db_init = True

    app = globe.app
    app.config['SECRET_KEY'] = 'root'  # 安全密码
    app.config['SQLALCHEMY_DATABASE_URI'] = f'{mysql_protocol}://{mysql_usr}:{mysql_pwd}@{mysql_host}:{mysql_port}/{mysql_database}'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 该字段增加了开销，设为 False 可以减小开销

    db = SQLAlchemy(app)
    logger.info('Database init done')


class Pile(db.Model):
    __tablename__ = 'piles'

    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), nullable=False, unique=True, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    state = Column(Integer)

    def get_location(self) -> tuple:
        return self.longitude, self.latitude

    def __repr__(self):
        return '<User %r>' % self.username


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    uid = Column(String(64), nullable=False, unique=True, index=True)

    def __repr__(self):
        return '<User %r>' % self.username


class Order(db.Model):
    __tablename__ = 'orders'  # 表名

    # init
    id = Column(Integer, primary_key=True)
    oid = Column(String(64), nullable=False, index=True, unique=True)
    owner = Column(String(64), nullable=False, index=True)
    device = Column(String(64), nullable=False, index=True)
    book_time = Column(DateTime, nullable=False, default=datetime.datetime.fromtimestamp(0))

    # mode
    smart = Column(Boolean)

    # started
    start = Column(Boolean, nullable=False, default=False)
    start_time = Column(DateTime, default=datetime.datetime.fromtimestamp(0))

    # finished
    end = Column(Boolean, nullable=False, default=False)
    end_time = Column(DateTime, default=datetime.datetime.fromtimestamp(0))

    # set when finished
    energy = Column(Float, default=0)
    payments = Column(Float, default=0)
    data_file = Column(String(64))

    # owner = sql.relationship('User', backref='order', lazy='dynamic')  # 外键关系，动态更新

    def to_json(self) -> dict:
        if self.end:
            charging_time = (self.end_time-self.start_time).seconds
            _state_ = 'finished'
        elif self.start:
            charging_time = (datetime.datetime.now()-self.start_time).seconds
            _state_ = 'charging'
        else:
            charging_time = 'NaN'
            _state_ = 'booked'
        return {
            'oid': self.oid,
            'device': self.device,
            'state': _state_,
            'book_time': str(self.book_time),
            'start_time': str(self.start_time) if self.start else 'NaN',
            'end_time': str(self.end_time) if self.end else 'NaN',
            'charging_time': charging_time,
            'energy': self.energy,
            'payments': self.payments
            # 'exception': self.exception,
            # 'detect': self.detect
        }

    def __repr__(self):
        return f'<Order {self.owner} ({self.oid})>'


# 每次重启都会清空数据库
try:
    User.__table__.drop(db.get_engine())
except:
    pass
try:
    Order.__table__.drop(db.get_engine())
except:
    pass
# db.drop_all()
db.create_all()
# clean_data()
