import argparse
import os
import queue
import google_auth_oauthlib.flow

from googleapiclient.discovery import build
from googleapiclient.discovery import build_from_document
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# AIzaSyBE5tvxahwBu3Z3y2R2lVrY11pNfQLOcIA, this is my API key. Please replace it with yours
# download it from your google developer console: https://cloud.google.com/console under tab of API Keys
DEVELOPER_KEY = "AIzaSyBE5tvxahwBu3Z3y2R2lVrY11pNfQLOcIA"

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = "v3"

CLIENT_SECRET_FILE = "/Users/f0rest/Desktop/CIS668_NLP/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube']

def build_register_client():
    """
    Register app with credentials from client_secret.json. REQUIRED
    """
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=CLIENT_SECRET_FILE, scopes=SCOPES)
    credentails = flow.run_console()
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentails)

def get_comment_threads(client, video_id):
    """ Call the API's commentThreads.list method to list the existing comment threads.
    Args:
        client (IntalledAppFlow): a dedicated client registered with credentials
        video_id (int): video unique id
    Returns:
        Queue: a simple queue containing video ids based on options.q search results
    """
    comment_threads = client.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText"
    ).execute()
    
    return comment_threads["items"]

def get_specific_comments(client, parent_id):
    """ Call the API's comments.list method to list the existing comment replies
    Args:
        client (IntalledAppFlow): a dedicated client registered with credentials
        parent_id (int): comment thread parent id 
    Returns:
        comments["items"]: a simple list containing comments for parent_id
    """
    comments = client.comments().list(
        part="snippet",
        parentId=parent_id,
        textFormat="plainText"
    ).execute()
    
    for item in comments["items"]:
        print("Comment by {}: {}".format(item["snippet"]["authorDisplayName"], item["snippet"]["textDisplay"]))
    
    return comments["items"]


def youtube_search(options):
    """ Search video ids based on keywords list provided
    Args:
        options: An instance of ArgParse(). Used for specifing certain parameters
    Returns:
        Queue: a simple queue containing video ids based on options.q search results
    """
    client = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    http_response = client.search().list(
        q=options.q,
        part='id,snippet',
        maxResults=options.max_results
    ).execute()
    
    video_ids = queue.Queue()
    
    for search_result in http_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            video_ids.put('%s' % (search_result['id']['videoId']))
    
    return video_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--q', help='Search term', default='Google')
    parser.add_argument('--max-results', help='Max results', default=25)
    args = parser.parse_args()
    
    try:
        video_ids = youtube_search(args)
        comments = []
        # print(video_ids)
        
        client = build_register_client()
        print("####################### Client built successful #######################")
        while not video_ids.empty():
            id = video_ids.get()
            print("ID: {}".format(id))
            comment_threads = get_comment_threads(client, id)
            print("Comment threads are \n")
            print(comment_threads)
            comments.append(get_specific_comments(client, comment_threads[0]["id"]))
            
        print("Total comments are {}".format(len(comments)))
        print(comments[:5])
    except HttpError:
        print("Http Request Error")