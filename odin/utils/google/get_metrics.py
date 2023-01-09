import base64
import email
import os
import pickle
import json
import re

import pandas as pd
import requests
from zipfile import ZipFile
import warnings
from datetime import date
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# todo: plan is to ---- connect gmail api, read emails on 1st of month, search for hootsuite, download hootsuite
#  twitter metrics, log metrics into social media airtable.


def get_permissions():

    cp = os.path.expanduser('~/.cred/google/gmail.json')
    with open(cp, 'r') as f:
        data = json.load(f)
    return data


def get_creds():

    cp = os.path.expanduser('~/.cred/google/credentials.json')
    with open(cp, 'r') as f:
        data = json.load(f)
    return data


def gmail_authenticate(SCOPES):
    creds = None
    cp = os.path.expanduser('~/.cred/google/credentials.json')
    tp = os.path.expanduser('~/.cred/google/token.pickle')
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists(tp):
        with open(tp, "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cp, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open(tp, "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


# def search_messages(service, query):
#     result = service.users().messages().list(userId='me',q=query).execute()
#     messages = [ ]
#     if 'messages' in result:
#         messages.extend(result['messages'])
#     while 'nextPageToken' in result:
#         page_token = result['nextPageToken']
#         result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
#         if 'messages' in result:
#             messages.extend(result['messages'])
#     return messages

def search_messages(service, user_id, search_string):
    try:
        # service.users inbox.do stuff (list, messages).execute()
        search_id = service.users().messages().list(userId=user_id, q=search_string).execute()
        n_results = search_id['resultSizeEstimate']

        lst = []
        if n_results > 0:
            message_ids = search_id['messages']
            for mid in message_ids:
                lst.append(mid['id'])
            return lst
        else:
            print(f'There were zero results for search parameters: {search_string}')

    except:
        print('error')


def get_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_raw)
        return mime_msg

    except:
        print('error')


def get_dl_link_from_msg(mime_msg):
    soup = BeautifulSoup(str(mime_msg), features='html.parser')
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
        links.append(link.get('href'))
    return links[0]


def main():
    user_id = 'me'
    DATE = date.today()
    DIRECTORY = os.path.expanduser('~/data/odin/social_media/hootsuite/monthly_metrics')
    SCOPES, EMAIL = get_permissions()['scopes'], get_permissions()['email']
    service = gmail_authenticate(SCOPES=SCOPES)
    msg_ids = search_messages(service, user_id=user_id, search_string='label:10_monthly_metrics')

    mime_msg = get_message(service, user_id='me', msg_id=msg_ids[0])


    dl_link = get_dl_link_from_msg(mime_msg)
    resp = requests.get(url=dl_link)
    f = resp.content
    # todo: write function to open zip, read csv, an save to AT social media.

    #### SAVE THE ZIP FILE
    filepath = os.path.join(DIRECTORY, f'{DATE}_monthly_metrics.zip')
    if not os.path.exists(filepath):
        with open(filepath, 'wb') as fp:
            fp.write(f)
    else:
        print(f'{filepath} already exists')


    #### OPEN AND READ THE CSV IN THE ZIP FILE
    with ZipFile(filepath) as zf:
        filenames = zf.namelist()
        # fname = os.path.join(DIRECTORY, filenames[0])
        fname = filenames[0]

        with zf.open(fname) as infile:

            df = pd.read_csv(infile)
    print(df)



if __name__ == '__main__':
    main()
