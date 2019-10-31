import datetime
import email
import os
import logging

from wheaton import gmail, discord

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
    )

    inbox = gmail.Inbox()

    date = datetime.date.today() - datetime.timedelta(days=2)

    query = " ".join([
        'list:{wheaton-ultimate@googlegroups.com wheaton-soccer@googlegroups.com}',
        'subject:(-"Message Pending)',
        'after:%s' % date.strftime('%Y/%m/%d'),
    ])
    query = 'subject:"toss a disc" before:2019/10/25'

    print(query)
    mids = inbox.list(query)

    for msg in inbox.get(mids):
        print(dict((k, msg[k]) for k in ('from', 'subject', 'body')))

        msg_args = {
            'topic': 'testing', #msg['topic'],
            'subject': msg['subject'],
            'from_': email.utils.parseaddr(msg['from']),
            'body': msg['body'],
            'channel': msg['id'] == msg['thread_id'],
            'attachments': msg['attachments'],
        }

        discord.post(**msg_args)


if __name__ == '__main__':
    main()

