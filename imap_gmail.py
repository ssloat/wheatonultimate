import datetime
import email
import os
import sys
import argparse
import logging

from pymongo import MongoClient

from wheaton import imap, slack, discord

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
    inbox = imap.Inbox(os.environ.get('SENDER_USER'), os.environ.get('SENDER_PASS'))

    delta = 365 if args.prime else 3
    date = datetime.date.today() - datetime.timedelta(days=delta)

    timestamps = {}
    uids = [int(u.decode('utf-8')) for u in inbox.search(date)]
    for uid in sorted(uids):
        uid = str(uid)
        if slack_db.emails.find_one({'uid': uid}):
            print("Found email with uid %s" % uid)
            continue

        msg = inbox.process_uid(uid)
        if msg is None:
            continue
        print(msg)
        slack_db.emails.insert_one(msg) 

        msg_args = {
            'topic': msg['topic'],
            'group': msg['group'],
            'subject': msg['subject'],
            'from_': email.utils.parseaddr(msg['from']),
            'body': msg['body'],
            'channel': False,
        }

        thread_id = msg['thread_id']
        if thread_id in timestamps:
            discord.post(**msg_args)
            bot.post(**msg_args)
            continue

        x = slack_db.threads.find_one({'thread_id': thread_id})
        if x: 
            timestamps[thread_id] = x['ts']
            discord.post(**msg_args)
            bot.post(**msg_args)
            continue

        msg_args['channel'] = True
        discord.post(**msg_args)
        ts = bot.post(**msg_args)
        timestamps[thread_id] = ts
        slack_db.threads.insert_one({
            'ts': ts, 
            'thread_id': thread_id, 
            'subject': msg['subject'],
            'tags': msg['tags'],
            'from': msg['from'],
            'group': msg['group'],
            'date': msg['date'],
        })


if __name__ == '__main__':
    main()

