# -*- encoding: utf-8 -*-
import re
import logging
import json

import requests
from lxml import etree

from facebot.message import send_group, send_person

log = logging.getLogger('facebook')
log.setLevel(logging.WARN)

user_agent = 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
facebook_url = 'http://facebook.com'
login_url = 'https://www.facebook.com/login.php'
access_token_url = 'https://developers.facebook.com/tools/explorer/%s/permissions?version=v2.1&__user=%s&__a=1&__dyn=5U463-i3S2e4oK4pomXWo5O12wAxu&__req=2&__rev=1470714'


class LoginError(Exception):
    pass


class Facebook:
    def __init__(self, email, password):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self._login(email, password)

    def _login(self, email, password):
        log.debug('loging in')

        # get login form datas
        res = self.session.get(facebook_url)
        if res.status_code != 200:
            raise LoginError('Status code is %d' % res.status_code)

        datas = self._get_login_form(res.content)
        datas['email'] = email
        datas['pass'] = password

        res = self.session.post(login_url, data=datas)
        self.user_id = self._get_user_id(res.content)
        log.debug('user_id: %s', self.user_id)
        self.dtsg = self._get_dtsg(res.content)
        log.debug('dtsg: %s', self.dtsg)

        log.info('welcome %s', self.user_id)

    def _get_login_form(self, content):
        '''Scrap post datas from login page.'''

        root = etree.HTML(content)
        # get the login form
        form = root.xpath('//form[@id="login_form"][1]')
        # can't find form tag
        if len(form) < 1:
            raise LoginError('No form datas')

        fields = {}
        # get all input tags in this form
        for input in form[0].xpath('.//input'):
            name = input.xpath('@name[1]')
            value = input.xpath('@value[1]')
            log.debug('name: %s, value: %s' % (name, value))
            if len(name) > 0 and len(value) > 0:
                fields[name[0]] = value[0]

        return fields

    def _get_user_id(self, content):
        '''Find user id in the facebook page.'''
        m = re.search('\"USER_ID\":\"(\d+)\"', content)
        if m:
            return m.group(1)
        else:
            return ''

    def _get_dtsg(self, content):
        '''Find dtsg value in the facebook page.'''
        m = re.search('name=\"fb_dtsg\" value=\"(.*?)\"', content)
        if m:
            return m.group(1)
        else:
            return ''

    def get_access_token(self, app_id='145634995501895'):
        '''Register an access token in graph api console.'''
        # get response of registering access token
        res = self.session.get(access_token_url % (app_id, self.user_id))
        # remove for (;;); so we can load content in json format
        content = json.loads(re.sub('for \(;;\);', '', res.content))

        # try to get access token inside a duplicate structure
        try:
            token = content['jsmods']['instances'][2][2][2]
        except KeyError:
            token = ''

        return token

    def send_group(self, thread, body, pic=None):
        '''Send message to specific group.'''
        send_group(self, thread, body, pic)

    def send_person(self, person, body, pic=None):
        '''Send message to specific user.'''
        send_person(self, person, body, pic)
