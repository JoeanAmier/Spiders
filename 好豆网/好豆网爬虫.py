# Author_QQ：2437596031
try:
    from requests_html import HTMLSession
    import time
    import pymysql
    import json
    import re
    import random
    import os
    import hashlib
    import copy
    from urllib.parse import quote
except ModuleNotFoundError as e:
    print('导入模块失败，请安装对应模块后再运行\n', e)
    exit()


class Config:
    config_file = 'config_file.json'
    default = {
        "MySQL": {"host": "",
                  "user": "",
                  "password": ""},
        "Progress": {"type": 0,
                     "page": 0},
        "Tasks": [
            ['type_url', 'type_name', 'start_page', 'end_page']
        ]
    }

    def __init__(self):
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.default))
            print('已生成配置文件：config_file.json\nTasks 格式：[爬取链接, 类型, 起始页数, 结束页数]')
            self.mysql = None
            self.progress = None
            self.tasks = None
        else:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                try:
                    self.config = json.load(f)
                    self.config_new = copy.deepcopy(self.config)
                except json.decoder.JSONDecodeError:
                    print(self.config_file, '格式错误！')
                    exit()
            self.mysql = self.config['MySQL']
            self.progress = self.config['Progress']
            self.tasks = self.config['Tasks']

    def new_config(self):
        return self.config_new

    def get_config(self):
        return self.mysql, self.progress, self.tasks, self.tasks_length

    def check_all(self):
        if None in [self.mysql, self.progress, self.tasks]:
            return False
        return False not in [
            self.check_mysql(),
            self.check_progress(),
            self.check_tasks(),
        ]

    def check_mysql(self):
        try:
            db = pymysql.connect(
                host=self.mysql['host'],
                user=self.mysql['user'],
                password=self.mysql['password'])
            db.close()
            return True
        except pymysql.err.OperationalError:
            print('连接数据库失败！')
            return False

    def check_progress(self):
        return isinstance(self.progress['type'], int) and isinstance(
            self.progress['page'], int
        )

    def check_tasks(self):
        for i in self.tasks:
            if not re.findall(
                    r'^https://www.haodou.com/recipe/all/\d+$',
                    i[0]):
                print('链接错误：', i)
                return False
            if not re.findall(r'^[\u4e00-\u9fa5]+$', i[1]):
                print('备注错误：', i)
                return False
            if not 1 <= i[2] <= 250:
                print('起始页数错误：', i)
                return False
            if not 1 <= i[3] <= 250:
                print('结束页数错误：', i)
                return False
            if i[2] > i[3]:
                print('起始页数大于结束页数：', i)
                return False
        return True

    @property
    def tasks_length(self):
        return len(self.tasks)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            f.write(json.dumps(self.config_new))
        print('配置文件已更新！\n未完成全部爬取任务前不要修改', self.config_file, '文件！')


class Database:
    db_name = 'haodouDB'
    sql = f"""create database IF NOT EXISTS {db_name} CHARACTER SET utf8mb4"""

    def __init__(self, mysql):
        self.mysql_db = pymysql.connect(
            host=mysql['host'],
            user=mysql['user'],
            password=mysql['password'])
        self.cursor = self.mysql_db.cursor()
        self.initial_db(mysql)

    def initial_db(self, mysql):
        self.cursor.execute(self.sql)
        self.mysql_db.commit()
        self.mysql_db.close()
        self.mysql_db = pymysql.connect(
            host=mysql['host'],
            user=mysql['user'],
            password=mysql['password'],
            db=self.db_name)
        self.cursor = self.mysql_db.cursor()

    def create_table(self):
        sql = """CREATE TABLE IF NOT EXISTS 好豆网数据(
        ID INTEGER primary key,
        链接 text not null,
        菜名 text not null,
        主料_1 text not null,
        主料_2 text,
        主料_3 text,
        主料_4 text,
        主料_5 text,
        主料_6 text,
        主料_7 text,
        主料_8 text,
        主料_9 text,
        主料_10 text,
        主料_11 text,
        主料_12 text,
        主料_13 text,
        主料_14 text,
        主料_15 text,
        主料_16 text,
        主料_17 text,
        主料_18 text,
        主料_19 text,
        主料_20 text,
        辅料 text not null,
        步骤 text not null,
        收藏 INTEGER not null,
        类型 text not null
        )"""
        self.cursor.execute(sql)
        self.mysql_db.commit()

    def insert_data(self, data):
        if not data:
            return
        sql = """insert ignore into 好豆网数据 values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(sql, data)
        self.mysql_db.commit()

    def __del__(self):
        self.mysql_db.close()
        print('数据库已关闭')


class Spider:
    base_url = 'https://www.haodou.com'
    ajax = 'https://vhop.haodou.com/hop/router/rest.json'
    headers_ajax = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'DNT': '1',
        'Host': 'vhop.haodou.com',
        'Origin': 'https://www.haodou.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.haodou.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.43'
                      '89.114 Safari/537.36 Edg/89.0.774.68'}
    headers_item = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,applicatio'
                  'n/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.haodou.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.haodou.com/recipe/all/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.43'
                      '89.114 Safari/537.36 Edg/89.0.774.68'}
    form_first = {
        '_HOP_': None,
        'from': 'mvue',
        'adcode': '100000',
        'appid': '100',
        'Siger': None,
        'uuid': '0',
        'uid': '0',
        'hduid': '0',
        'vc': '177',
        'vn': '1.0.0'}
    form_second = {'numbers': '[]',
                   'moduleId': '5d35709cfd96c61a103a13c2',
                   'id': None,
                   '_HOP_': None,
                   'from': 'mvue',
                   'adcode': '100000',
                   'appid': '100',
                   'Siger': None,
                   'uuid': '0',
                   'uid': '0',
                   'hduid': '0',
                   'vc': '177',
                   'vn': '1.0.0',
                   'last': None}

    class Parameter:

        @staticmethod
        def get_hop(time_, sign):
            return f'{{"version":"1.0.0","action":"api.www.recipe.category","secret_id":"5722f877e4b0d4512e3fd872","c' \
                   f'urrent_time":{time_},"sign":"{sign}"}}'

        @staticmethod
        def url_encode(text):
            return quote(text)

        @staticmethod
        def get_current_time():
            return str(time.time())[:10]

        def get_last(self, page, total):
            base = f'{{current:{page},total:{total},offset:{page * 40},limit:40}}'
            return self.url_encode(base)

        @staticmethod
        def get_sign(time_, siger_, last=None, id_=None):
            if last and id_:
                return (
                    f"Siger{siger_}_HOP_.actionapi.www.recipe.category_HOP_.current_time{time_}_HOP_.secret_id5722f"
                    f"877e4b0d4512e3fd872_HOP_.version1.0.0adcode100000appid100frommvuehduid0id{id_}last{last}mod"
                    f"uleId5d35709cfd96c61a103a13c2numbers%5B%5Duid0uuid0vc177vn1.0.01bc0d50feafb484b863d4100a561"
                    f"a9cf")

            else:
                return (
                    f"Siger{siger_}_HOP_.actionapi.www.search.default_HOP_.current_time{time_}_HOP_.secret_id5722f8"
                    f"77e4b0d4512e3fd872_HOP_.version1.0.0adcode100000appid100frommvuehduid0uid0uuid0vc177vn1.0.0"
                    f"1bc0d50feafb484b863d4100a561a9cf")

        @staticmethod
        def get_siger():
            return time.strftime("%Y%m%d")

    def __init__(self, progress, tasks, length):
        self.session = HTMLSession()
        self.type_ = progress['type']
        self.page = progress['page']
        self.tasks = tasks
        self.length = length
        self.parameter = self.Parameter()
        self.state = False
        self.last = None

    def open_url(self, url, id_, page):
        current = 1 if page < 2 else page - 1
        if not self.last or page == 1:
            html = self.get_last(url)
        if self.state:
            return ['0']
        if page == 1:
            print('获取菜品列表成功：', url, page)
            return [i.attrs['href'] for i in html.find('div > a.lists')]
        current_time = self.parameter.get_current_time()
        siger = self.md5(self.md5(self.parameter.get_siger()))
        last = '{{"current":{},"total":{},"offset":{},"limit":40}}'.format(
            current, self.last, (page - 1) * 40)
        sign = self.md5(
            self.parameter.get_sign(
                current_time,
                siger,
                self.parameter.url_encode(last),
                id_))
        hop = self.parameter.get_hop(current_time, sign)
        form = copy.deepcopy(self.form_second)
        form['id'] = id_
        form['Siger'] = siger
        form['_HOP_'] = hop
        form['last'] = last
        response = self.session.post(
            self.ajax, headers=self.headers_ajax, data=form)
        if response.status_code != 200:
            print('获取菜品列表失败：', url, page)
            self.state = True
            return ['0']
        self.wait()
        print('获取菜品列表成功：', url, page)
        return self.get_url(response.html.html)

    def get_html(self, url, id_):
        headers = copy.deepcopy(self.headers_item)
        headers['Referer'] += id_
        response = self.session.get(url, headers=headers)
        if response.status_code != 200:
            print('获取菜品详情失败：', url)
            self.state = True
            return None
        self.wait()
        print('获取菜品详情成功：', url)
        return response.html

    def get_url(self, content):
        try:
            initial = json.loads(content)
            return ["/recipe/" + str(item["id"])
                    for item in initial['data']['dataset']]
        except TypeError as e:
            for item in initial['data']['dataset']:
                print(type(item["id"]), item["id"])
            print(e)
        except KeyError:
            pass
        self.state = True
        return ['0']

    def get_data(self, html):
        if not html:
            return None
        try:
            name = html.find('div.content-right > h1.title-p')[0].text
            ingredients = [i.text for i in html.find('div.ingredients')]
            condiment = [i.text for i in html.find('div.condiment')]
            practices = [i.text for i in html.find('div.practices > div.pai')]
            favorite = html.find(
                'div.read > div.cntFavorite:nth-child(2)')[0].text
            return [
                       self._filter(name),
                       ','.join(self._filter(condiment)),
                       ','.join(self._filter(practices)),
                       self._filter(favorite)
                   ], self._filter(ingredients)
        except IndexError:
            return None

    def run(self, config, database):
        for i in self.tasks[self.type_:self.length]:
            id_ = self.get_id(i[0])
            start = max(self.page, i[2])
            config["Progress"]["page"] = start
            for j in range(start, i[3] + 1):
                if self.state:
                    return
                url = self.open_url(i[0], id_, j)
                for x in url:
                    if self.state:
                        return
                    html = self.get_html(self.base_url + x, id_)
                    data, ingredients = self.get_data(html)
                    if data:
                        data = self.merge(x, data, i[1], ingredients)
                        database.insert_data(data)
                    else:
                        self.state = True
                    # break
                else:
                    config["Progress"]["page"] += 1
                # break
            else:
                config["Progress"]["type"] += 1
                config["Progress"]["page"] = 0
            self.last = None
            return  # 默认每次运行仅获取一种类型的数据，注释此代码可实现一次性爬取全部数据
        else:
            print('已完成全部爬取任务！')

    def get_last(self, url):
        response = self.session.get(url, headers=self.headers_item)
        if response.status_code != 200:
            self.state = True
            print('获取 last 异常：', url)
            return
        last = re.findall(
            re.compile(r'total:(\d+),'),
            response.html.html)
        if len(last) != 2:
            self.state = True
            print('获取 last 异常：', last)
            return
        self.wait()
        self.last = last[1]
        return response.html

    def get_id(self, url):
        id_ = re.findall(r'^https://www.haodou.com/recipe/all/(\d+$)', url)
        if not id_:
            self.state = True
            return
        return id_[0]

    @staticmethod
    def wait():
        time.sleep(random.random() + random.randint(2, 5))
        return

    @staticmethod
    def md5(text):
        hash_ = hashlib.md5()
        hash_.update(bytes(text, encoding='utf-8'))
        return hash_.hexdigest()

    @staticmethod
    def _filter(content):
        if isinstance(content, str):
            return content.replace('\n', '').strip()
        elif isinstance(content, list):
            return [i.replace('\n', '').strip() for i in content]
        else:
            raise ValueError

    def merge(self, link, data, type_, ingredients):
        try:
            id_ = re.findall(r'^/recipe/(\d+)$', link)[0]
        except IndexError:
            self.state = True
            return None
        item = [id_, self.base_url + link, type_]
        if len(ingredients) > 20:
            self.state = True
            print('主料信息过多：', self.base_url + link, '请联系开发者或自行修改代码！')
            return None
        while len(ingredients) < 20:
            ingredients.append(None)
        data[1:1] = ingredients
        item[2:2] = data
        return item


class Core:
    def __init__(self, config, database, spider):
        self.config = config()
        if not self.config.check_all():
            print(f'请修改 {self.config.config_file} 配置文件')
            self.run = False
        else:
            self.mysql_config, self.progress_config, self.tasks_config, self.tasks_length = self.config.get_config()
            self.database = database(self.mysql_config)
            self.spider = spider(
                self.progress_config,
                self.tasks_config,
                self.tasks_length)
            self.run = True

    def start(self):
        if not self.run:
            print('未开始爬取数据！')
            return
        print('若程序报错请保留错误信息，并联系开发者！')
        self.database.create_table()
        config_new = self.config.new_config()
        self.spider.run(config_new, self.database)
        self.config.save_config()

    def __del__(self):
        print('程序已退出！')


def main():
    corn = Core(Config, Database, Spider)
    corn.start()


if __name__ == '__main__':
    main()
