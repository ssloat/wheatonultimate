import os
import email
import email.policy

from wheaton import mime, discord

def main():
    d = '/home/kona/emails/2019'
    fn = '1566434505000.16cb6c5e691b1a0a'
    with open("%s/%s" % (d, fn), 'rb') as fh:
        b = fh.read()
        message = email.message_from_bytes(b, policy=email.policy.default)
        body = mime.get_body(message)
        body = discord.adjust_body(body)

        print("---------------------------------------")
        print("--- %s" % fn)
        print(body)
        print("---------------------------------------")


if __name__ == '__main__':
    main()



