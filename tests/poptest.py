import os, sys

srcpath = os.path.abspath("../src")
sys.path.insert(0,srcpath)

import poplib
from email.Parser import Parser as EmailParser
from email.header import decode_header
from cloudsn.core import utils

class PopBox:
    def __init__(self, user, password, host, port = 110, ssl = False):
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port)
        self.ssl = ssl

        self.mbox = None
        self.parser = EmailParser()

    def __connect(self):
        if not self.ssl:
            self.mbox = poplib.POP3(self.host, self.port)
        else:
            self.mbox = poplib.POP3_SSL(self.host, self.port)

        self.mbox.user(self.user)
        self.mbox.pass_(self.password)

    def get_mails(self):
        self.__connect()

        messages = []
        print "Starting reading POP messages"
        msgs = self.mbox.list()[1]
        print "POP messages readed: %i" % (len(msgs))
        for msg in msgs:
            msgNum = int(msg.split(" ")[0])
            msgSize = int(msg.split(" ")[1])

            # retrieve only the header
            st = "\n".join(self.mbox.top(msgNum, 0)[1])
            print st
            print "----------------------------------------"
            msg = self.parser.parsestr(st, True) # header only
            sub = utils.mime_decode(msg.get("Subject"))
            msgid = msg.get("Message-Id")
            if not msgid:
                msgid = hash(msg.get("Received") + sub)
            fr = utils.mime_decode(msg.get("From"))
            messages.append( [msgid, sub, fr] )

        self.mbox.quit()
        return messages

def main():
    g = PopBox ("chuchiperriman@gmail.com", , 
            "pop.gmail.com", 995, True)
    mails = g.get_mails()
    for mail_id, sub, fr in mails:
        print mail_id, sub
        notifications[mail_id] = sub
        if mail_id not in account.notifications:
            n = Notification(mail_id, sub, fr)
            account.new_unread.append (n)
    account.notifications = notifications
        
if __name__ == '__main__':
    main()
