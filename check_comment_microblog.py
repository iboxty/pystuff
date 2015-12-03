# -*-coding:utf8-*-

'''
author:iboxty
date:2015-12-3
function:登陆微博自动检测微博好友是否发微博，并且自动评论
         爬取信息的页面是微博手机版weibo.cn
'''

import requests
from lxml import etree
import os
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')


class MicroSniffer(object):

    def __init__(self):
        self.url_target = 'http://weibo.cn/u/********' #填入要解析的微博主页
        self.url_login = 'https://login.weibo.cn/login/' #微博登陆页面
        self.url_random_login = self.url_login
        self.session = requests.session()

    def getsource(self, url):
        html = self.session.get(url).content
        return html

    '''
    解析登陆页面,得到登录信息
    '''
    def getdata(self, html, ch, backurl=''):
        selector = etree.HTML(html)
        password = selector.xpath('//input[@type="password"]/@name')[0]
        vk = selector.xpath('//input[@name="vk"]/@value')[0]
        action = selector.xpath('//form[@method="post"]/@action')[0]
        self.url_random_login = self.url_login + action
        if ch == 0:
            url = 'http://weibo.cn/u/1771904270'
        else:
            url = backurl
        data = {
            'mobile': '**********',     #自己的微博账号
            password: '**********',   #自己的微博密码
            'remember': 'on',
            'backURL': url,
            'backTitle': u'微博',
            'tryCount': '',
            'vk': vk,
            'submit': u'登录'
            }
        return data

    '''
    从好友主页获取第一条微博内容
    以及第一条微博内容评论的url
    '''
    def getcontent(self, data):
        newhtml = self.session.post(self.url_random_login, data=data).content
        new_selector = etree.HTML(newhtml)
        content = new_selector.xpath('//span[@class="ctt"]')
        newcontent = unicode(content[2].xpath('string(.)')).replace('http://','')
        sendtime = new_selector.xpath('//span[@class="ct"]/text()')[0]
        urls = new_selector.xpath('//a[@class="cc"]/@href')
        urlcon = new_selector.xpath('//a[@class="cc"]/text()')
        url = ""
        ran = len(urls)
        for i in range(0, ran):
            if "原文" in urlcon[i]:
                pass
            else:
                url = urls[i]
                break
        print url
        sendtext = newcontent + sendtime
        info = []
        info.append(sendtext)
        info.append(url)
        return info

    '''
    发送评论内容
    '''
    def sendcomment(self, newurl, comment):
        commenthtml = self.session.get(newurl).content
        com_selector = etree.HTML(commenthtml)
        srcuid = com_selector.xpath('//input[@name="srcuid"]/@value')[0]
        id1 = com_selector.xpath('//input[@name="id"]/@value')[0]
        rl = com_selector.xpath('//input[@name="rl"]/@value')[0]
        action = com_selector.xpath('//form[@method="post"]/@action')[0]
        com_url = "http://weibo.cn" + action
        data = {
            'srcuid' : srcuid ,
            'id' : id1 ,
            'rl' : rl ,
            'content' : comment ,
            }
        newhtml = self.session.post(com_url, data=data).content
        if "点击这里" in newhtml:
            err_selector = etree.HTML(newhtml)
            err_info = err_selector.xpath('//div[@class="me"]/text()')[0]
            print "评论失败,错误信息如下："
            print err_info
        else:
            print "评论成功"

    def tosave(self,text):
        f= open('weibo.txt','a')
        f.write(text + '\n')
        f.close()

    def tocheck(self,data):
        if not os.path.exists('weibo.txt'):
            return True
        else:
            f = open('weibo.txt', 'r')
            existweibo = f.readlines()
            if data + '\n' in existweibo:
                return False
            else:
                return True

if __name__ == '__main__':
    helper = MicroSniffer()
    while True:
        '''
        每一次执行过程新开一个session
        保持一次登陆之后不用再次登录
        也不用担心session过期的问题

        执行流程：
        get请求-好友主页
        post请求-登录信息
        IF 微博有更新
        get请求-第一条微博评论页面
        post请求-评论
        ELSE 下一轮
        '''
        try:
            helper.session = requests.session()
            print time.strftime( '%Y-%m-%d %X', time.localtime() )
            source = helper.getsource(helper.url_target)
            data = helper.getdata(source,0,'')
            content = helper.getcontent(data)
            if helper.tocheck(content[0]):
                helper.sendcomment(content[1], u'评论内容***')   #填入评论内容
                helper.tosave(content[0])
                print content[0]
            else:
                print u'pass'
            helper.session.close()
        except:
            print "出错了,请自行检查"
        time.sleep(15)