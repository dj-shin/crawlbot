# !/usr/bin/python3
import requests
from queue import Queue
from bs4 import BeautifulSoup as bs
from setting import snupsy_username, snupsy_password
from datetime import datetime
from time import sleep
import threading


class PsyCrawl(threading.Thread):
    s = requests.Session()
    link_list = []
    board_name = None

    def __init__(self, queue, board_name):
        threading.Thread.__init__(self)
        login_form = {
                'ctl00$ContentPlaceHolder1$userid': snupsy_username,
                'ctl00$ContentPlaceHolder1$pw': snupsy_password,
                'ctl00$ContentPlaceHolder1$default_auth_button': '로그인',
                'ctl00$ContentPlaceHolder1$return_experiment_id': '',
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__EVENTVALIDATION': '/wEdAAXgbYJg97p18OKhGOsqqg4rUIlPJ3shF6ZfHx5cHAdswX1Gsa4Qp9IFMNZyT1m/ORlOGPoKvJSxXl507+PWyULdk0IaRa81gSyF/t2E7n3iJQQ6kzdIXOQxbd+RTCSkYGCFK4jpQmHNMxPymazrnBSo',
                '__VIEWSTATE': '/wEPDwUKLTM3OTkzMzYzMmRkSvWQjlXufOcf6h0NcyLaxKNboki1VicdKQ9fTRV1nOY=',
                '__VIEWSTATEGENERATOR': 'CA0B0334',
                }
        header = {
                'Cookie': 'ASP.NET_SessionId=msxgmcu5qnbo0b1l2ytxermp; cookie_ck=Y; language_pref=KO',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
                }
        login_form_req = self.s.post(
                'https://snupsy.sona-systems.com/Default.aspx?ReturnUrl=%2fall_exp_participant.aspx',
                data=login_form, headers=header)

        self.queue = queue
        self.board_name = board_name

    def init_crawl(self):
        header = {
                'Cookie': 'ASP.NET_SessionId=msxgmcu5qnbo0b1l2ytxermp; cookie_ck=Y; language_pref=KO; WEBHOME=3B7E11218CD95FDFA12E086BA826ECCCED3D9C1B3FEC2B323414B5C4AD9F9D7428272D4DD6CAF232B4D713C1305D18EA3AF57722072C799050654167625B9B92F2DEFAE0F8F36DE917C3D756C8EB03D362E05E15761AF73E6337CCFAE4A927710EDD3483D282E7F9295611EDB9994E3A2052F4368A0202DC4D4799744A08F615'
                }
        psy = self.s.get('https://snupsy.sona-systems.com/all_exp_participant.aspx', headers=header)
        psy_board = bs(psy.text, 'html5lib').find_all('tr')
        for title in psy_board:
            if title.a is not None:
                link = title.a.get('href')
                article = title.a.get_text().strip()
                if link not in self.link_list:
                    self.link_list.append(link)

    def crawl(self):
        header = {
                'Cookie': 'ASP.NET_SessionId=msxgmcu5qnbo0b1l2ytxermp; cookie_ck=Y; language_pref=KO; WEBHOME=3B7E11218CD95FDFA12E086BA826ECCCED3D9C1B3FEC2B323414B5C4AD9F9D7428272D4DD6CAF232B4D713C1305D18EA3AF57722072C799050654167625B9B92F2DEFAE0F8F36DE917C3D756C8EB03D362E05E15761AF73E6337CCFAE4A927710EDD3483D282E7F9295611EDB9994E3A2052F4368A0202DC4D4799744A08F615'
                }
        psy = self.s.get('https://snupsy.sona-systems.com/all_exp_participant.aspx', headers=header)
        psy_board = bs(psy.text, 'html5lib').find_all('tr')
        for title in psy_board:
            if title.a is not None:
                link = title.a.get('href')
                article = title.a.get_text().strip()
                if link not in self.link_list:
                    self.link_list.append(link)
                    self.queue.put(
                            {'type': 'msg',
                             'content': '마시마로: ' + self.board_name +
                             ' : "' + article})
                    self.queue.put(
                            {'type': 'msg', 'content': '"[' + link + ']'})
                print(article + ' ' + link)

    def run(self):
        self.init_crawl()
        while True:
            self.crawl()
            sleep(60)

if __name__ == '__main__':
    q = Queue()
    psy = PsyCrawl(q, 'R-Point')
    psy.init_crawl()
    while True:
        psy.crawl()
        while not q.empty():
            print(q.get())
        sleep(10)
