import json
import re
import time

import requests


class DouYin:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5time.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chro'
                          'me/77.0.3904.108 Safari/537.36'}
        self.android_headers = {'user-agent': 'Android'}

    def get_share_url(self, url):
        response = requests.get(
            url,
            headers=self.headers,
            allow_redirects=False)
        if 'location' in response.headers.keys():
            return response.headers['location']
        else:
            raise Exception("解析失败")

    def get_data(self, url, share):
        response = requests.get(url, headers=self.headers).text
        json_str = json.loads(response)
        download_url = json_str['item_list'][0]['video']['play_addr']['url_list'][0].replace(
            "playwm", "play")
        name = re.findall(r'(.*)https://v.douyin.com', share)[0]
        name = name.strip()
        with open(name + '.mp4', 'wb') as f:
            f.write(
                requests.get(
                    url=download_url,
                    headers=self.android_headers).content)
        print('视频下载完成！')
        print('软件即将退出')
        for i in range(1, 6):
            time.sleep(1)
            print('\r', end='')
            print(6 - i, end='')

    def run(self):
        print("请输入抖音短视频分享链接：")
        share = input()
        url = re.findall(r'https://v.douyin.com/.*/', share)[0]
        location = self.get_share_url(url)
        vid = re.findall(r'/share/video/(\d*)', location)[0]
        url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(
            vid)
        self.get_data(url, share)


if __name__ == '__main__':
    dy = DouYin()
    dy.run()
