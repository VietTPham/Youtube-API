#!/usr/bin/python

#apt-get install python-pip
import httplib2 #pip install httplib2
import os
import sys
import readline #to do backspace, for window use $pip install pyreadline
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
def add_new_playlist(youtube, playlist_title, playlist_description, playlist_privacy):
  playlists_insert_response = youtube.playlists().insert(
  part="snippet,status",
  body=dict(
    snippet=dict(
      title=playlist_title,
      description=playlist_description
    ),
    status=dict(
      privacyStatus=playlist_privacy
    )
  )
  ).execute()
  
  print "New playlist id: %s" % playlists_insert_response["id"]

def delete_playlist(youtube, playlist_id):
  playlists_delete_response = youtube.playlists().delete(
    id=playlist_id
  ).execute()
  
  print "Playlist delete successful."
  #print "New playlist id: %s" % playlists_insert_response["id"]

def get_own_scription_list ( youtube):
  next_token = ''
  token_list = ['']
  subscription_list = []
  while token_list[ len(token_list) - 1 ] is not None:
    subscription_query = youtube.subscriptions().list(
        part = 'snippet',
        mine = True,
        maxResults = 50,
        pageToken = token_list[ len(token_list) - 1 ],
        order = 'alphabetical',
        fields = "nextPageToken,items/snippet/resourceId/channelId"
        ).execute()
    if subscription_query.get('nextPageToken') is not None:
      token_list.append(subscription_query.get('nextPageToken'))
    else:
      token_list.append(None)
    for channel in subscription_query['items']:
      print channel.get('snippet').get('resourceId').get('channelId')
  return subscription_list
def menu():
  selection_num = raw_input("""
  Main Menu
  (1) Add new playlist
  (2) Delete a playlist
  (3) List user subscription
  (3) Search a channel for all video
  (3) List video in a playlist
  
  (10) Quit
  select: """)
  if (selection_num == "1"):
    print "\nAdd new playlist"
    title = raw_input ("Title of new playlist (required): ")
    description = raw_input ("Description of playlist (optional): ")
    privacy = raw_input("Privacy of playlist (public/(private)): ")
    if not privacy:
      privacy = "private"
    add_new_playlist(youtube, title, description, privacy)
  elif (selection_num == "2"):
    playlist_id = raw_input ("Playlist id: ")
    make_sure = raw_input ("Are you sure you want to remove the playlist (y/n)? ")
    if (make_sure == "y"):
      delete_playlist(youtube, playlist_id)
  elif (selection_num == "3"):
    my_subscription_list = get_own_scription_list ( youtube)
      
  elif (selection_num == "10"):
    print "\nQuitting program. Good Bye"
    exit()
  else:
    print "Invalid selection."
if __name__ == "__main__":
  youtube = get_authenticated_service()
  while (1):
    menu()