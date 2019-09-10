import base64
import datetime
import email
import re

from wheaton import tags

def get_body(msg):
    parts = [part for part in msg.walk() if part.get_content_type() == 'text/plain']
    return " ".join([remove_suffix(p.get_payload()) for p in parts])


def remove_suffix(txt):
    lines = txt.splitlines()
    for n, line in list(enumerate(lines)):
        if line == '-- ' or line == '--=20' \
                or line.startswith('From: wheaton-ultimate@googlegroups.com') \
                or re.match(r'-+$', line):
                    
            lines = lines[:n]
            break

    body = "\n".join(lines)
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

def process_msg(message, mid, thread_id):
    body = get_body(message)
    subj = message['Subject'].replace('[wheaton-ultimate] ', '')

    attachments = []
    for part in message.walk():
        if part.get_content_type() == 'image/jpeg':
            content = base64.urlsafe_b64decode(part.get_payload().encode('UTF-8'))
            attachments.append((part.get_filename(), content))

    msg = {
        'id': mid,
        'thread_id': thread_id,
        'date': datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(email.utils.parsedate_tz(message['Date']))
        ),
        'group': message['List-ID'][1:-1].replace('.googlegroups.com', ''),
        'from': message['From'],
        'body': body,
        'subject': "".join(subj.splitlines()),
        'attachments': attachments,
    }

    msg['tags'] = tags.msg_tags(msg)
    msg['topic'] = topic(msg)

    return msg

def topic(msg):
    if msg['group'] == 'wheaton-soccer':
        return 'soccer'
    elif 'ultimate' in msg['tags']:
        return 'ultimate'
    elif 'housing' in msg['tags']:
        return 'housing'
    else:
        return 'social'

