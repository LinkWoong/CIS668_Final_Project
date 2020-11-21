from __future__ import print_function

import io
import json
import os
import sys
import time

import argparse
import lxml.html
import requests
import queue
import google_auth_oauthlib.flow

from lxml.cssselect import CSSSelector

from googleapiclient.discovery import build
from googleapiclient.discovery import build_from_document
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from id_getter import youtube_search

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v={youtube_id}'
YOUTUBE_COMMENTS_AJAX_URL_OLD = 'https://www.youtube.com/comment_ajax'
YOUTUBE_COMMENTS_AJAX_URL_NEW = 'https://www.youtube.com/comment_service_ajax'

# AIzaSyBE5tvxahwBu3Z3y2R2lVrY11pNfQLOcIA, this is my API key. Please replace it with yours
# download it from your google developer console: https://cloud.google.com/console under tab of API Keys
DEVELOPER_KEY = "AIzaSyBE5tvxahwBu3Z3y2R2lVrY11pNfQLOcIA"

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = "v3"

# Http header
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

# find a specific value in HTML entities
def find_value(html, key, num_chars=2, separator='"'):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(separator, pos_begin)
    return html[pos_begin: pos_end]

# simple HTTP GET request with retries, each retry has 20 seconds separation
def ajax_request(session, url, params=None, data=None, headers=None, retries=5, sleep=20):
    for _ in range(retries):
        response = session.post(url, params=params, data=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        if response.status_code in [403, 413]:
            return {}
        else:
            time.sleep(sleep)

# use new api to download live stream
# else use old api
def download_comments(youtube_id, sleep=.1):
    if r'\"isLiveContent\":true' in requests.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id)).text:
        print('Live stream detected! Not all comments may be downloaded.')
        return download_comments_new_api(youtube_id, sleep)
    return download_comments_old_api(youtube_id, sleep)

def download_comments_new_api(youtube_id, sleep=1):
    # Use the new youtube API to download some comments
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT

    response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))
    html = response.text
    session_token = find_value(html, 'XSRF_TOKEN', 3)

    data = json.loads(find_value(html, 'window["ytInitialData"] = ', 0, '\n').rstrip(';'))
    for renderer in search_dict(data, 'itemSectionRenderer'):
        ncd = next(search_dict(renderer, 'nextContinuationData'), None)
        if ncd:
            break
    continuations = [(ncd['continuation'], ncd['clickTrackingParams'])]

    while continuations:
        continuation, itct = continuations.pop()
        response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL_NEW,
                                params={'action_get_comments': 1,
                                        'pbj': 1,
                                        'ctoken': continuation,
                                        'continuation': continuation,
                                        'itct': itct},
                                data={'session_token': session_token},
                                headers={'X-YouTube-Client-Name': '1',
                                         'X-YouTube-Client-Version': '2.20200207.03.01'})

        if not response:
            break
        if list(search_dict(response, 'externalErrorMessage')):
            raise RuntimeError('Error returned from server: ' + next(search_dict(response, 'externalErrorMessage')))

        # Ordering matters. The newest continuations should go first.
        continuations = [(ncd['continuation'], ncd['clickTrackingParams'])
                         for ncd in search_dict(response, 'nextContinuationData')] + continuations

        for comment in search_dict(response, 'commentRenderer'):
            yield {'cid': comment['commentId'],
                   'text': ''.join([c['text'] for c in comment['contentText']['runs']])}

        time.sleep(sleep) # sleep for a given time period so we don't get blocked by Google :)


def search_dict(partial, key):
    if isinstance(partial, dict):
        for k, v in partial.items():
            if k == key:
                yield v
            else:
                for o in search_dict(v, key):
                    yield o
    elif isinstance(partial, list):
        for i in partial:
            for o in search_dict(i, key):
                yield o


def download_comments_old_api(youtube_id, sleep=1):
    # Use the old youtube API to download all comments (does not work for live streams)
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT

    # Get Youtube page with initial comments
    response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))
    html = response.text

    reply_cids = extract_reply_cids(html)

    ret_cids = []
    for comment in extract_comments(html):
        ret_cids.append(comment['cid'])
        yield comment

    page_token = find_value(html, 'data-token')
    session_token = find_value(html, 'XSRF_TOKEN', 3)

    first_iteration = True

    # Get remaining comments (the same as pressing the 'Show more' button)
    while page_token:
        data = {'video_id': youtube_id,
                'session_token': session_token}

        params = {'action_load_comments': 1,
                  'order_by_time': True,
                  'filter': youtube_id}

        if first_iteration:
            params['order_menu'] = True
        else:
            data['page_token'] = page_token

        response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL_OLD, params, data)
        if not response:
            break

        page_token, html = response.get('page_token', None), response['html_content']

        reply_cids += extract_reply_cids(html)
        for comment in extract_comments(html):
            if comment['cid'] not in ret_cids:
                ret_cids.append(comment['cid'])
                yield comment

        first_iteration = False
        time.sleep(sleep)

    # Get replies (the same as pressing the 'View all X replies' link)
    for cid in reply_cids:
        data = {'comment_id': cid,
                'video_id': youtube_id,
                'can_reply': 1,
                'session_token': session_token}

        params = {'action_load_replies': 1,
                  'order_by_time': True,
                  'filter': youtube_id,
                  'tab': 'inbox'}

        response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL_OLD, params, data)
        if not response:
            break

        html = response['html_content']

        for comment in extract_comments(html):
            if comment['cid'] not in ret_cids:
                ret_cids.append(comment['cid'])
                yield comment
        time.sleep(sleep)

# use lxml parser to extract comments from html tree
def extract_comments(html):
    tree = lxml.html.fromstring(html)
    item_sel = CSSSelector('.comment-item')
    text_sel = CSSSelector('.comment-text-content')

    for item in item_sel(tree):
        yield {'cid': item.get('data-cid'),
               'text': text_sel(item)[0].text_content()}


def extract_reply_cids(html):
    tree = lxml.html.fromstring(html)
    sel = CSSSelector('.comment-replies-header > .load-comments')
    return [i.get('data-cid') for i in sel(tree)]


def main(argv):
    parser = argparse.ArgumentParser(add_help=False, description=('Download Youtube comments without using the Youtube API'))
    # parser.add_argument('--youtubeid', '-y', help='ID of Youtube video for which to download the comments')
    parser.add_argument('--output', '-o', help='Output filename (output format is line delimited JSON)')
    # parser.add_argument('--limit', '-l', type=int, help='Limit the number of comments')
    parser.add_argument('--q', '-q', help='Keyword to search, now only accept one word.')
    parser.add_argument('--maxresults', '-m', help='Maximum query result for a keyword', default=25)
    
    # TODO: read a list containing all words needed instead of read one by one
    
    # example output: <K, V> pair -> cid : comment
    # {
    #     "UgyNfVDpgesamWyWT794AaABAg": "the irony is that this video is stored in google cloud platform",
    #     "UghZPYxpAU6oT3gCoAEC": "Ouch, high frequency tones used for digital bit flow sound effect. Use lower tones...",
    #     "UghZPYxpAU6oT3gCoAEC.8OrRc3r3vFl8W71TLv2WSz": "nerd",
    #     "UgjO0PNK_Y2nMngCoAEC": "That's awesome. People with money who want to help people are the best"
    # }

    try:
        args = parser.parse_args(argv)
        output = args.output
        
        video_ids = youtube_search(args, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, DEVELOPER_KEY)
        inc = 0
        
        while not video_ids.empty():
            youtube_id = video_ids.get()
            if not youtube_id or not output:
                parser.print_usage()
                raise ValueError('you need to specify a Youtube ID and an output filename')

            if os.sep in output:
                outdir = os.path.dirname(output)
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
    
            print('Downloading Youtube comments for video:', youtube_id)
            count = 0
            
            sys.stdout.write('Downloaded %d comment(s)\r' % count)
            sys.stdout.flush()
            start_time = time.time()
            
            for comment in download_comments(youtube_id):
                comment_json = json.dumps(comment, ensure_ascii=False)
                if isinstance(comment_json, bytes):
                    comment_json = comment_json.decode('utf-8')
                # print(comment_json)
                # {"cid": "UgyNfVDpgesamWyWT794AaABAg", "text": "the irony is that this video is stored in google cloud platform"}
                comment_json = json.loads(comment_json)
                if inc != 0:
                    with open(output) as fp:
                        data = json.load(fp)
                    data.update({comment_json["cid"]: comment_json["text"]})

                    with open(output, "w", encoding='utf-8') as fp:
                        json.dump(data, fp, ensure_ascii=False, indent=4)
                else:
                    with open(output, "w", encoding='utf-8') as fp:
                        # print(comment_json.decode('utf-8') if isinstance(comment_json, bytes) else comment_json, file=fp)
                        json.dump({comment_json["cid"]: comment_json["text"]}, fp, ensure_ascii=False, indent=4)
                inc += 1
                count += 1
                sys.stdout.write('Downloaded %d comment(s)\r' % count)
                sys.stdout.flush()
                
            print('\n[{:.2f} seconds] Done!'.format(time.time() - start_time))

    except Exception as e:
        print('Error:', str(e))
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])