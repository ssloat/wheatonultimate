import datetime
import email
import os
import logging

from pymongo import MongoClient

from wheaton import gmail, discord

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
    )

    mongo_db = MongoClient(os.environ.get('MONGO_DB_URI'), retryWrites=False)['slack']
    inbox = gmail.Inbox()

    date = datetime.date.today() - datetime.timedelta(days=2)

    query = " ".join([
        'list:{%s}' % ' '.join(['wheaton-%s@googlegroups.com' % g for g in ['ultimate', 'soccer', 'housing', 'ultimate-frisbee']]),
        'subject:(-"Message Pending)',
        'after:%s' % date.strftime('%Y/%m/%d'),
    ])

    print(query)
    mids = inbox.list(query)
    mids = [mid for mid in mids if not mongo_db.emails.find_one({'id': mid})]

    for msg in inbox.get(mids):
        print(dict((k, msg[k]) for k in ('from', 'subject', 'body')))
        mongo_db.emails.insert_one(dict((k, v) for k, v in msg.items() if k != 'attachments')) 

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
        if not thread:
            mongo_db.threads.insert_one({'id': msg['thread_id']})


if __name__ == '__main__':
    main()

