import base64
import datetime
import email
import re

from wheaton import tags

def get_body(msg):
    parts = [part for part in msg.walk() if part.get_content_type() == 'text/plain']
    body = " ".join([remove_suffix(p.get_payload()) for p in parts])

    lens = [l for l in body.splitlines() if len(l) > 75]
    if not lens:
        print("looks like fixed width")
        lines = body.splitlines()
        for n in range(len(lines) - 1):
            if re.match(r'.*[.?!]$', lines[n]):
                lines[n] += "\n"
                continue

            match = re.match('(\S+)', lines[n+1])
            if not match or len(lines[n]) + len(match.group(1)) < 75:
                lines[n] += "\n"

            else:
                lines[n] += " " 

        body = "".join(lines)

    return body


def remove_suffix(txt):
    txt = txt.replace("=\r\n", '').replace("=\n", '')
    lines = txt.splitlines()
    for n, line in list(enumerate(lines)):
        next_line = lines[n+1] if n < len(lines)-1 else ""
        if line == '-- ' or line == '--=20' \
                or line.startswith('From: wheaton-ultimate@googlegroups.com') \
                or line.startswith('To: wheaton-ultimate@googlegroups.com') \
                or re.match(r'(> )?On .* wrote:', line) \
                or (re.match(r'(> )?On ', line) and next_line.endswith('wrote:')) \
                or re.match(r'-+ Original message', line) \
                or re.match(r'-+$', line):
                    
            lines = lines[:n]
            break

    body = "\n".join(lines)
    body = body.replace(' Sent from my iPhone', '')

    patterns = [
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

