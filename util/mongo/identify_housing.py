#!/usr/bin/python

import os
import re
import datetime
from pymongo import MongoClient
from functools import reduce


# housing emails
#  list:wheaton-ultimate@googlegroups.com subject:+{rent tenant housing roommate} 

if __name__ == '__main__':
    mongo = MongoClient(os.environ.get('MONGO_DB_URI'))
    slack = mongo['slack']

    #for thread in slack['threads'].find():
    #    print thread

    #for email in slack['emails'].find({'thread_id': '1634433431354119519'}):
    #    print email

    threads = {}
    for email in slack['emails'].find({'date': {'$gt': datetime.datetime(2018, 1, 1)}}):
        subject = email['subject'].lower()
        if any([x in subject for x in ('rent', 'tenant', 'housing', 'roommate')]):
            #print email['subject']
            #print email['body']
            body = email['body'].replace("\n", " ")
            body = re.sub(r'[^a-zA-Z\d\s.:]', '', body).lower()
            words = set([
                w for w in body.split() if not w.startswith('http') and len(w) > 3
            ])
            threads[email['thread_id']] = words

    all_words = reduce(lambda x, y: x | y, threads.values(), set())

    count = float(len(threads.keys()))

    freqs = []
    for word in all_words:
        matches = [tid for tid, words in threads.items() if word in words]

        freqs.append((word, len(matches) / count))
    
    for x in sorted(freqs, key=lambda x: x[1]):
        print(x)
