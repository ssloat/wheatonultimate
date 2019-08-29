import imaplib
import email
import re
import chardet
import datetime
import time
import urllib
from html.parser import HTMLParser
from email.parser import BytesParser, Parser
from email.policy import default

from wheaton import tags


class Inbox(object):
    def __init__(self, user, pwd):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(user, pwd)
        self.mail.select('inbox')
        
    def search(self, date):
        result, data = self.mail.uid('search', None, "(SENTSINCE %s)" % date.strftime('%d-%b-%Y'))
        return set(data[0].split())

    def fetch_message(self, uid):
        result, data = self.mail.uid('fetch', uid, '(X-GM-THRID RFC822)')
        thread_id = re.match('.*X-GM-THRID (\d+)', data[0][0].decode('utf-8')).group(1)
        raw_email = data[0][1]

        #return thread_id, email.message_from_string(raw_email.decode('utf-8'))
        message = Parser(policy=default).parsestr(raw_email.decode('utf-8'))
        if message is None:
            print("Couldn't parse email %s: %s" % (uid, raw_email))
        return thread_id, message

    def process_uid(self, uid):
        thread_id, message = self.fetch_message(uid)

        if not message:
            return
        
        if 'List-ID' not in message:
            print("Not to google group: %s" % uid)
            return

        #txt = message.get_payload(decode=True)
        txt = message.get_body(['plain', 'html']).get_payload(decode=True).decode('utf-8')
        if not txt:
            txt = '<Could not parse message>'

        body = self.parse_body(txt)

        subj = message['Subject'].replace('[wheaton-ultimate] ', '')
        msg = {
            'uid': uid,
            'thread_id': thread_id,
            'date': datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(email.utils.parsedate_tz(message['Date']))
            ),
            'group': message['List-ID'][1:-1].replace('.googlegroups.com', ''),
            'from': message['From'],
            'body': body,
            'subject': "".join(subj.splitlines()),
        }

        msg['tags'] = tags.msg_tags(msg)

        if msg['group'] == 'wheaton-soccer':
            msg['topic'] = 'soccer'
        elif 'ultimate' in msg['tags']:
            msg['topic'] = 'ultimate'
        elif 'housing' in msg['tags']:
            msg['topic'] = 'housing'
        else:
            msg['topic'] = 'social'

        return msg

    def parse_body(self, txt):
        lines = txt.splitlines()
        for n, line in list(enumerate(lines)):
            if line == '-- ' or line.startswith('From: wheaton-ultimate@googlegroups.com') or re.match(r'-+$', line):
                lines = lines[:n]
                break

        body = " ".join(lines)
        body = body.replace(' Sent from my iPhone', '')

        patterns = [
            '(.*?)( >)?\s+On .* wrote: .*', 
            r'(.*?)From: wheaton-ultimate@googlegroups.com', 
        ]
        for p in patterns:
            match = re.match(p, body)
            if match:
                return match.group(1)

        return body


def get_text(msg):
    text = ""
    if msg.is_multipart():
        html = None
        for part in msg.walk():
            payload = part.get_payload(decode=True)
            if not payload:
                continue

            if part.get_content_charset() is None:
                charset = chardet.detect(part)['encoding']
            else:
                charset = part.get_content_charset()

            #print(payload)
            #print(type(payload))
            #x = unicode(payload, str(charset), "ignore")
            #x = x.encode('utf8','replace')
            x = payload.decode('utf-8')
            
            if part.get_content_type() == 'text/plain':
                text = x

            elif part.get_content_type() == 'text/html':
                html = x

        if text != "": return text.strip()
        return text.strip() if html is None else html.strip()

    else:
        print(msg.get_payload(decode=True))
        #text = unicode(
        #    msg.get_payload(decode=True),
        #    msg.get_content_charset(),
        #    'ignore'
        #).encode('utf8','replace')

        return text.strip()


