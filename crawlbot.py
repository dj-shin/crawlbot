# -*- coding: utf-8 -*-

from connector.ircmessage import IRCMessage
from queue import Queue


class Bot():
    irc = None
    msgQueue = Queue()
    channel_list = []

    def __init__(self):
        from connector.ircconnector import IRCConnector
        self.irc = IRCConnector(self.msgQueue)
        self.irc.setDaemon(True)
        self.irc.start()

    def run(self):
        while True:
            packet = self.msgQueue.get()
            if packet['type'] == 'msg':
                msg = packet['content']
                for channel in self.channel_list:
                    self.irc.sendmsg(channel, msg)

            elif packet['type'] == 'irc':
                message = packet['content']
                print(message)
                if message.msgType == 'INVITE':
                    self.irc.joinchan(message.channel)

                elif message.msgType == 'MODE':
                    if message.msg == '+o ' + self.irc.botnick:
                        self.irc.sendmsg(message.channel, '감사합니다 :)')

                elif message.msgType == 'KICK':
                    if message.channel in self.channel_list:
                        self.channel_list.remove(message.channel)

                elif message.msgType == 'PRIVMSG':
                    if (message.msg == '!공지' and
                            message.channel not in self.channel_list):
                        self.channel_list.append(message.channel)
                        self.irc.sendmsg(message.channel, '크롤링 공지를 시작합니다')

                    elif (message.msg == '!공지해제' and
                            message.channel in self.channel_list):
                        self.channel_list.remove(message.channel)
                        self.irc.sendmsg(message.channel, '크롤링 공지를 해제합니다')


if __name__ == '__main__':
    bot = Bot()
    bot.run()
