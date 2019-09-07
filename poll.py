import datetime
import email
import os
import sys
import argparse
import logging

from pymongo import MongoClient

from wheaton import gmail, slack, discord

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--prime', 
        help='Prime db with existing messages',
        action='store_true',
    )

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
    )

    slack_db = MongoClient(os.environ.get('MONGO_DB_URI'), retryWrites=False)['slack']

    bot = slack.Bot()
    inbox = gmail.Inbox()

    delta = 365 if args.prime else 3
    date = datetime.date.today() - datetime.timedelta(days=delta)

    query = " ".join([
        'list:{wheaton-ultimate@googlegroups.com wheaton-soccer@googlegroups.com}',
        '-subject:(-"Message Pending)',
        'after:%s' % date.strftime('%Y/%m%d'),
    ])

    mids = inbox.list(query)
    mids = [mid for mid in mids if not slack_db.emails.find_one({'id': mid})]

    for msg in inbox.get(mids):
        print(msg)
        slack_db.emails.insert_one(msg) 

        msg_args = {
            'topic': msg['topic'],
            'subject': msg['subject'],
            'from_': email.utils.parseaddr(msg['from']),
            'body': msg['body'],
            'channel': msg['id'] == msg['thread_id'],
        }

        discord.post(**msg_args)
        ts = bot.post(**msg_args)


if __name__ == '__main__':
    main()

