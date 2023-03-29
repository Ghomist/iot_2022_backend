# 充电桩项目后端

## 环境配置

### config.py

配置文件仓库里只给出了示例：[config_example.py](./config_example.py)，开始使用前请记得把配置项补充完整

### MySQL

首先安装 MySQL，并注册好用户，默认的用户配置在 `config.py` 文件中，内容如下：

```python
# MySQL 配置示例
mysql_usr = 'm'
mysql_pwd = 'Test_8876'
mysql_port = '3306'
mysql_database = 'test'  # 数据库需提前建好
```

若你的 MySQL 配置与该配置不一样，请自行修改 `config.py` 中的配置项

特别注意，`mysql_database` 所指向的数据库需要提前建好，里面可以没有任何 table

如果出现报错：`"Can't connect to MySQL server on 'localhost' ([Errno 111] Connection refused)"`，可以尝试重启 mysql 服务

```shell
$ sudo service mysql restart
```

### pip

安装以下 pip 包

```shell
$ pip install requests flask flask_sqlalchemy pymysql websockets
```

若启用京东商城的话则需要安装：

```shell
$ pip install bs4
```

若下载时出现错误可尝试为 pip 换源，具体方法网上很多，恕不赘述

## 使用

### screen

Screen 是一个将命令行程序设置到后台运行的命令行程序。因为大部分命令行程序在开启之后会霸占掉终端，无法执行其它指令。若需要执行别的指令，则需开新的终端窗口。此时若不慎关闭原来的终端窗口，后续便没有办法再通过终端控制该程序了，只能使用强制关闭（kill 等指令）的方式结束程序

而 screen 正是为了解决这个问题，为了让用户可以在一个终端窗口内控制多个程序（特别是需要长期保持运行、需要实时监控的程序，如服务器后台）

虽然非必须，但**强烈建议将本后端（以及任何持久运行的命令行程序）开到 screen 当中运行**

简单的用法如下：

```shell
$ screen -S xxx     # 创建一个名为 xxx 的后台窗口
$ screen -r xxx     # 回到名为 xxx 的后台窗口
$ screen -r -d xxx  # 强制回到名为 xxx 的后台窗口并把其他在此窗口的用户踢掉
```

进入 screen 后的界面和普通的终端无异，但是无法使用鼠标滚轮上下翻页

部分 screen 内使用的快捷键如下：

-   `ctrl` + `D` 退出并关闭 screen
-   `ctrl` + `A` + `D` 退出但不关闭 screen
-   `ctrl` + `A` + `Esc` 进入复制模式（可以使用`↑` `↓`实现向前翻页），按两次 `Enter` 退出

其余快捷键和用法建议自行上网学习

### 启动服务器

若要外部设备能访问到该程序，需要先在防火墙中将端口开放，默认的端口号为 8876，可在配置脚本当中修改

启动时使用如下指令

```shell
$ cd path/to/root/folder
$ python main.py
```

### 其它问题

正常来说，关掉服务器需要按两次 `ctrl+c`，是为了关闭 websocket 所在的线程以及主线程

若还有其它问题请交 issue