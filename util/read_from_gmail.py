import email
import base64
import re
from wheaton import gmail, discord

searches = {
    'josiah': 'from:josiah.sledge@gmail.com after:2019/09/07', # before:2019/09/07'
    'jerrod': 'ifrom:jerrodtillotson@gmail.com after:2019/09/10',
    'long_body': 'from:labergsma "Friends. We are officially less than two months away from objectively the best month of
    the year.  April."',
}


def main():
    inbox = gmail.Inbox() #'wheatonultimate.slack@gmail.com')
    q = searches['josiah']
    mids = inbox.list(q)


    for mid in mids:
        msg = inbox.service.users().messages().get(userId='me', id=mid, format='raw').execute()
        #print(msg)
        msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        message = email.message_from_bytes(msg_str, policy=email.policy.default)
        body = message.get_payload()[0].get_payload()
        body = body.replace("=\r\n", '')
        #body = body.replace("=\n", '')
        #body = "\n".join([x.rstrip('=') for x in body.splitlines()])
        print(body)


if __name__ == '__main__':
    main()
