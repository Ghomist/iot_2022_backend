from flask import Flask
import logging

import globe
from config import (
    flask_listen_ip, flask_listen_port, flask_debug_mode, flask_use_reloader, enable_jd_crawler
)

import logging
logger = logging.getLogger(__name__)


def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    import os, json
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def get_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)

    if test_config is None:
        # Load the instance config
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config
        app.config.from_mapping(test_config)

    # make globe var (app)
    globe.app = app

    with app.app_context():
        # init database orm
        import utils.orm

        # init websocket
        from utils import wx
        wx.websocket_initialize()

    # register blueprint
    from blueprints import (auth, charge, info, order, vocal)
    app.register_blueprint(auth.bp)
    app.register_blueprint(charge.bp)
    app.register_blueprint(info.bp)
    app.register_blueprint(order.bp)
    app.register_blueprint(vocal.bp)
    if enable_jd_crawler:
        from blueprints import shop
        app.register_blueprint(shop.bp)  # 商城（京东爬虫）

    # Test print
    logger.info('Flaskr is running!')

    return app


if __name__ == '__main__':
    app = get_app()

    # Test page
    @app.route('/hello')
    def hello():
        return 'Hello, Flaskr!'

    # run flask
    app.run(
        host=flask_listen_ip,
        port=flask_listen_port,
        debug=flask_debug_mode,
        use_reloader=flask_use_reloader
    )
