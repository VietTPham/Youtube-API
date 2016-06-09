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

#authorizing api key
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

#delete playlist smartly
def delete_playlist(youtube):
  print '\n\n  Delete playlist menu'
  playlistId_list = []
  for playlist in get_my_playlist ( youtube ):
    #prevent special playlist from adding to list
    if ( playlist['title'] in ( 'favorites', 'likes', 'uploads', 'watchHistory', 'watchLater')):
      continue
    else : 
      playlistId_list.append ( playlist )
  
  if ( len(playlistId_list) == 0 ) :
    print "No valid playlist to delete"
    return
  else :
    playlistId_list = sorted (playlistId_list, key=lambda k: k['title'].lower())
    while True:
      
      for i in range(0, len(playlistId_list)):
        print "  " + str ( i ) + ':', playlistId_list[i]['title']
      print '  q: return to menu.'
      input = raw_input('Select a playlist to delete [1-'+str(len(playlistId_list))+']: ')
      if ( input in ( 'q', 'Q' )):
        return
      try:
        int ( input )
      except ValueError:
        print 'ERROR: Invalid input.\n'
      else:
        if (( int ( input ) < 1  ) or ( int ( input ) >= len ( playlistId_list ))):
          print 'ERROR: Invalid input.\n'
        else :
          sure_check = raw_input('Are you sure you want to delete the playlist '+str(playlistId_list[int(input)]['title']) + ' (y/[n])? ') or 'n'
          print sure_check
          if ( sure_check.lower() == 'y' ):
            print 'Deleting playlist ' + str(playlistId_list[int(input)]['title'])
            youtube.playlists().delete(id = playlistId_list[int(input)]['playlistId']).execute()
            return
          elif (sure_check.lower() == 'n' ):
            return
          else : 
            'ERROR: Invalid input.\n'

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
                          'title': u'watchLater',
                          'playlistId' : playlist_1.get('watchLater')
                        })
  playlistId_list.append({
                          'title': u'watchHistory',
                          'playlistId' : playlist_1.get('watchHistory')
                        })
  playlistId_list.append({
                          'title': u'likes',
                          'playlistId' : playlist_1.get('likes')
                        })
  playlistId_list.append({
                          'title': u'favorites',
                          'playlistId' : playlist_1.get('favorites')
                        })
  playlistId_list.append({
                          'title': u'uploads',
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
                fields="nextPageToken,items/id,items/snippet/title"
              ).execute()
    token = playlist_2.get('nextPageToken')
    for playlist in playlist_2['items']:
      playlistId_list.append({
                              'title' : playlist.get('snippet').get('title'),
                              'playlistId' : playlist.get('id')
                            })
    if token == None:
      return playlistId_list

#return a dictionary with 'channelTitle' and 'channelId'
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
      channelId_list.append({ 'channelTitle': channel.get('snippet').get('title'), 
                              'channelId': channel.get('snippet').get('resourceId').get('channelId')
                           })
    token = channelId.get('nextPageToken')
    if token == None:
      return channelId_list

#return dictionary with 'id', 'publishedAt', 'title', and 'channelTitle' 
def get_video (youtube, videoId) :
  videoId_list = []
  videoId = youtube.videos().list(
                      part = 'snippet',
                      id = videoId,
                      fields = "nextPageToken,items/id,items/snippet/publishedAt,items/snippet/title,items/snippet/channelTitle"
                      ).execute()
  for video in videoId['items']:
    videoId_list.append({ 'id': video.get('id'),
                          'publishedAt': video.get('snippet').get('publishedAt'),
                          'title': video.get('snippet').get('title'),
                          'channelTitle': video.get('snippet').get('channelTitle')
                        })
  return videoId_list
  
#return dictionary with 'id', 'publishedAt', 'title', and 'channelTitle'
def get_playlist_video_list (youtube, playlist_id):
  videoId_list = []
  videoId_str = ''
  token = None
  while True:
    videoId = youtube.playlistItems().list(
                      part = 'snippet',
                      maxResults = 50,
                      pageToken = token,
                      playlistId = playlist_id,
                      fields = "nextPageToken,items/snippet/resourceId/videoId"
                      ).execute()
    token = videoId.get('nextPageToken')
    for video in videoId['items']:
      #temporary video list that store videoID
      #playlistItems does not give details such as title of the video, channelTitle, and original publishedAt date 
      videoId_str += str(video.get('snippet').get('resourceId').get('videoId')) + ','
    if ( token == None ):
      return get_video ( youtube, videoId_str )

def get_channel_video_list ( youtube, channelId):
  print 'stuff'
def menu():
  selection_num = raw_input("""
  Main Menu
  (1) Add new playlist
  (2) Delete a playlist
  (3) List user subscription
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
    delete_playlist ( youtube )
  elif (selection_num == "3"):
    #print get_my_subscriptions_list ( youtube )
    #print get_my_playlist ( youtube )
    print get_playlist_video_list ( youtube, 'WLO2sY8dA4DODmOojyEIxlqw')
    #get_channel_video_list ( youtube, 'UCXuqSBlHAE6Xw-yeJA0Tunw')
  elif selection_num in ('10', 'Q', 'q'):
    print "\nQuitting program. Good Bye"
    exit()
  else:
    print "Invalid input."
    return

if __name__ == "__main__":
  youtube = get_authenticated_service()
  while True:
    menu()
