import os
import queue
import re
import threading

import requests
from lxml import etree

dateHome = 'https://pixivbox.com/'

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36",
    'referer': 'https://pixivbox.com/?daily',
    'cookie': 'custom_visited_urls=a%3A8%3A%7Bi%3A0%3Bs%3A15%3A%22%2F%3Fpid%3D117381087%22%3Bi%3A1%3Bs%3A15%3A%22%2F'
              '%3Fpid%3D117379582%22%3Bi%3A2%3Bs%3A15%3A%22%2F%3Fpid%3D116537645%22%3Bi%3A3%3Bs%3A15%3A%22%2F%3Fpid'
              '%3D117365403%22%3Bi%3A4%3Bs%3A15%3A%22%2F%3Fpid%3D117375978%22%3Bi%3A5%3Bs%3A15%3A%22%2F%3Fpid'
              '%3D117365327%22%3Bi%3A6%3Bs%3A15%3A%22%2F%3Fpid%3D116518816%22%3Bi%3A7%3Bs%3A15%3A%22%2F%3Fpid'
              '%3D117388870%22%3B%7D'
}


def getPidFromHome():
    dateResponse = requests.get(dateHome, headers=headers)
    dateHtml = etree.HTML(dateResponse.text)

    # 获取日期列表 0 代表第一个日期
    dateList = dateHtml.xpath('/html/body/form/div[2]')[0]
    PidList = []
    for picNode in dateList:
        picID = picNode.xpath('./a/p/text()')
        # 将获取到的图片 ID 存储到列表中
        picID_list = [paremeter.strip() for paremeter in picID if paremeter.strip()]  # 去除空格并过滤空元素
        PidList.extend(picID_list)  # 使用 extend 方法添加到列表中
    return PidList


def getPicFromPid(pid):
    pic_indexUrl = 'https://pixivbox.com/?pid=' + pid
    picResponse = requests.get(pic_indexUrl, headers=headers)
    picHtml = etree.HTML(picResponse.text)

    # 获取图片链接
    Url = picHtml.xpath('/html/body/form/div[3]/div/a/@href')
    return Url


def downloadPic(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        pic_content = response.content
        # 解析URL获取文件名
        pic_filename = url.split('/')[-1]
        # 构建文件夹路径
        folder_path = 'imgs/' + getDate() + '/'
        # 如果文件夹不存在，则创建它
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # 写入文件
        with open(os.path.join(folder_path, pic_filename), 'wb') as f:
            f.write(pic_content)
            print('图片下载成功')
    else:
        print('图片下载失败')


def getDate():
    dateResponse = requests.get(dateHome, headers=headers)
    dateHtml = etree.HTML(dateResponse.text)

    # 获取日期
    Date = dateHtml.xpath('/html/body/form/center/div[2]/text()')
    Date = ''.join(Date).strip()  # 去除空格
    if Date:  # 检查是否成功获取到日期文本

        # 匹配日期的正则表达式
        pattern = r'(\d+)/(\d+)/(\d+)'

        # 使用正则表达式进行匹配
        match = re.search(pattern, Date)

        if match:
            month = match.group(1)
            day = match.group(2)
            year = match.group(3)
            # 组合成20240331的形式
            date = year + month.zfill(2) + day.zfill(2)
            return date
        else:
            return "年月日"
    else:
        return "无日期"


# 线程池
class MyThreadPool:
    def __init__(self, maxsize=5):
        self.maxsize = maxsize
        self._pool = queue.Queue(maxsize)  # 使用queue队列，创建一个线程池
        for _ in range(maxsize):
            self._pool.put(threading.Thread)

    def get_thread(self):
        return self._pool.get()

    def add_thread(self):
        self._pool.put(threading.Thread)


def run(url):
    print("任务开始")
    downloadPic(url)
    pool.add_thread()  # 执行完毕后，再向线程池中添加一个线程类


if __name__ == '__main__':
    # 进阶:多线程处理下载图片
    pool = MyThreadPool(10)  # 设定线程池中最多只能有5个线程类

    for i in range(len(getPidFromHome())):
        t = pool.get_thread()  # 每个t都是一个线程类
        pid = getPidFromHome()[i]
        pic_url = getPicFromPid(pid)[0]
        obj = t(run(pic_url))  # 这里的obj才是正真的线程对象
        obj.start()
