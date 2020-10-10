#!/usr/bin/python

# Sample usage:
#   python search.py --q=surfing --max-results=10

import argparse
import os

from googleapiclient import discovery
from googleapiclient.errors import HttpError


# AIzaSyBE5tvxahwBu3Z3y2R2lVrY11pNfQLOcIA
# download it from your google developer console: https://cloud.google.com/console under tab of API Keys

DEVELOPER_KEY = "AIzaSyBE5tvxahwBu3Z3y2R2lVrY11pNfQLOcIA"
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
    client = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    http_response = client.search().list(
        q=options.q,
        part='id,snippet',
        maxResults=options.max_results
    ).execute()
    
    videos = []
    channels = []
    playlists = []
    
    for search_result in http_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append('%s (%s)' % (search_result['snippet']['title'], search_result['id']['videoId']))
        elif search_result['id']['kind'] == 'youtube#channel':
            channels.append('%s (%s)' % (search_result['snippet']['title'], search_result['id']['channelId']))
        elif search_result['id']['kind'] == 'youtube#playlist':
            playlists.append('%s (%s)' % (search_result['snippet']['title'], search_result['id']['playlistId']))
    
    print("Videos:\n")
    print("\n".join(videos))
    print("\n")
    
    print("Channels:\n")
    print("\n".join(channels))
    print("\n")
    
    print("Playlists:\n")
    print("\n".join(playlists))
    print("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--q', help='Search term', default='Google')
    parser.add_argument('--max-results', help='Max results', default=25)
    args = parser.parse_args()
    
    try:
        youtube_search(args)
    except HttpError:
        print("Http Request Error")