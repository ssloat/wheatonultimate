import email
import email.policy
import os

from wheaton import mime

def parse_content(msg, prefix=''):
    if msg.get_content_maintype() == 'multipart':
        print("%smulti" % prefix)
        for part in msg.get_payload():
            parse_content(part, "  "+prefix) 

    else:
        print("%s%s %s" % (prefix, msg.get_content_maintype(), msg.get_content_type()))
 
if __name__ == '__main__':
    d = '/home/kona/emails/2019'
    for f in os.listdir(d):
        with open("%s/%s" % (d, f), 'rb') as fh:
            txt = fh.read()
            msg = email.message_from_bytes(txt, policy=email.policy.default)
            #print(type(msg))
            #print(msg.get_body(preferencelist=('plain',))[:200])

            texts = [part for part in msg.walk() if part.get_content_type() == 'text/plain']
            if len(texts) == 1:
                continue

            #if msg.get_content_maintype() == 'text':
            #    continue

            #if len(msg.get_payload()) == 2 \
            #        and msg.get_payload()[0].get_content_maintype() == 'text' \
            #        and msg.get_payload()[1].get_content_maintype() == 'text':

            #    continue

            print(f)
            parse_content(msg)
            print(mime.get_body(msg))
            #for n, p in enumerate(texts):
            #    print("---------------------------------")
            #    print(n)
            #    print(p.get_payload())
            #for part in msg.walk():
            #    print(part.get_content_type())

