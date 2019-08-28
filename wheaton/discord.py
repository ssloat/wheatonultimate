import os
import http.client

channels = {
    'wheaton-soccer': (os.environ.get('DISCORD_SOCCER'), '@soccer'),
    'wheaton-ultimate': (os.environ.get('DISCORD_ULTIMATE'), '@ultimate'),
}


def post(group, subject, from_, body, channel, **args):
    print(group)
    if group not in channels:
        return

    webhook, label = channels[group]

    msg = "%sFrom %s: %s\n%s" % ((label+' ' if channel else ''), from_, subject, body)

    send_msg(webhook, msg)
 

def send_msg(webhook, msg):
    boundary = '----:::BOUNDARY:::'
    formdata = "\r\n".join([
        "--%s" % boundary,
        'Content-Disposition: form-data; name="content"',
        "",
        msg,
        "--%s--" % boundary,
    ])

    webhookurl = "https://discordapp.com/api/webhooks/"+webhook
    connection = http.client.HTTPSConnection("discordapp.com")
    connection.request("POST", webhookurl, formdata, {
        'content-type': "multipart/form-data; boundary=%s" % boundary,
        'cache-control': "no-cache",
    })

    response = connection.getresponse()
    result = response.read()
  
    print( result.decode("utf-8") )
 

