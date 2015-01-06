#!/usr/bin/env python3

import re
import json
import logging

import requests
from facebot import Facebook

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

USERNAME = ''
PASSWORD = ''
fb = Facebook(USERNAME, PASSWORD)
log.info('login %s', fb.user_id)


def pull_message(seq=None):
    '''
    Call pull api with seq value to get message data.
    '''
    url = 'https://1-channel-proxy-07-ash2.facebook.com/pull?channel=p_{user_id}&partition=-2&clientid=6f09f868&cb=ith0&idle=8&cap=0&uid={user_id}&viewer_uid={user_id}&sticky_token=195&traceid=H1WKF&state=active'

    # if seq is not None, append seq to parameters
    if seq:
        url += '&seq={seq}'

    # call pull api, and set timeout as one minute
    res = fb.session.get(
        url.format(user_id=fb.user_id, seq=seq), timeout=60)

    # remove for (;;); so we can turn them into dictionaries
    content = json.loads(re.sub('for \(;;\); ', '', res.text))

    # get seq from response
    seq = content.get('seq', '0')
    log.debug('seq: %s', seq)

    return content, seq


def get_message(content):
    '''
    Get message and author name from content.
    May contains multiple messages in the content.
    '''
    if 'ms' not in content:
        return

    for m in content['ms']:
        # we only want item which type is m_messaging
        if m.get('type') != 'm_messaging':
            continue

        message = m.get('message', '')
        author_id = m.get('author_fbid', '')
        author_name = m.get('author_name', '')
        tid = m.get('tid', '')

        yield tid, author_id, author_name, message


def main():
    # call pull api without seq, so we can get seq value from response
    _, seq = pull_message()

    while True:
        # tell facebook that client is alive
        fb.ping()

        # call pull api with seq
        try:
            content, seq = pull_message(seq)
        except requests.exceptions.RequestException as e:
            log.warn('RequestException: {}'.format(e))
            continue

        # iterate through each message in response
        for tid, author_id, author_name, message in get_message(content):
            log.debug('%s(%s): %s', author_name, author_id, message)

            # if author is myself, leave him alone
            if author_id == int(fb.user_id):
                continue

            if tid.startswith('mid'):
                # this was sent from person
                log.info('%s: %s', author_id, message)
            elif tid.startswith('id'):
                # this was sent from group
                log.info('%s: %s', tid[3:], message)

if __name__ == '__main__':
    main()
