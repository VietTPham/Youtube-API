#!/usr/bin/python

#apt-get install python-pip
import httplib2 #pip install httplib2
import os
import sys
#install api
#pip install --upgrade google-api-python-client
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    message=MISSING_CLIENT_SECRETS_MESSAGE,
    scope=YOUTUBE_READ_WRITE_SCOPE)
  
  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()
  
  if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, storage, flags)
  
  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

# This code creates a new, private playlist in the authorized user's channel.
#def add_new_playlist()
#playlists_insert_response = youtube.playlists().insert(
#  part="snippet,status",
#  body=dict(
#    snippet=dict(
#      title="Test Playlist",
#      description="A private playlist created with the YouTube API v3"
#    ),
#    status=dict(
#      privacyStatus="private"
#    )
#  )
#).execute()
#
#print "New playlist id: %s" % playlists_insert_response["id"]


if __name__ == "__main__":
  #youtube = get_authenticated_service()
  playlist = raw_input("Enter the appointment time (y\\n): ")
  if (playlist == "y"):
    print "yes"
  #    add_video_to_playlist(youtube,"yszl2oxi8IY","PL2JW1S4IMwYubm06iDKfDsmWVB-J8funQ")