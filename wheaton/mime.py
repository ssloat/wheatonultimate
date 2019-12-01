import base64
import datetime
import email
import re

from wheaton import tags

def get_body(msg):
    parts = [p for p in msg.walk() if p.get_content_type() == 'text/plain']
    body = " ".join([p.get_payload(decode=True).decode('utf-8') for p in parts])
    body = remove_suffix(body)

    lens = [l for l in body.splitlines() if len(l) > 77 and ' ' in l]
    if lens:
        return body

    print("looks like fixed width")
    lines = body.splitlines()
    for n in range(len(lines) - 1):
        if re.match(r'.*[.?!:]"?$', lines[n]):
            lines[n] += "\n"
            continue

        match = re.match('(\S+)', lines[n+1])
        if not match or len(lines[n]) + len(match.group(1)) < 71:
            lines[n] += "\n"

        else:
            lines[n] += " " 

    return "".join(lines)


def remove_suffix(txt):
    lines = txt.splitlines()
    for n, line in list(enumerate(lines)):
        next_line = lines[n+1] if n < len(lines)-1 else ""
        if ((line == '-- ' and (next_line.startswith('---') or next_line.startswith('You received this message because ')))
                or (re.match(r'(>+ )?On ', line) 
                    and (line.endswith('wrote:') or next_line.endswith('wrote:'))
                )
                or re.match(r'Sent from my iPhone', line) 
                or re.match(r'Get Outlook for Android', line) 
                #or (line.startswith('> ') and all([l.startswith('> ') for l in lines[n+1:]]))
                or line.startswith('From: wheaton-ultimate@googlegroups.com')
                or line.startswith('To: wheaton-ultimate@googlegroups.com') 
                or re.match(r'-+ Original message', line) 
                #or re.match(r'-+$', line) 
                ):
                    
            print("Removing: %s" % lines[n:n+4])
            lines = lines[:n]
            break

    while lines and lines[-1] == "":
        lines = lines[:-1]

    body = "\n".join(lines)

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

