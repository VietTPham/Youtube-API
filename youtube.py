#!/usr/bin/python -x

#yum install python-pip
#pip install --upgrade pip
#pip install argparse
#pip install httplib2
#install api
#pip install --upgrade google-api-python-client
import httplib2
import os
import sys
import readline #to do backspace, for window use $pip install pyreadline
import operator #for sorting dictionary
import unicodedata
import datetime
import time
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
def add_new_playlist(youtube):
  print "\nAdd new playlist"
  playlist_title = raw_input ("Title of new playlist (required): ")
  playlist_description = raw_input ("Description of playlist (optional): ")
  playlist_privacy = raw_input("Privacy of playlist (public/(private)): ")
  if not playlist_privacy:
    playlist_privacy = "private"
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
      for i in range(1, len(playlistId_list)):
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

#return title and playlistId
def get_my_playlist (youtube):
  print "  Getting my playlist"
  playlistId_list = []
  #get playlist for special playlist
  playlist_1 = youtube.channels().list(
                part = 'contentDetails',
                mine = True,
                fields = 'items/contentDetails/relatedPlaylists'
              ).execute()['items'][0]['contentDetails']['relatedPlaylists']
  #don't really know a better way to do the 5 lines below
  playlistId_list.append({
                          'title': u'watchLater',
                          'playlistId' : playlist_1['watchLater']
                        })
  playlistId_list.append({
                          'title': u'watchHistory',
                          'playlistId' : playlist_1['watchHistory']
                        })
  playlistId_list.append({
                          'title': u'likes',
                          'playlistId' : playlist_1['likes']
                        })
  playlistId_list.append({
                          'title': u'favorites',
                          'playlistId' : playlist_1['favorites']
                        })
  playlistId_list.append({
                          'title': u'uploads',
                          'playlistId' : playlist_1['uploads']
                        })
  
  #user created playlist
  token = None
  while True:
    playlist_2 = youtube.playlists().list(
                part="snippet",
                maxResults=50,
                mine=True,
                pageToken=token,
                fields="nextPageToken,items/id,items/snippet/title"
              ).execute()
    token = playlist_2.get('nextPageToken')
    for playlist in playlist_2['items']:
      playlistId_list.append({
                              'title' : playlist['snippet']['title'],
                              'playlistId' : playlist['id']
                            })
    if token == None:
      return playlistId_list

#return a dictionary with 'channelTitle' and 'channelId'
def get_my_subscriptions_list (youtube): 
  print "  Getting subscription list"
  channelId_list = []
  token = None
  while True:
    channelId = youtube.subscriptions().list(
              part = 'snippet',
              maxResults = 50,
              mine = True,
              pageToken = token,
              fields = 'nextPageToken,items/snippet/title,items/snippet/resourceId/channelId').execute()
    for channel in channelId['items']:
      channelId_list.append({ 'channelTitle': channel['snippet']['title'], 
                              'channelId': channel['snippet']['resourceId']['channelId']
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
    videoId_list.append({ 'id' : unicodedata.normalize('NFKC', video['id']),
                          'publishedAt' : unicodedata.normalize('NFKC', video['snippet']['publishedAt']),
                          'title' : unicodedata.normalize('NFKC', video['snippet']['title']),
                          'channelTitle' : unicodedata.normalize('NFKC', video['snippet']['channelTitle'])
                        })
  return videoId_list
def get_playlistId (youtube, title):
  for playlist in get_my_playlist (youtube):
    if playlist['title'] == title:
      return playlist
#return dictionary with 'id', 'publishedAt', 'title', and 'channelTitle'
def get_playlist_video_list (youtube, playlist_id):
  print "  Getting playlist videos"
  videoId_list = []
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
      videoId_list.append(str(video['snippet']['resourceId']['videoId']))
    if ( token == None ):
      playlist_videoId_list = []
      for videoId in videoId_list:
        _video = get_video ( youtube, videoId)
        #playlist_videoId_list.append(get_video ( youtube, videoId))
        try:
         playlist_videoId_list.append({  'id' : _video[0]['id'],
                                          'publishedAt' : _video[0]['publishedAt'],
                                          'title' : _video[0]['title'],
                                          'channelTitle' : _video[0]['channelTitle']
                                        })
        except:
          continue
      return playlist_videoId_list

#return dictionary with 'id', 'title', and 'videoId'
def get_playlist_video_id_list (youtube, playlist_id):
  playlist_videoId_list = []
  token = None
  while True:
    videoId = youtube.playlistItems().list(
                      part = 'snippet',
                      maxResults = 50,
                      pageToken = token,
                      playlistId = playlist_id,
                      fields = "items(id,snippet(resourceId/videoId,title)),nextPageToken"
                      ).execute()
    token = videoId.get('nextPageToken')
    print videoId
    for video in videoId['items']:
      playlist_videoId_list.append ({ 'id' : unicodedata.normalize('NFKC', video['id']),
                                      'title' : unicodedata.normalize('NFKC', video['snippet']['title']),
                                      'videoId' : unicodedata.normalize('NFKC', video['snippet']['resourceId']['videoId'])
                                    })
    if (token == None):
      return playlist_videoId_list
#delete a video from a playlist, the id is unique to the item in the playlist
def delete_video_from_playlist (youtube, id):
  youtube.playlistItems().delete(id = id).execute()
#return the date of the oldest video from the watchLater playlist that has channelTitle matching my subscription_list
#return dict with 'id', 'publishedAt', 'title', and 'channelTitle'
def get_watchLater_playlist_newest_video ( youtube ):
  for playlistId in get_my_playlist (youtube):
      if playlistId['title'] == ".WatchLater":
        videoId = sorted (get_playlist_video_list ( youtube , playlistId['playlistId'] ), key=lambda k: k['publishedAt'], reverse=True )
        return videoId[0]
  print ".WatchLater playlist cannot be found, please create a playlist call \".WatchLater\" and add a video as a starting place"
  menu()
        
#return dictionary with 'id', 'publishedAt', 'title', and 'channelTitle'
def get_channel_video_list ( youtube, channelId, date = None):
  #add 10 seconds to date
  date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(0,10)
  date = str(date.year) + '-' + str(date.month) + '-' + str(date.day) + 'T' + str(date.hour) + ':' + str(date.minute) + ':' + str(date.second) + '.000Z'
  return youtube.search().list(
                              part = 'snippet',
                              channelId = channelId,
                              maxResults = 50,
                              publishedAfter = date,
                              fields = 'items(id(videoId),snippet(channelTitle,publishedAt,title))'
                              ).execute()
#return a dict with channelTitle, publishedAt, title, and videoId
#sorted by publishedAt
def get_subscription_video_list ( youtube ):
  print "  Getting subscription videos"
  video_newest = get_watchLater_playlist_newest_video ( youtube )
  video_list = []
  for channel in get_my_subscriptions_list ( youtube ):
    channel_video = get_channel_video_list ( youtube, channel['channelId'], video_newest['publishedAt'] )#"2016-09-20T22:30:10.000Z" )
    if ( len(channel_video['items']) >= 1  ):
      for video in channel_video['items']:
        try:
          video_list.append({
                          'channelTitle' : unicodedata.normalize('NFKC', video['snippet']['channelTitle']) ,
                          'publishedAt' : unicodedata.normalize('NFKC', video['snippet']['publishedAt']) ,
                          'title' : unicodedata.normalize('NFKC', video['snippet']['title']) ,
                          'videoId' : unicodedata.normalize('NFKC', video['id']['videoId']) 
                          })
        except:
          continue
  return sorted (video_list, key=lambda k: k['publishedAt'])

def add_video_to_playlist ( youtube, videoId, playlistId ):
  try:
    youtube.playlistItems().insert(
                            part = 'snippet',
                            body = {
                                   'snippet': {
                                      'playlistId': playlistId, 
                                      'resourceId': {
                                        'kind': 'youtube#video',
                                        'videoId': videoId
                                                    }
                                              }
                                    }
                            ).execute()
  except:
    print "Video already added"

def add_subsription_video_to_watchLater ( youtube ):
  print "\nAdding subscription video to watch later playlist"
  subscription_videos = get_subscription_video_list ( youtube )
  if len(subscription_videos) == 0:
    print "No new subscription videos. No videos added to watch later playlist."
    return
  for videoId in subscription_videos:
    print "  Adding " + unicodedata.normalize('NFKC', videoId['title'] ) + " to watch later playlist"
    add_video_to_playlist ( youtube, videoId['videoId'], 'WL')
  print "Finished adding videos"
  #delete ".WatchLater" playlist and readd it with updated video"
  youtube.playlists().delete(id = get_playlistId(youtube, ".WatchLater")['playlistId']).execute()
  #add ".WatchLater" playlist back and then add video to it
  playlists_insert_response = youtube.playlists().insert(
                                part="snippet,status",
                                body=dict(
                                  snippet=dict(
                                    title=".WatchLater",
                                  ),
                                  status=dict(
                                    privacyStatus="private"
                                  )
                                )
                                ).execute()
  time.sleep(3)
  add_video_to_playlist ( youtube, subscription_videos[-1]['videoId'], get_playlistId(youtube, ".WatchLater")['playlistId'])
def remove_watched_video_from_watchLater_playlist ( youtube ):
  print "\nRemoving watched video from watch later playlist"
  watchLater_list = get_playlist_video_list ( youtube, 'WL' )
  playlist = get_my_playlist ( youtube )
  for playlistId in playlist:
	if playlistId['title'] == "watchHistory":
		#watchHS = playlistId['playlistId']
		watchHistory_list = get_playlist_video_list ( youtube, playlistId['playlistId'])
  
def menu():
  selection_num = raw_input("""
  Main Menu
  (0) For debugging purposes
  (1) Add new playlist
  (2) Delete a playlist
  (3) List user subscription
  (4) Add subscription video to watch later playlist
  (5) Removed videos up to the latest watched video in watch later playlist
  (10/q) Quit
  select: """)
  if (selection_num == "0"): #for debug
    #print get_watchLater_playlist_newest_video ( youtube )
    #print get_my_subscriptions_list ( youtube )
    #print get_playlist_video_list (youtube, )
    #print get_my_playlist(youtube)
    #print get_subscription_video_list ( youtube )
    #print get_playlist_video_id_list (youtube, 'WL')
    #delete_video_from_playlist (youtube, id_here)
    #print get_watchLater_playlist_newest_video ( youtube )
    #print get_my_playlist (youtube)
    #print get_my_subscriptions_list ( youtube )
    #print get_watchLater_playlist_newest_video ( youtube ) This one is causing errors
    #print get_playlist_video_list ( youtube , "HL" )
    #print get_watchLater_playlist_newest_video ( youtube )
    #print get_my_playlist (youtube)
    #print get_playlistId(youtube, ".WatchLater")
	subscription_videos = get_subscription_video_list ( youtube )
	print subscription_videos[-1]['videoId']
  elif (selection_num == "1"):
    add_new_playlist( youtube)
  elif (selection_num == "2"):
    delete_playlist ( youtube )
  elif (selection_num == "3"):
    video = get_subscription_video_list ( youtube )
    for _video in video:
      print _video
  elif (selection_num == "4"):
    add_subsription_video_to_watchLater ( youtube )
  elif (selection_num == "5"):
    remove_watched_video_from_watchLater_playlist ( youtube )
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
