import json
from random import random
import requests
import bs4
import re
import time
import math
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

bp = Blueprint('shop', __name__, url_prefix='/shop')


@bp.route('/search/<key>')
def search(key):
    goods = search_goods(key, 1)
    goods = json.dumps(goods, ensure_ascii=False)
    return goods, 200


def get_good_info(item_url, session=None) -> dict:
    """
    获取商品信息
    Parameters:
            item_url - 物品链接
    """
    item_url = 'http:' + item_url
    return {"url": item_url}
    if session:
        response = session.get(item_url, timeout=0.5)
    else:
        response = requests.get(item_url, timeout=0.5)
    response.encoding = 'utf-8'
    page = bs4.BeautifulSoup(response.text, 'lxml')  # spec-img
    img_url = 'http:' + page.find('img', id='spec-img')['data-origin']
    try:
        name = page.find('div', class_='sku-name').string.lstrip().rstrip()
    except:
        # print('ERR: http:'+item_url)
        # print(page.find('div', class_='sku-name'))
        name = str(page.find('div', class_='sku-name'))
        name = re.findall('>\s*(.*)\s*<', name)[-1].lstrip().rstrip()

    # print(page.find('span', class_='price'))
    return {
        'url': item_url,
        'img_url': img_url,
        'name': name
    }


def search_goods(keyword, pages) -> list:
    """
    搜索商品
    Parameters:
            keyword - str 搜索关键词
            pages - int 搜索页数
    Returns:
            goods_urls - list 商品链接
    """
    # 创建 session
    sess = requests.Session()
    goods = {}
    for page in range(pages):
        # 第一次加载
        search_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
            'Host': 'search.jd.com'
        }
        s = page*28
        if s == 0:
            s = 1
        # 搜索url
        search_url = 'https://search.jd.com/Search'
        search_params = {
            'keyword': keyword,
            'enc': 'utf-8',
            'qrst': '1',
            'rt': '1',
            'stop': '1',
            'vt': '2',
            'wq': keyword,
            'stock': '1',
            'page': page*2+1,
            's': s,
            'click': '0'
        }
        search_req = sess.get(url=search_url, params=search_params, headers=search_headers, verify=False)
        search_req.encoding = 'utf-8'
        search_req_bf = bs4.BeautifulSoup(search_req.text, 'lxml')
        for item in search_req_bf.find_all('div', class_='gl-i-wrap'):
            # 链接
            item_url = item.div.a.get('href')
            # 滤除广告
            if 'ccc-x.jd.com' in item_url:
                continue
            # 防止重复
            if goods.get(item_url):
                continue
            # 进入页面获取商品信息
            good_info = get_good_info(item_url, sess)
            if good_info:
                goods[item_url] = good_info
                good_info['unit_name'] = '件'
                good_info['sales'] = int(random()*250+50)
            # 获取粗略的价格
            for content in item.contents:
                if hasattr(content, 'get'):
                    c = content.get('class')
                    if not c:
                        continue
                    if 'p-price' in c:
                        # price = f'{content.strong.em.string}{content.strong.i.string}'
                        price = float(content.strong.i.string)
                        good_info['price'] = price
                        good_info['vip_price'] = float(f'{price*(random()/3+0.6):.2f}')
                    elif 'p-img' in c:
                        data_original = content.a.img.get('data-lazy-img')
                        img_url = 'http:' + data_original
                        good_info['image'] = img_url
                        # print(img_url)
                    elif 'p-name' in c:
                        name = ''
                        for s in content.a.strings:
                            name += s
                        name = name.lstrip().rstrip()
                        good_info['store_name'] = name
        # 继续加载log_id
        log_id = re.findall("log_id:'(.*)',", search_req.text)[0]

    return list(goods.values())

    for page in range(pages):
        # 第二次加载
        # 继续加载url
        search_more_url = 'https://search.jd.com/s_new.php'
        search_more_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
            'Host': 'search.jd.com',
            'Referer': search_req.url
        }
        s = (1+page)*25
        search_more_params = {
            'keyword': keyword,
            'enc': 'utf-8',
            'qrst': '1',
            'rt': '1',
            'stop': '1',
            'vt': '2',
            'wq': keyword,
            'stock': '1',
            'page': (1+page)*2,
            's': s,
            'log_id': log_id,
            'scrolling': 'y',
            'tpl': '1_M'
        }
        search_more_req = sess.get(url=search_more_url, params=search_more_params, headers=search_more_headers, verify=False)
        search_more_req.encoding = 'utf-8'
        # 匹配商品链接
        search_more_req_bf = bs4.BeautifulSoup(search_more_req.text, 'lxml')
        for item in search_more_req_bf.find_all('li', class_='gl-item'):
            # 链接
            item_url = item.div.a.get('href')
            # 滤除广告
            if 'ccc-x.jd.com' in item_url:
                continue
            # 防止重复
            if goods.get(item_url):
                continue
            # 获取粗略的价格
            price = "undefined"
            for content in item.contents:
                if hasattr(content, 'get'):
                    c = content.get('class')
                    if not c:
                        continue
                    if 'p-price' in c:
                        price = f'{content.strong.em.string}{content.strong.i.string}'
            # 进入页面获取商品信息
            good_info = get_good_info(item_url, sess)
            if good_info:
                good_info['price'] = price
                goods[item_url] = good_info
    # 去重
    # goods_urls = list(set(goods_urls))
    # 链接合成
    # goods_urls = list(map(lambda x: 'http:'+x, goods_urls))
    return list(goods.values())
    # return goods_urls


def goods_comments(goods_url):
    """
    获得商品评论
    Parameters:
            goods_url - str 商品链接
    Returns:
            image_urls - list 评论
    """
    image_urls = []
    product_id = goods_url.split('/')[-1].split('.')[0]

    # 评论url
    comment_url = 'https://sclub.jd.com/comment/productPageComments.action'
    comment_params = {
        'callback': 'fetchJSON_comment98',
        'productId': product_id,
        'score': '0',
        'sortType': '5',
        'page': '0',
        'pageSize': '10',
        'isShadowSku': '0',
        'fold': '1'
    }
    comment_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        # 'Referer': goods_url,
        'Referer': 'https://item.jd.com/',
        'Host': 'sclub.jd.com',
        'cache-control': 'no-cache'
    }

    comment_req = requests.get(url=comment_url, params=comment_params, headers=comment_headers, verify=False)
    # html = json.loads(comment_req.text)
    print(goods_url, end=': ')
    # print(comment_req.status_code)
    print(comment_req.text)
    # # 获得晒图个数
    # imageListCount = html['imageListCount']
    # # 计算晒图页数,向上取整
    # pages = math.ceil(imageListCount / 10)
    # for page in range(1, pages+1):
    #     # 获取晒图图片url
    #     club_url = 'https://club.jd.com/discussion/getProductPageImageCommentList.action'
    #     now = time.time()
    #     now_str = str(now).split('.')
    #     now = now_str[0] + now_str[-1][:3]
    #     club_params = {'productId': product_id,
    #                    'isShadowSku': '0',
    #                    'page': page,
    #                    'pageSize': '10',
    #                    '_': now}
    #     club_headers = comment_headers
    #     club_req = requests.get(url=club_url, params=club_params, headers=club_headers, verify=False)
    #     html = json.loads(club_req.text)
    #     for img in html['imgComments']['imgList']:
    #         image_urls.append(img['imageUrl'])
    # # 去重
    # image_urls = list(set(image_urls))
    # # 链接合成
    # image_urls = list(map(lambda x: 'http:'+x, image_urls))

    # return image_urls


# a = get_good_info('//item.jd.com/100005312811.html')

if __name__ == '__main__':
    goods = search_goods('电动自行车配件', 1)

    for good in goods:
        goods_comments(good['url'])

    goods = json.dumps(
        # json文件-dict
        goods,
        # 缩进显示
        indent=4,
        # 排序 a-z
        sort_keys=True,
        # 防止中文乱码
        ensure_ascii=False,
        # #去掉‘，’和‘：’的前后空格。打印以方便阅读时不建议使用
        #separators=(',', ':')
    )

    # print(goods)
