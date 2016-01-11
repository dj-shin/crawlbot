# !/usr/bin/python3
import requests
from queue import Queue
from bs4 import BeautifulSoup as bs
from setting import username, password
from datetime import datetime
from time import sleep
import threading


class EtlCrawl(threading.Thread):
    s = requests.Session()
    link_list = []
    ubboard_id = None
    board_name = None

    def __init__(self, queue, ubboard_id, board_name):
        threading.Thread.__init__(self)
        login_form = {
            'si_redirect_address': 'https://sso.snu.ac.kr/snu/ssologin_proc.jsp? \
            si_redirect_address=http://my.snu.ac.kr/mysnu/login? \
            langKnd=ko&loginType=portal',
            'si_realm': 'SnuUser1',
            '_enpass_login_': 'submit',
            'langKnd': 'ko',
            'si_id': username,
            'si_pwd': password, }
        login_form_req = self.s.post(
                'https://sso.snu.ac.kr/safeidentity/modules/auth_idpwd',
                data=login_form)

        redirect_url = 'https://sso.snu.ac.kr/nls3/fcs'
        redirect_data = bs(login_form_req.text, 'html5lib').find_all('input')
        redirect_form = {redirect_datum['name']: redirect_datum['value']
                         for redirect_datum in redirect_data}
        self.s.post(redirect_url, data=redirect_form)

        self.queue = queue
        self.ubboard_id = ubboard_id
        self.board_name = board_name

    def init_crawl(self, ubboard_id):
        etl = self.s.get(
                'http://etl.snu.ac.kr/mod/ubboard/view.php?id=' +
                str(ubboard_id) +
                '&ls=1000&page=1')
        etl_board = bs(etl.text, 'html5lib').find_all('tr')
        for title in etl_board:
            if title.a is not None:
                link = title.a.get('href')
                article = title.a.get_text().strip()
                if link not in self.link_list:
                    self.link_list.append(link)

    def crawl(self, ubboard_id):
        etl = self.s.get(
                'http://etl.snu.ac.kr/mod/ubboard/view.php?id=' +
                str(ubboard_id) +
                '&ls=1000&page=1')
        etl_board = bs(etl.text, 'html5lib').find_all('tr')
        for title in etl_board:
            if title.a is not None:
                link = title.a.get('href')
                article = title.a.get_text().strip()
                if link not in self.link_list:
                    self.link_list.append(link)
                    self.queue.put(
                            {'type': 'msg',
                             'content': '마시마로_業: ' + self.board_name +
                             ' : "' + article})
                    self.queue.put(
                            {'type': 'msg', 'content': '"[' + link + ']'})

    def run(self):
        self.init_crawl(self.ubboard_id)
        while True:
            self.crawl(self.ubboard_id)
            sleep(60)

if __name__ == '__main__':
    q = Queue()
    etl = EtlCrawl(q)
    etl.init_crawl(383757)
    while True:
        etl.crawl(383757)
        while not q.empty():
            print(datetime.now())
            print(q.get())
        sleep(60)
