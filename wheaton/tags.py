import re


def has_time(s):
    return re.search(r'(\d+(:\d+)? *[ap]m?)', s) or re.search(r'(\d+:\d\d)', s) or re.search(r' at \d+', s)

def msg_tags(msg):
    subject = msg['subject'].lower()
    body = msg['body'].lower()

    tags = []
    if has_time(msg['subject']):
        tags.append('event')
    elif 'looking for ' in subject:
        tags.append('looking for')

    if msg['group'] == 'wheaton-housing':
        tags.append('housing')
    elif msg['group'] == 'wheaton-soccer':
        tags.append('soccer')
    elif msg['group'] == 'wheaton-ultimate-frisbee':
        tags.append('ultimate')


    return tags


