import json
import logging
import os
import re
import requests
import time

from discord_webhook import DiscordWebhook, DiscordEmbed

channels = {
    'soccer': (os.environ.get('DISCORD_SOCCER'), '<@&613218877165535232> '),
    'ultimate': (os.environ.get('DISCORD_ULTIMATE'), '<@&613215568274915341> '),
    'social': (os.environ.get('DISCORD_SOCIAL'), '<@&613728159069634560> '),
    'housing': (os.environ.get('DISCORD_HOUSING'), '<@&616489369544687616> '),

    'testing': (os.environ.get('DISCORD_TESTING'), '<@&618295398620069909> '),
}

# https://birdie0.github.io/discord-webhooks-guide/discord_webhook.html
def requests_post(url, json, files=None):
    if bool(files) is False:
        response = requests.post(url, json=json)
    else:
        files['payload_json'] = (None, json.dumps(json))
        response = requests.post(url, files=files)

    if response.status_code in [200, 204]:
        logging.info("Webhook executed")

    elif response.status_code == 429:
        millis = json.loads(resp.content.decode("utf-8"))['retry_after']
        secs = int(millis / 1000) + 1
        logging.info("Sleep %d" % secs)
        time.sleep(secs)

    else:
        logging.error('status code %s: %s' % (
            response.status_code, response.content.decode("utf-8"))
        )


class Webhook(DiscordWebhook):
    def execute(self):
        """
        execute Webhook
        :return:
        """
        #requests_post(self.url, self.json, self.files)
        if bool(self.files) is False:
            response = requests.post(self.url, json=self.json, proxies=self.proxies)
        else:
            self.files['payload_json'] = (None, json.dumps(self.json))
            response = requests.post(self.url, files=self.files, proxies=self.proxies)

        if response.status_code in [200, 204]:
            logging.debug("Webhook executed")

        elif response.status_code == 429:
            millis = json.loads(resp.content.decode("utf-8"))['retry_after']
            secs = int(millis / 1000) + 1
            logging.info("Sleep %d" % secs)
            time.sleep(secs)

        else:
            logging.error('status code %s: %s' % (response.status_code, response.content.decode("utf-8")))


def adjust_body(body):
    def repl(m):
        return "[%s](%s)" % (m.group(1), m.group(2)[1:-1])

    return re.sub(r"(\S+)\s?(<http\S+?>)", repl, body)


def post(topic, subject, from_, body, channel, attachments=None):
    attachments = attachments or []
    print(topic)
    if topic not in channels:
        return

    webhook_url, label = channels[topic]
    webhook_url = "https://discordapp.com/api/webhooks/"+webhook_url

    subject = subject.replace('||', '//')
    body = adjust_body(body)
    body_parts = split_body(body, 1900-len(subject))
    if channel:
        body_parts[0] += "\n%s" % label

    for i, part in enumerate(body_parts):
        content = "> **%s**\n%s" % (subject, part)
        hook = Webhook(url=webhook_url, content=content, username=from_[0])

        if i == len(body_parts)-1:
            hook.content += "\n%s" % from_[1]
            for filename, a in attachments:
                hook.add_file(file=a, filename=filename)

        hook.execute()

        time.sleep(2) # discord doesn't like you posting too aggresively


def split_body(body, l=1950):
    parts = []
    while len(body) > l:
        n = l
        while body[n] != ' ':
            n -= 1

        parts.append(body[:n])
        body = body[n:]

    if body:
        parts.append(body)

    for i in range(len(parts)):
        if i > 0:
            parts[i] = '...%s' % parts[i]

        if i != len(parts) - 1:
            parts[i] += '...'

    return parts

