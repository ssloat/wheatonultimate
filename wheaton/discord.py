import os
import http.client

channels = {
    'soccer': (os.environ.get('DISCORD_SOCCER'), '@soccer'),
    'ultimate': (os.environ.get('DISCORD_ULTIMATE'), '@ultimate'),
    'social': (os.environ.get('DISCORD_SOCIAL'), '@social'),
    #'housing': (os.environ.get('DISCORD_HOUSING'), '@social'),
}


def post(topic, subject, from_, body, channel, **args):
    print(topic)
    if topic not in channels:
        return

    webhook, label = channels[topic]

    msg = "%sFrom %s (%s): %s\n%s" % (
        (label+' ' if channel else ''), 
        from_[0], from_[1], subject, body
    )

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
 

