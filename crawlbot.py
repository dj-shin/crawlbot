#-*- coding: utf-8 -*-

from ircmessage import IRCMessage
from queue import Queue
from setting import botnick


class Bot():
    irc = None
    sendQueue = Queue()
    receiveQueue = Queue()
    channel_list = []

    def __init__(self):
        from ircconnector import IRCConnector
        self.irc = IRCConnector(self.receiveQueue)
        self.irc.setDaemon(True)
        self.irc.start()

        from mysnu import EtlCrawl
        crawlTargetList = [
            {'name':'심리학개론 자료실', 'id':383757},
            {'name':'심리학개론 공지사항', 'id':383755},
            ]
        for crawlTarget in crawlTargetList:
            board = EtlCrawl(self.sendQueue, crawlTarget['id'], crawlTarget['name'])
            board.setDaemon(True)
            board.start()

    def run(self):
        while True:
            while not self.receiveQueue.empty():
                message = self.receiveQueue.get()
                print(message)
                if message.msgType == 'INVITE':
                    self.irc.joinchan(message.channel)

                elif message.msgType == 'MODE':
                    if message.msg == '+o ' + botnick:
                        self.irc.sendmsg(message.channel, '감사합니다 :)')

                elif message.msgType == 'PRIVMSG':
                    if message.msg == '!공지' and message.channel not in self.channel_list:
                        self.channel_list.append(message.channel)
                        self.irc.sendmsg(message.channel, '크롤링 공지를 시작합니다')

                    elif message.msg == '!공지해제' and message.channel in self.channel_list:
                        self.channel_list.remove(message.channel)
                        self.irc.sendmsg(message.channel, '크롤링 공지를 해제합니다')


            while not self.sendQueue.empty():
                msg = self.sendQueue.get()
                for channel in self.channel_list:
                    self.irc.sendmsg(channel, msg)


if __name__ == '__main__':
    bot = Bot()
    bot.run()
