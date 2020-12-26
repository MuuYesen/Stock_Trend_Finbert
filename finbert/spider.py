import requests
import re
import time
import random
import json
from lxml import etree
import re
import pandas as pd


class Spider_For_GUBA(object):
    
    def __init__(self):
        pass
    
    def require_reviews(self,startPage,endPage):
        base_url = 'http://guba.eastmoney.com'

        headers_h = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"}

        review_all = []

        for i in range(startPage-1,endPage): ### 仅爬取三面帖子
            start_url = "http://guba.eastmoney.com/list,zssh000001,99_{}.html".format(i+1)
            response = requests.get(url=start_url, headers=headers_h)
            html = response.content.decode("utf-8")
            html_obj = etree.HTML(html)
            div_list = html_obj.xpath('//div[@id="articlelistnew"]/div')
            for div in div_list: ### 遍历每一个帖子
                if div.xpath("./span/a/@href") == []:
                    continue
                sub_url = str(div.xpath("./span/a/@href")[0])
                url_post = re.findall('\d{9}',sub_url)[0]
                reviews = self.require_reviews_of_one_blob(url_post)
                review_all.extend(reviews)
            print('page {} : completed'.format(i+1))
        corpus = pd.DataFrame(review_all,columns=['text','date'])
        return corpus
            
    def require_reviews_of_one_blob(self,url_post):  ### 单个帖子的评论采集
#        time.sleep(random.random()*3)
        url = 'http://guba.eastmoney.com/interface/GetData.aspx'  ### t可以为任意值，不一定非要是当前时间
        headers ={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '121',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'guba.eastmoney.com',
            'Origin': 'http://guba.eastmoney.com',
            'Referer': 'http://guba.eastmoney.com/news,zssh000001,964725926_1.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        } ### 来自XHR

        review_all = []

        i=1
    
        while True:  ### 前12面
            data = {"param": "postid={}&sort=1&sorttype=1&p={}&ps=30".format(url_post,i),
                    "path": "reply/api/Reply/ArticleNewReplyList","env":"2"} ### XHR
            r = requests.post(url=url, headers=headers,data=data)
            data_json = json.loads(r.text)
        
            if data_json['re'] == None:
                break
            
            for review in data_json['re']:
                review_all.append([review['reply_text'],review['reply_time']])
                if len(review['child_replys']) != 0:
                    for chlid_review in review['child_replys']:
                        review_all.append([chlid_review['reply_text'],chlid_review['reply_time']])  
                
            if data_json['me'] == "暂无更多评论，欢迎发表观点":
                break   
        
            i = i + 1
        
        return review_all  