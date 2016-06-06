#!/usr/bin/python

#yum install python-pip
#pip install --upgrade pip
import httplib2 #pip install httplib2
import os
import sys
import readline #to do backspace, for window use $pip install pyreadline
import operator #for sorting dictionary
#install api
#pip install --upgrade google-api-python-client
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow #easy_install argparse


def get_authenticated_service():
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

def get_my_playlist (youtube):
  playlistId_list = []
  #get playlist for special playlist
  playlist_1 = youtube.channels().list(
                part = 'contentDetails',
                mine = True,
                fields = 'items/contentDetails/relatedPlaylists'
              ).execute()['items'][0].get('contentDetails').get('relatedPlaylists')
  #don't really know a better way to do the 5 lines below
  playlistId_list.append({
                          'title': 'watchLater',
                          'playlistId' : playlist_1.get('watchLater')
                        })
  playlistId_list.append({
                          'title': 'watchHistory',
                          'playlistId' : playlist_1.get('watchHistory')
                        })
  playlistId_list.append({
                          'title': 'likes',
                          'playlistId' : playlist_1.get('likes')
                        })
  playlistId_list.append({
                          'title': 'favorites',
                          'playlistId' : playlist_1.get('favorites')
                        })
  playlistId_list.append({
                          'title': 'uploads',
                          'playlistId' : playlist_1.get('uploads')
                        })
  
  #user created playlist
  token = None
  while True:
    playlist_2 = youtube.playlists().list(
                part="snippet",
                maxResults=1,
                mine=True,
                pageToken=token,
                fields="nextPageToken,items/snippet/channelId,items/snippet/title"
              ).execute()
    token = playlist_2.get('nextPageToken')
    for playlist in playlist_2['items']:
      playlistId_list.append({
                              'title' : playlist.get('snippet').get('title'),
                              'playlistId' : playlist.get('snippet').get('channelId')
                            })
    if token == None:
      return playlistId_list
    
def get_my_subscriptions_list (youtube): 
  channelId_list = []
  token = None
  while True:
    channelId = youtube.subscriptions().list(
              part = 'snippet',
              maxResults = 50,
              mine = True,
              pageToken = token,
              fields = 'nextPageToken,items/snippet/title,items/snippet/resourceId/channelId').execute()
    for channel in channelId.get('items'):
      channelId_list.append({'title': channel.get('snippet').get('title'), 
                           'channelId': channel.get('snippet').get('resourceId').get('channelId')})
    token = channelId.get('nextPageToken')
    if token == None:
      return channelId_list
    
  
def get_playlist_video_list (youtube, playlist_id):
  videoId_list = []
  token = None
  while True:
    videoId = youtube.playlistItems().list(
                      part = 'snippet',
                      maxResults = 50,
                      pageToken = token_list[ len(token_list) - 1 ],
                      playlistId = playlist_id,
                      fields = "nextPageToken,items/snippet"
                      ).execute()

def menu():
  selection_num = raw_input("""
  Main Menu
  (1) Add new playlist
  (2) Delete a playlist
  (3) List user subscription
  (4) Get watchLater ID
  (5) List video in watchLater playlist
  (6) List all subscription
  (10/q) Quit
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
    search_query = youtube.search().list(
        part = 'snippet',
        channelId = 'UCWJQeV1fVrBnUXHtWmfUUfA',
        maxResults = 50,
        order = 'date',
        fields = 'items/id/videoId,items/snippet/publishedAt'
      ).execute().get('items')
    for i in search_query:
      print i.get('snippet').get('publishedAt')
      print i.get('id').get('videoId')
    #print search_query[0].get('snippet')
  elif (selection_num == "4"):
    print get_own_watchLater_playlist_id(youtube)
    print get_own_watchHistory_playlist_id(youtube)
  elif (selection_num == "5"):
    get_playlist_token(youtube, get_own_watchLater_playlist_id(youtube))
  elif (selection_num == "6"):
    
    #get_my_subscriptions_list ( youtube )
    get_my_playlist ( youtube )
  elif (selection_num == "10" or "Q" or "q"):
    print "\nQuitting program. Good Bye"
    exit()
  else:
    print "Invalid selection."

if __name__ == "__main__":
  youtube = get_authenticated_service()
  while (1):
    menu()
