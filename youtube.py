#!/usr/bin/python

#apt-get install python-pip
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
      subscription_list.append(channel.get('snippet').get('resourceId').get('channelId'))
  return subscription_list
def get_own_watch_later_playlist_id (youtube):
  return youtube.channels().list(
      part = 'contentDetails',
      mine = True,
      fields = 'items/contentDetails/relatedPlaylists/watchLater'
    ).execute()['items'][0].get('contentDetails').get('relatedPlaylists').get('watchLater')

def get_playlist_video (youtube, playlist_id):
  next_token = ''
  token_list = ['']
  video_list = []
  while token_list[ len(token_list) - 1 ] is not None:
    playlist_query = youtube.playlistItems().list(
        part = 'snippet',
        maxResults = 50,
        pageToken = token_list[ len(token_list) - 1 ],
        playlistId = playlist_id,
        fields = "nextPageToken,items/snippet/publishedAt,items/snippet/resourceId/videoId"
        ).execute()
    if playlist_query.get('nextPageToken') is not None:
      token_list.append(playlist_query.get('nextPageToken'))
    else:
      token_list.append(None)
    for video in playlist_query['items']:
      #print video.get('snippet').get('publishedAt')
      #print video.get('snippet').get('channelId')
      #print video.get('snippet').get('resourceId').get('videoId')
      channel_id = youtube.videos().list(
        part = 'snippet',
        id = video.get('snippet').get('resourceId').get('videoId'),
        maxResults = 1,
        fields = 'items/snippet/channelId'
      ).execute()['items'][0].get('snippet').get('channelId')
      video_list.append({'publishedAt': video.get('snippet').get('publishedAt'),
                          'channelId': channel_id,
                          'videoId': video.get('snippet').get('resourceId').get('videoId')})
  return video_list
  #new_list = sorted(video_list, key=lambda k: k['videoId'].lower())
  #print "68",video_list[68]['videoId']
  #print len(video_list)
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
    #my_subscription_list = get_own_scription_list ( youtube)
    #watch_later_playlist_id = get_own_watch_later_playlist_id (youtube)
    #watch_later_video_list = get_playlist_video (youtube, watch_later_playlist_id)
    #get_50_video_per_channel = []
    
    #for channel in my_subscription_list:
    #  print channel
    #  for video in get_playlist_video (youtube, watch_later_playlist_id):
    #    print video
    #    get_50_video_per_channel.append(video)
    print "here"
    #for channel in my_subscription_list:
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
    
  elif (selection_num == "10"):
    print "\nQuitting program. Good Bye"
    exit()
  else:
    print "Invalid selection."
if __name__ == "__main__":
  youtube = get_authenticated_service()
  while (1):
    menu()