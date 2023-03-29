'''
**本文件为配置示例，不会被项目读取！**
使用时请先将本文件复制一份并改名为 config.py
然后在新文件中填好所有为 None 的项即可使用

特别注意不是 None 的项可能也需要根据你的环境配置灵活改动
这些项为 None 的主要原因是涉及私人信息/隐私泄露
'''

# 本文件存放整个项目的独立配置

# Flask 配置
flask_listen_ip = '0.0.0.0'  # 本地测试时可以改成 localhost
flask_listen_port = 8876
flask_debug_mode = True
flask_use_reloader = False  # 使用 websocket 时不可开启

# MySQL 配置
mysql_protocol = 'mysql+pymysql'
mysql_usr = 'm'
mysql_pwd = None
mysql_host = 'localhost'
mysql_port = '3306'
mysql_database = None  # 数据库需提前建好

# 微信开发者配置
wx_appid = None  # 微信小程序的 APPID
wx_secret = None  # 微信开发者密钥

# 华为开发者配置
hw_iam_user = None  # IAM用户名
hw_iam_pwd = None  # 华为云登录密码
hw_account = None  # 账号名
hw_project_scope = 'cn-north-4'
hw_token_url = 'https://iam.cn-north-4.myhuaweicloud.com/v3/auth/tokens'
hw_token_alive = 20*60*60  # 超过这个时间才会申请新 token   TODO: 可能没有效果

# IoTDA 设置
iot_project_id = None
iot_device_id = None
iot_api_host = 'a16236a40f.iotda.cn-north-4.myhuaweicloud.com'

# websocket 配置
websocket_ip = '0.0.0.0'
websocket_port = 8877

# SIS
# 语音识别的具体指令需要到 blueprints/vocal.py 里面自行更改
sis_project_id = None
sis_api_host = f"https://sis-ext.cn-north-4.myhuaweicloud.com/v1/{sis_project_id}/asr/short-audio"
sis_dialect = ('chinese', 'cantonese')  # Also available: 'sichuan', 'shanghai'

# 开启京东爬虫和商城系统
enable_jd_crawler = True
