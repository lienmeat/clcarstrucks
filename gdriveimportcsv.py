import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import argparse
# flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
ap = argparse.ArgumentParser(parents=[tools.argparser])
ap.add_argument('csvfilename', metavar='csvfilename', type=str, help=".csv file to upload/import to g sheets without the extention (.csv)")
flags = ap.parse_args()

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-upload.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def list10():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(
        pageSize=10,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))

def uploadCSV(csvfilename):
    DST_FILENAME = flags.csvfilename
    SRC_FILENAME = DST_FILENAME + '.csv'
    SHT_MIMETYPE = 'application/vnd.google-apps.spreadsheet'
    CSV_MIMETYPE = 'text/csv'

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    # Import CSV file to Google Drive as a Google Sheets file
    METADATA = {'name': DST_FILENAME, 'mimeType': SHT_MIMETYPE}
    #first, see if the file exists already
    lrsp = drive_service.files().list(pageSize=1, fields="files(id)", q="name='"+DST_FILENAME+"' and trashed=false", ).execute()
    items = lrsp.get('files', [])
    if not items:
        print('No files found.')
        rsp = drive_service.files().create(body=METADATA, media_body=SRC_FILENAME).execute()
    else:
        print('File:')
        print('{0}'.format(items[0]['id']))
        #since this file exists already, if we wish to import without appending, we must clear the document.
        #At least, I can't find a way to get it to overwrite on update, unless it's a metadata value
        #I can't find documented
        sheets_service = discovery.build('sheets', 'v4', http=http)
        #hopefully this range is suitable
        range_='A1:Z5000'
        body_ = {}
        srsp = sheets_service.spreadsheets().values().clear(spreadsheetId=items[0]['id'], range=range_, body=body_).execute()

        rsp = drive_service.files().update(fileId=items[0]['id'], body=METADATA, media_body=SRC_FILENAME).execute()

    if rsp:
        print('Imported %r to %r (as %s)' % (SRC_FILENAME, DST_FILENAME, rsp['mimeType']))

def main():
    # list10()
    uploadCSV("clcarstrucks")

if __name__ == '__main__':
    main()
