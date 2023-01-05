import os
import pickle
import json
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
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


def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages


def main():

    SCOPES, EMAIL = get_permissions()['scopes'], get_permissions()['email']
    service = gmail_authenticate(SCOPES=SCOPES)


if __name__ == '__main__':
    main()
