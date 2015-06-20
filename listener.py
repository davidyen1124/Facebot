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


def get_sticky():
    '''
    Call pull api to get sticky and pool parameter,
    newer api needs these parameter to work.
    '''
    url = 'https://0-edge-chat.facebook.com/pull?channel=p_{user_id}&partition=-2&clientid=3396bf29&cb=gr6l&idle=0&cap=8&msgs_recv=0&uid={user_id}&viewer_uid={user_id}&state=active&seq=0'

    # call pull api, and set timeout as one minute
    res = fb.session.get(url.format(user_id=fb.user_id), timeout=60)

    # remove for (;;); so we can turn them into dictionaries
    content = json.loads(re.sub('for \(;;\); ', '', res.text))

    # check existence of lb_info
    if 'lb_info' not in content:
        raise Exception('Get sticky pool error')

    sticky = content['lb_info']['sticky']
    pool = content['lb_info']['pool']

    return sticky, pool


def pull_message(sticky, pool, seq='0'):
    '''
    Call pull api with seq value to get message data.
    '''
    url = 'https://0-edge-chat.facebook.com/pull?channel=p_{user_id}&partition=-2&clientid=3396bf29&cb=gr6l&idle=0&cap=8&msgs_recv=0&uid={user_id}&viewer_uid={user_id}&state=active&seq={seq}&sticky_token={sticky}&sticky_pool={pool}'

    # call pull api, and set timeout as one minute
    res = fb.session.get(
        url.format(user_id=fb.user_id, seq=seq, sticky=sticky, pool=pool),
        timeout=60)

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
    # get sticky and pool parameter, so we can listener for message
    sticky, pool = get_sticky()

    # call pull api without seq, so we can get seq value from response
    _, seq = pull_message(sticky, pool)

    while True:
        # tell facebook that client is alive
        fb.ping()

        # call pull api with seq
        try:
            content, seq = pull_message(sticky, pool, seq)
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
