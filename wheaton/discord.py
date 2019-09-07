import os
import re
from discord_webhook import DiscordWebhook, DiscordEmbed

channels = {
    'soccer': (os.environ.get('DISCORD_SOCCER'), '<@&613218877165535232> '),
    'ultimate': (os.environ.get('DISCORD_ULTIMATE'), '<@&613215568274915341> '),
    'social': (os.environ.get('DISCORD_SOCIAL'), '<@&613728159069634560> '),
    'housing': (os.environ.get('DISCORD_HOUSING'), '<@&616489369544687616> '),

    'testing': (os.environ.get('DISCORD_TESTING'), '<@&618295398620069909> '),
}


def post(topic, subject, from_, body, channel, attachments):
    print(topic)
    if topic not in channels:
        return

    webhook_url, label = channels[topic]
    webhook_url = "https://discordapp.com/api/webhooks/"+webhook_url

    subject = subject.replace('||', '//')

    urls_in_body = []
    def repl(m):
        urls_in_body.append(m.group(2)[1:-1])
        return "[%s](%s)" % (m.group(1), m.group(2)[1:-1])

    body = re.sub(r'(\S+)\s+(<https?:\S+?>)', repl, body)

    content = "%s %s " % (label, from_[1]) if channel else from_[1]
    hook = DiscordWebhook(url=webhook_url, content=content)

    body_parts = split_body(body)

    embed = DiscordEmbed(title=subject, description=body_parts[0], color=242424)
    embed.set_author(name=from_[0]) #, url='author url', icon_url='author icon url')
    hook.add_embed(embed)

    for bp in body_parts[1:]:
        hook.add_embed(DiscordEmbed(description=bp, color=242424))

    hook.execute()

    for filename, a in attachments:
        h = DiscordWebhook(url=webhook_url)
        h.add_file(file=a, filename=filename)
        h.execute()


def split_body(body):
    parts = []
    while len(body) > 2048:
        n = 2048
        while body[n] != ' ':
            n -= 1

        parts.append(body[:n])
        body = body[n:]

    if body:
        parts.append(body)

    return parts

