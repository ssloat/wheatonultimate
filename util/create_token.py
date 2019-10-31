from __future__ import print_function
import pickle
import email
import json
import base64
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file( 'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    query = 'list:wheaton-ultimate@googlegroups.com -subject:(-{Abridged "Message Pending}) after:2019/08/25'
    response = service.users().messages().list(userId='wheatonultimate.slack@gmail.com', q=query).execute()

    """
    print(response)
    {
        'messages': [
            {'id': '16cefb111b7b9fc7', 'threadId': '16cefb111b7b9fc7'}, {'id': '16ce35e7bf16e788', 'threadId': '16ce35e7bf16e788'}, 
            {'id': '16cd002ebb039b85', 'threadId': '16cce823cab8d1e8'}, {'id': '16cce823cab8d1e8', 'threadId': '16cce823cab8d1e8'}, 
            {'id': '16ccde480717ac5b', 'threadId': '16ccde480717ac5b'}
        ],
        'resultSizeEstimate': 5
    }
    """

    message = service.users().messages().get(userId='wheatonultimate.slack@gmail.com', id=response['messages'][0]['id'], format='raw').execute()
    with open('/tmp/json.out', 'w') as fh:
        json.dump(message, fh)

    #print(get_body(message))

def get_body(message):
    try:
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)
        messageMainType = mime_msg.get_content_maintype()
        if messageMainType == 'multipart':
            for part in mime_msg.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
                return ""
        elif messageMainType == 'text':
            return mime_msg.get_payload()

    except errors.HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()
