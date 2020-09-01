# -*- coding:UTF-8 -*-
import datetime
import os
import re
import threading
import time
from base64 import b64encode
from threading import Thread
import redis
import requests
import json
from Newslive.lib.lib_args.redis_connect import redis_host, password
from Newslive.utils.logging import logger

tag_obj = {'0': '全部', '10': 'A股', '1': '宏观', '2': '行业', '3': '公司', '4': '数据', '5': '市场', '6': '观点', '7': '央行',
           '8': '其他'}

base_url = 'http://zhibo.sina.com.cn/api/zhibo/feed?&page=1&page_size=5&zhibo_id=152&tag_id='
now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

redis_setting = {
    "host": redis_host,
    "port": 6379,
    "password": password,
    "db": 0,
    "decode_responses": True
}


# 异步调用
def async_func(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


# 新线程
def request_main_task():
    threading.Thread(target=request_main).start()


def detele_redis_task(tag_id):
    threading.Thread(target=delete_redis(tag_id)).start()


# 请求接口数据
def requests_live_data(tag_id):
    try:
        url = base_url + str(tag_id)
        s = requests.session()
        s.keep_alive = False
        response = s.get(url=url, timeout=5)
        # 获取接口对象
        obj_data_list = response.json()['result']['data']['feed']['list']
        # print(obj_data_list)
        for obj_data in obj_data_list:
            theme_id = obj_data['id']
            theme_time = obj_data['create_time']
            rich_text = obj_data['rich_text']

            # 如果为新浪广告
            if del_theme(rich_text):
                continue

            img_text = obj_data['multimedia']
            # 判断是否有图片
            if img_text:
                # 有图片，请求图片数据
                img = True
                img_url = img_text['img_url'][0].replace('\\', '')
                img_data = get_img_data(img_url, theme_id, 'save')
            else:
                img_data = ''
                img = False
            context = {}
            context['theme_id'] = str(theme_id)
            context['tag_id'] = str(tag_id)
            context['theme_time'] = theme_time
            context['rich_text'] = rich_text
            context['img'] = img
            context['img_data'] = img_data

            # print(context)
            data_key = f'newslive:tag_id:{str(tag_id)}'
            # 放入缓存
            save_redis(data_key, context)
    except Exception as e:
        print(e)
        logger.error(f'requests_live_data: {e}, time:{now_time}')


def del_theme(text):
    if re.search('新浪', text) != None:
        return True


# 保存图片数据
def get_img_data(url, id, method):
    try:
        if method == 'save':
            response = requests.get(url=url, timeout=5)
            file = f'/static/img_live/{id}.jpg'
            f = open(r'Newslive/static/img_live/%s.jpg' % id, 'ab')  # 存储图片，多媒体文件需要参数b（二进制文件）
            # f = open(r'../../static/img_live/%s.jpg' % id, 'ab')  # 存储图片，多媒体文件需要参数b（二进制文件）
            f.write(response.content)  # 多媒体存储content
            f.close()
            return file
        else:
            # b64
            f = open(r'Newslive/static/img_live/%s.jpg' % id, 'rb')  # 图片，多媒体文件需要参数b（二进制文件）
            # f = open(r'../../static/img_live/%s.jpg' % id, 'rb')  # 存储图片，多媒体文件需要参数b（二进制文件）
            f_data = f.read()  # 多媒体存储content
            img_str = b64encode(f_data).decode('utf-8')
            f.close()
            return img_str
    except Exception as e:
        print(e)
        logger.error(f'get_img_data: {e}, time:{now_time}')


# 放入缓存
def save_redis(key, value):
    try:
        conn = redis.Redis(host=redis_setting['host'],
                           port=redis_setting['port'],
                           password=redis_setting['password'],
                           db=redis_setting['db'],
                           decode_responses=redis_setting['decode_responses'])
        # for str_value in list(conn.smembers(key)):
        #     value_obj = eval(str_value)
        #     if value_obj['rich_text'] == value['rich_text']:
        #         return
        conn.sadd(key, str(value))  # 172800
        conn.close()
    except Exception as e:
        print(e)
        logger.error(f'save_redis: {e}, time:{now_time}')


def delete_redis(tag_id):
    try:
        data_list = []
        key = f'newslive:tag_id:{str(tag_id)}'
        conn = redis.Redis(host=redis_setting['host'],
                           port=redis_setting['port'],
                           password=redis_setting['password'],
                           db=redis_setting['db'],
                           decode_responses=redis_setting['decode_responses'])
        for value in list(conn.smembers(key)):
            value_obj = eval(value)
            data_list.append(value_obj)

        # 获取今昨时间
        today = datetime.date.today()  # 当前日期
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        time_list = [str(today), str(yesterday)]

        if data_list != []:
            for data in data_list:
                time = data['theme_time'].split(' ')[0]
                theme_id = data['theme_id']
                # 时间时间是否在list中
                if time not in time_list:
                    if conn.sismember(key, str(data)):
                        conn.srem(key, str(data))
                        # print(str(data))
                        # 删除图片
                        delete_img(theme_id)
        conn.close()
    except Exception as e:
        print(e)
        logger.error(f'delete_redis: {e}, time:{now_time}')


def delete_img(theme_id):
    try:
        path = 'Newslive/static/img_live/%s.jpg' % theme_id
        # path = '../../static/img_live/%s.jpg' % theme_id
        os.remove(path)
        # print('已删除：%s' % path)
    except Exception as e:
        print(e)
        logger.error(f'delete_img: {e}, time:{now_time}')


# 缓存读取数据
def read_redis(tag_id, theme_id, type_method):
    try:
        data = {"list": []}
        key = f'newslive:tag_id:{str(tag_id)}'
        conn = redis.Redis(host=redis_setting['host'],
                           port=redis_setting['port'],
                           password=redis_setting['password'],
                           db=redis_setting['db'],
                           decode_responses=redis_setting['decode_responses'])
        for value in list(conn.smembers(key)):
            value_obj = eval(value)
            # 暂时用 图片路径，咱不用 B 64
            # if value_obj['img']:
            #     img_data = get_img_data('', value_obj['theme_id'], 'read')
            #     value_obj['img_data'] = img_data
            # else:
            #     value_obj['img_data'] = ''
            data['list'].append(value_obj)
        sort_data = sorted(data['list'], key=lambda i: i['theme_time'], reverse=True)

        # 清除新增
        if theme_id != None and type_method == 'all':
            for i in range(0, len(sort_data)):
                if sort_data[i]['theme_id'] != theme_id:
                    sort_data.pop(i)
                else:
                    break

        if theme_id != None and type_method == 'update':
            list_1 = []
            for i in range(0, len(sort_data)):
                if int(sort_data[i]['theme_id']) > int(theme_id):
                    list_1.append(sort_data[i])
                else:
                    break
            sort_data = sorted(list_1, key=lambda i: i['theme_time'], reverse=True)
        data = {'list': sort_data}
        # print(data)
        conn.close()
        return data
    except Exception as e:
        print(e)
        logger.error(f'read_redis: {e}, time:{now_time}')


def request_main():
    while True:
        # print(now_time)
        for tag_id in tag_obj.keys():
            # 清除缓存
            if str(datetime.datetime.now()).split(' ')[1].split('.')[0].split(':')[0] + ':' + \
                    str(datetime.datetime.now()).split(' ')[1].split('.')[0].split(':')[1] == '23:00':
                try:
                    detele_redis_task(tag_id)
                except Exception as e:
                    print(e)
                    logger.error(f'detele_redis_task: {e}, time:{now_time}')
            try:
                requests_live_data(tag_id)
            except Exception as e:
                print(e)
                logger.error(f'requests_live_data: {e}, time:{now_time}')
        time.sleep(60)


if __name__ == '__main__':
    # requests_live_data('5')
    request_main_task()
    # delete_redis('7')
    # delete_img('1802625')
