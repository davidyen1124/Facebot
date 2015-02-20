# -*- encoding: utf-8 -*-
import re
import logging
import json

import requests
from lxml import etree

from facebot.message import (
    send_group, send_person, group_typing, person_typing,
    read)
from facebot.sticker import get_stickers

logging.basicConfig()
log = logging.getLogger('facebook')
log.setLevel(logging.WARN)

USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'

LOGIN_URL = 'https://www.facebook.com/login.php'
ACCESS_TOKEN_URL = 'https://developers.facebook.com/tools/explorer/{}/permissions?version=v2.1&__user={}&__a=1&__dyn=5U463-i3S2e4oK4pomXWo5O12wAxu&__req=2&__rev=1470714'
PING_URL = 'https://0-channel-proxy-06-ash2.facebook.com/active_ping?channel=p_{user_id}&partition=-2&clientid=5ae4ed0b&cb=el2p&cap=0&uid={user_id}&viewer_uid={user_id}&sticky_token=479&state=active'


class LoginError(Exception):
    pass


class Facebook:

    def __init__(self, email, password):
        # create a session instance
        self.session = requests.Session()
        # use custom user-agent
        self.session.headers.update({'User-Agent': USER_AGENT})

        # login with email and password
        self._login(email, password)

    def _login(self, email, password):
        log.debug('loging in')

        # get login form datas
        res = self.session.get(LOGIN_URL)

        # check status code is 200 before proceeding
        if res.status_code != 200:
            raise LoginError('Status code is {}'.format(res.status_code))

        # get login form and add email and password fields
        datas = self._get_login_form(res.text)
        datas['email'] = email
        datas['pass'] = password

        # call login API with login form
        res = self.session.post(LOGIN_URL, data=datas)

        # get user id
        self.user_id = self._get_user_id(res.text)
        log.debug('user_id: %s', self.user_id)

        # get facebook dtsg
        self.dtsg = self._get_dtsg(res.text)
        log.debug('dtsg: %s', self.dtsg)

        log.info('welcome %s', self.user_id)

    def _get_login_form(self, content):
        '''Scrap post datas from login page.'''
        # get login form
        root = etree.HTML(content)
        form = root.xpath('//form[@id="login_form"][1]')

        # can't find form tag
        if not form:
            raise LoginError('No form datas')

        fields = {}
        # get all input tags in this form
        for input in form[0].xpath('.//input'):
            name = input.xpath('@name[1]')
            value = input.xpath('@value[1]')
            log.debug('name: %s, value: %s' % (name, value))

            # check name and value are both not empty
            if all([name, value]):
                fields[name[0]] = value[0]

        return fields

    def _get_user_id(self, content):
        '''Find user id in the facebook page.'''
        m = re.search('\"USER_ID\":\"(\d+)\"', content)
        if m:
            # if user_id is 0, there is something wrong
            if m.group(1) == '0':
                raise LoginError('User id is 0')
            else:
                return m.group(1)
        else:
            raise LoginError('No user id')

    def _get_dtsg(self, content):
        '''Find dtsg value in the facebook page.'''
        m = re.search('name=\"fb_dtsg\" value=\"(.*?)\"', content)
        if m:
            return m.group(1)
        else:
            raise LoginError('No facebook dtsg')

    def get_access_token(self, app_id='145634995501895'):
        '''Register an access token in graph api console.'''
        # get response of registering access token
        res = self.session.get(ACCESS_TOKEN_URL.format(app_id, self.user_id))
        # remove for (;;); so we can load content in json format
        content = json.loads(re.sub('for \(;;\);', '', res.text))

        # try to get access token inside a complex structure
        try:
            token = content['jsmods']['instances'][2][2][2]
        except KeyError:
            token = ''

        return token

    def send_group(self, *args, **kwargs):
        '''Send message to specific group.'''
        send_group(self, *args, **kwargs)

    def send_person(self, *args, **kwargs):
        '''Send message to specific user.'''
        send_person(self, *args, **kwargs)

    def ping(self):
        '''Tell facebook that client is alive.'''
        res = self.session.get(PING_URL.format(user_id=self.user_id))
        log.debug(res.text)
        # check pong is in response text
        return 'pong' in res.text

    def get_stickers(self, *args, **kwargs):
        '''Get all stickers by giving one sticker bundle id.'''
        return get_stickers(self, *args, **kwargs)

    def group_typing(self, *args, **kwargs):
        '''Tell everyone in group that current user is typing.'''
        return group_typing(self, *args, **kwargs)

    def person_typing(self, *args, **kwargs):
        '''Tell specific user that current user is typing.'''
        return person_typing(self, *args, **kwargs)

    def read(self, *args, **kwargs):
        '''Read messages of this conversation.'''
        return read(self, *args, **kwargs)
