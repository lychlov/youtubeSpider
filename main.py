# -*- coding: utf-8 -*-
# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python
from itertools import count
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By  # 按照什么方式查找，By.ID,By.CSS_SELECTOR
from selenium.webdriver.common.keys import Keys  # 键盘按键操作
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait  # 等待页面加载某些元素
import os
import httplib2
from httplib2 import socks
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from bs4 import BeautifulSoup
import json
from config import keywords, proxy_url
from utils import YouTubeMongoP
import re


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
        # client_secrets_file = "cert3.json"
        proxy_info = httplib2.ProxyInfo(
            socks.PROXY_TYPE_HTTP, proxy_url['ip'], proxy_url['port'])
        http = httplib2.Http(timeout=100, proxy_info=proxy_info)
        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        # credentials = flow.run_console()
        key = 'AIzaSyABDWWTFKsKKa3DOESUTiwEwBB9jaorg6o'
        # key = 'AIzaSyDEo-roH1IUEy0PZRNV2AoLUOX1cQ8H3Bg'
        
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=key, http=http)

    def search(self, keyword):
        request = self.youtube.search().list(
            part="snippet",
            maxResults=50,
            q=keyword,
            regionCode='US'
        )
        response = request.execute()
        return response

    def search_next_page(self,keyword,pagetoken):
        request = self.youtube.search().list(
            part="snippet",
            maxResults=50,
            q=keyword,
            regionCode='US',
            pageToken=pagetoken
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


if __name__ == "__main__":
    count=0
    fac = GoogleFactory()
    pipline = YouTubeMongoP()
    pagetoken = ''
    # browser = webdriver.Chrome()
    for keyword in keywords:
        res = fac.search(keyword)
        while True  :
            channel_ids = set()
            for item in res.get('items'):
                channel_ids.add(item.get('snippet').get('channelId'))
            channel_str = ','.join(channel_ids)
            info = fac.channel(channel_str)
            for channel_info in info.get('items'):
                item = {}
                item_example = {"description": "PO Box 976 Greensburg PA 15601\nShe/Her\nVenmo: jjones0451\n⬇️ALL NEEDS BELOW⬇️",
                    "email": "",
                    "nickname": "Jordan",
                    "tik_link": "https://www.tiktok.com/@jjones451",
                    "social_link": "https://linktr.ee/jjones451",
                    "fans": 1500000,
                    "video_count": 3213,
                    "create_time": 1544652250,
                    "keyword": "petvacuum"}
                item['description'] = channel_info.get('snippet').get('description')
                match = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,8}', item['description'])
                item['email'] = ','.join(list(set(match)))
                item['nickname'] = channel_info.get('snippet').get('title')
                item['youtube_link'] = 'https://www.youtube.com/channel/{}'.format(channel_info.get('id'))
                item['fans'] = int(channel_info.get('statistics').get('subscriberCount','0'))
                item['video_count'] = int(channel_info.get('statistics').get('videoCount','0'))
                item['create_time'] = channel_info.get('snippet').get('publishedAt')
                item['keyword'] = keyword
                item['location'] = channel_info.get('snippet').get('country')
                print(item)
                if item and item['email'] != '' and item['fans'] >= 50000:
                    count += 1
                    print("{}-{}:{}".format(str(count), item['email'], item['fans']))
                pipline.process_item(item=item)
            if res.get('nextPageToken') and pagetoken!=res.get('nextPageToken'):
                pagetoken = res.get('nextPageToken')
                res  = fac.search_next_page(keyword,pagetoken)

