#!/usr/bin/python
import re
import urllib.request
import httplib2
import os
import sys

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

DOWNLOAD_PATH = 'C:/Users/poliang/Desktop/music_download/'
GLOBAL_SONG_COUNTER = 1
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "baugusli_google_api_auth.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

YOUTUBEINMP3_API_URL = 'http://www.youtubeinmp3.com/fetch/?video=https://www.youtube.com/watch?v='


def initialize_youtube_api():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
      message=MISSING_CLIENT_SECRETS_MESSAGE,
      scope=YOUTUBE_READONLY_SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)

    youtube_init = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))
    return youtube_init

# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.


def get_youtube_response(youtube, part, playlist_id, no_of_songs_to_dl):
    playlistitem_request = youtube.playlistItems().list(
      playlistId=playlist_id,
      part=part,
      maxResults=no_of_songs_to_dl
    )

    playlistitem_response = playlistitem_request.execute()

    return playlistitem_response


def download_video_from_youtube(youtube_vid_obj):
    youtube_vid_id = youtube_vid_obj.get('video_id')
    youtube_vid_title = youtube_vid_obj.get('video_title', 'song' + youtube_vid_id)
    download_link = YOUTUBEINMP3_API_URL + youtube_vid_id
    urllib.request.urlretrieve(download_link, '{0}{1}.mp3'.format(DOWNLOAD_PATH, youtube_vid_title))


def get_video_details_from_youtube_res_contentDetails(response):
    video_id = response.get('videoId')
    return video_id


def get_video_details_from_youtube_res_snippet(response):
    video_id = response.get('resourceId').get('videoId')
    video_title = re.sub('[^\w\d]', '_', response.get('title'))
    video_details = {'video_id': video_id, 'video_title': video_title}
    return video_details


def process_youtube_response(part, response):
    for video in response["items"]:
        response_content = video.get(part)
        video_details = {}

        if part == 'snippet':
            video_details = get_video_details_from_youtube_res_snippet(response_content)
        else:
            video_details = get_video_details_from_youtube_res_contentDetails(response_content)

        download_video_from_youtube(video_details)

if __name__ == '__main__':
    youtube_obj = initialize_youtube_api()
    playlist_id = "PLvjTMQo9D_15-1zFJdH66kEJhVTu7ZrTw"
    youtube_api_part = 'snippet'
    playlistitem_response = get_youtube_response(youtube_obj, youtube_api_part, playlist_id, 50)
    process_youtube_response(youtube_api_part, playlistitem_response)


