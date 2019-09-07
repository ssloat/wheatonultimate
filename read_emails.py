import datetime
import email
import os
import logging

from pymongo import MongoClient

from wheaton import gmail, discord, slack

def main():
    #logging.basicConfig(
    #    level=logging.INFO,
    #    format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
    #)

    mongo_db = MongoClient(os.environ.get('MONGO_DB_URI'), retryWrites=False)['slack']
    slack_bot = slack.Bot()
    inbox = gmail.Inbox()

    date = datetime.date.today() - datetime.timedelta(days=7)

    query = " ".join([
        'list:{wheaton-ultimate@googlegroups.com wheaton-soccer@googlegroups.com}',
        'subject:(-"Message Pending)',
        'after:%s' % date.strftime('%Y/%m/%d'),
    ])

    print(query)
    mids = inbox.list(query)
    mids = [mid for mid in mids if not mongo_db.emails.find_one({'id': mid})]

    for msg in inbox.get(mids):
        print(dict((k, msg[k]) for k in ('from', 'subject', 'body')))
        mongo_db.emails.insert_one(msg) 

        msg_args = {
            'topic': msg['topic'],
            'subject': msg['subject'],
            'from_': email.utils.parseaddr(msg['from']),
            'body': msg['body'],
            'channel': msg['id'] == msg['thread_id'],
            'attachments': msg['attachments'],
        }

        discord.post(**msg_args)

        thread = mongo_db.threads.find_one({'id': msg['thread_id']})
        if thread:
            slack_bot.post(thread_ts=thread['ts'], **msg_args)
        else:
            ts = slack_bot.post(**msg_args)
            mongo_db.threads.insert_one({'id': msg['thread_id'], 'ts': ts})


if __name__ == '__main__':
    main()

