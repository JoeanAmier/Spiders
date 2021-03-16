import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import FakeUserAgent
import json
import jieba
import wordcloud
import xlwt


def input_data():
    url = input('输入视频网址：')
    if url[-1] != '/':
        url += '/'
    check_url = re.compile(r'^https://www.bilibili.com/video/(.*?)/$')
    bv = re.findall(check_url, url)
    if not bool(bv):
        raise ValueError('视频网址格式错误')
    if len(bv[0].split('/')) != 1:
        raise ValueError('视频网址格式错误')
    page = int(input('爬取评论页数(仅爬取指定页数评论)：'))
    if page < 1:
        raise ValueError('爬取评论总页数输入错误')
    return url, page


def get_url(url, page):
    findav = re.compile(
        r'<meta content="https://www.bilibili.com/video/av(.*?)/"')
    content, text = open_url(url)
    html = BeautifulSoup(content, 'html.parser')
    html = str(html)
    av = re.findall(findav, html)
    if len(av) == 2 and av[0] == av[1]:
        av = av[0]
        url = 'https://api.bilibili.com/x/v2/reply?pn=' + \
              str(page) + '&type=1&oid=' + av + '&sort=2'
        return url
    else:
        raise ValueError('获取视频AV号发生异常')


def open_url(url):
    header = {'user-agent': FakeUserAgent().chrome}
    html = requests.get(url=url, headers=header)
    return html.content, html.text


def deal_data(jsdata):
    data = []
    jsdata = json.loads(jsdata)
    for i in range(len(jsdata['data']['replies'])):
        mdata = []
        aname = jsdata['data']['replies'][i]['member']['uname']
        mdata.append(aname)
        asex = jsdata['data']['replies'][i]['member']['sex']
        mdata.append(asex)
        asign = jsdata['data']['replies'][i]['member']['sign']
        mdata.append(asign)
        amessage = jsdata['data']['replies'][i]['content']['message']
        mdata.append(amessage)
        idata = []
        if bool(jsdata['data']['replies'][i]['replies']):
            for j in range(len(jsdata['data']['replies'][i]['replies'])):
                idata_cache = []
                iname = jsdata['data']['replies'][i]['replies'][j]['member']['uname']
                idata_cache.append(iname)
                isex = jsdata['data']['replies'][i]['replies'][j]['member']['sex']
                idata_cache.append(isex)
                isign = jsdata['data']['replies'][i]['replies'][j]['member']['sign']
                idata_cache.append(isign)
                imessage = jsdata['data']['replies'][i]['replies'][j]['content']['message']
                idata_cache.append(imessage)
                idata.append(idata_cache)
        mdata.append(idata)
        data.append(mdata)
    return data


def cloud(data):
    cache = ''.join(data[i][3] for i in range(len(data)))
    data = jieba.cut(cache)
    word = wordcloud.WordCloud(
        font_path='msyh.ttc',
        background_color='white',
        width=1920,
        height=1080)
    word.generate('%s' % ' '.join(data))
    word.to_file('评论词云图.png')


def save_data(data):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('爬取结果', cell_overwrite_ok=False)
    top = ('类型', '用户名', '性别', '签名', '评论')
    for i in range(len(top)):
        sheet.write(0, i, top[i])
    for i in range(len(data)):
        top = data[i]
        for j in range(len(top) + 1):
            if j == 4 and bool(top[j]):
                for x in range(len(top[j])):
                    for y in range(len(top[j][x]) + 1):
                        if y == 4:
                            sheet.write(x + 2 + 4 * i, 0, '评论回复')
                        else:
                            text = top[j][x][y]
                            sheet.write(x + 2 + 4 * i, y + 1, text.strip())
            elif j != 4 or not bool(1 - bool(top[j])):
                if j == 5:
                    sheet.write(1 + 4 * i, 0, '主评论')
                else:
                    text = top[j]
                    sheet.write(1 + 4 * i, j + 1, text.strip())
    try:
        book.save('B站评论数据.xls')
    except PermissionError:
        print('保存数据失败，请关闭xlsx文件后重新运行程序')


def main():
    url, page = input_data()
    url = get_url(url, page)
    content, text = open_url(url)
    data = deal_data(text)
    save_data(data)
    cloud(data)
    print('程序结束')


if __name__ == '__main__':
    main()
