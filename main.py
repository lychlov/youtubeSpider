# -*- coding: utf-8 -*-
# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By  # 按照什么方式查找，By.ID,By.CSS_SELECTOR
from selenium.webdriver.common.keys import Keys  # 键盘按键操作
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait  # 等待页面加载某些元素
import csv
import os
import time
from urllib import request
import httplib2
from httplib2 import socks
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from bs4 import BeautifulSoup
import json
from config import keywords, proxy_url


class GoogleFactory():
    def __init__(self):
        scopes = [
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/youtube.readonly"
        ]
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "cert2.json"
        proxy_info = httplib2.ProxyInfo(
            socks.PROXY_TYPE_HTTP, proxy_url['ip'], proxy_url['port'])
        http = httplib2.Http(timeout=100, proxy_info=proxy_info)
        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        # credentials = flow.run_console()
        key = 'AIzaSyABDWWTFKsKKa3DOESUTiwEwBB9jaorg6o'
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=key, http=http)

    def search(self, keyword):
        request = self.youtube.search().list(
            part="snippet",
            maxResults=50,
            q=keyword
        )
        response = request.execute()
        return response

    def channel(self, _id):
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics,brandingSettings,contentOwnerDetails,status,topicDetails",
            id=_id
        )
        response = request.execute()
        return response

    def videos(self, ids):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=ids
        )
        response = request.execute()
        return response

    def channelSections(self, _id):
        request = self.youtube.channelSections().list(
            part="snippet,contentDetails,id",
            channelId=_id
        )
        response = request.execute()
        return response


class Pipeline():
    head = ['channel_id', 'channel_name','location','subscribe',
            'videos_info', 'contacts', 'channel_url']

    def __init__(self):
        self.f = open("youtube-{}.csv".format(time.time()),
                      "w", newline="", encoding='utf-8')
        self.fieldnames = self.head
        self.writer = csv.DictWriter(self.f, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def write(self, item):
        self.writer.writerow(item)


if __name__ == "__main__":
    fac = GoogleFactory()
    pipline = Pipeline()
    browser = webdriver.Chrome()
    for keyword in keywords:
        res = fac.search('keyword')
        channel_ids = set()
        for item in res.get('items'):
            channel_ids.add(item.get('snippet').get('channelId'))
        channel_str = ','.join(channel_ids)
        info = fac.channel(channel_str)
        for channel_info in info.get('items'):
        item = {}
        item['channel_id'] = channel_info.get('id')
        item['channel_name'] = channel_info.get('snippet').get('title')
        item['subscribe'] = channel_info.get(
            'statistics').get('subscriberCount')
        item['channel_url'] = 'https://www.youtube.com/channel/{}'.format(
            item['channel_id'])
        item['location'] = channel_info.get('snippet').get('country')
        # contacts_res = requests.get(url=item['channel_url']+'/about',proxies={'http':'http://127.0.0.1:1080','https':'https://127.0.0.1:1080'})

        browser.get(item['channel_url']+'/about')
        # html = contacts_res.content
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        if soup.find('div', id='link-list-container'):
            link_area = soup.find(
                'div', id='link-list-container').find_all('a')
        else:
            link_area = []
        links = []
        for i in link_area:
            links.append(i.get('href'))
        item['contacts'] = links
        browser.get(item['channel_url']+'/videos')
        # html = contacts_res.content
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        videos_area = soup.find_all('a', id='video-title')
        vids = []
        for i in videos_area:
            vids.append(i.get('href').replace('/watch?v=',''))
        ids = ','.join(vids)
        v_info = fac.videos(ids)
        videos_info = []
        for v in v_info.get('items'):
            videos_info.append(
                {
                    'v_id': v.get('id'),
                    'title': v.get('snippet').get('title'),
                    'publishedAt':v.get('snippet').get('publishedAt'),
                    'description': v.get('snippet').get('description'),
                    "viewCount": v.get('statistics').get('viewCount'),
                    "likeCount": v.get('statistics').get('likeCount'),
                    "favoriteCount": v.get('statistics').get('favoriteCount'),
                    "commentCount": v.get('statistics').get('commentCount')
                }
            )
        item['videos_info'] = videos_info
        pipline.write(item)


