from __future__ import print_function
import pickle
import email
import base64
import os.path
from googleapiclient.discovery import build

from wheaton import tags, mime

class Inbox(object):
    def __init__(self):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

        self.service = build('gmail', 'v1', credentials=creds)

    def list(self, query):
        #query = " ".join([
        #    'list:{wheaton-ultimate@googlegroups.com wheaton-soccer@googlegroups.com}',
        #    '-subject:(-"Message Pending)',
        #    'after:%s' % date.strftime('%Y/%m%d'),
        #])
        resp = self.service.users().messages().list(userId='me', q=query).execute()
        msg_ids = resp.get('messages', [])
        while 'nextPageToken' in resp:
            token = resp['nextPageToken']
            resp = self.service.users().messages().list(userId='me', q=query, pageToken=token).execute()

            msg_ids.extend(resp.get('messages', []))

        return [m['id'] for m in msg_ids]

    def get(self, mids):
        if not isinstance(mids, list):
            mids = [mids]

        messages = {}
        for mid in mids:
            msg = self.service.users().messages().get(userId='me', id=mid, format='raw').execute()
            msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
            message = email.message_from_bytes(msg_str, policy=email.policy.default)

            messages[int(msg['internalDate'])] = mime.process_msg(message, mid, msg['threadId'])
    
        return [messages[k] for k in sorted(messages)]

