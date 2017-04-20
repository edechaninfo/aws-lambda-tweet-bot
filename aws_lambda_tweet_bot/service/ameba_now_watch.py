# Copyright 2016 edechaninfo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from decimal import Decimal
from HTMLParser import HTMLParser
import logging
import xml.etree.cElementTree as ET

import requests

from tweepy import TweepError
from aws_lambda_tweet_bot.utils import get_dynamodb_table, get_tweepy_api


SERVICE_ID = 'ameba-now-watch'
logger = logging.getLogger('aws_lambda_tweet_bot.service.ameba_now_watch')
logger.setLevel(logging.INFO)


AMEBA_NOW_HOST = 'http://now.ameba.jp'
TEXT_DEFAULT_MAX = 80


# Ameba Now CDATA parser. parsed_data conatins
# - entry_id: ID of now entry (used for key)
# - href: relative URL to now entry
# - time: simple text of posted time
# - text: main posted text
class AmebaNowParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.parsed_info = {}
        self.in_entry_id = None
        self.in_time_body = False
        self.in_text_body = False
        self.in_text_body_a = False
        self.text = ""

    # handle unicode error in ameblo
    def parse_starttag(self, i):
        try:
            return HTMLParser.parse_starttag(self, i)
        except UnicodeDecodeError:
            pass

    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            entry_id = None
            for key, val in attrs:
                if key == 'data-entry-id':
                    entry_id = val
            if entry_id:
                self.in_entry_id = int(entry_id)
                self.parsed_info[self.in_entry_id] = {"entry_id": entry_id}
        elif tag == 'a':
            if self.in_text_body:
                self.in_text_body_a = True
            href = None
            is_time = False
            for key, val in attrs:
                if key == 'href':
                    href = val
                elif key == 'class' and 'time' in val:
                    is_time = True
            if is_time:
                self.parsed_info[self.in_entry_id]["href"] = href
                self.in_time_body = True
        elif tag == 'span':
            is_text = False
            for key, val in attrs:
                if key == 'class' and 'text' in val:
                    is_text = True
                elif key == 'class' and 'photoArea' in val:
                    self.parsed_info[self.in_entry_id]["has_photo"] = True
            self.in_text_body = is_text

    def handle_data(self, data):
        if self.in_time_body:
            self.parsed_info[self.in_entry_id]["time"] = data
        if self.in_text_body and not self.in_text_body_a:
            self.text += data

    def handle_endtag(self, tag):
        if tag == 'li':
            self.in_entry_id = None
        elif tag == 'a' and self.in_time_body:
            self.in_time_body = False
        elif tag == 'a' and self.in_text_body_a:
            self.in_text_body_a = False
        elif tag == 'span' and self.in_text_body:
            self.parsed_info[self.in_entry_id]["text"] = self.text
            self.text = ""
            self.in_text_body = False


def _now_parsed_body(link):
    # stab
    try:
        r = requests.get(link)
        root = ET.fromstring(r.text.encode('utf-8'))
        cdata = root.find('htmlData')
        parser = AmebaNowParser()
        parser.feed(cdata.text)
        parser.close()
        return parser.parsed_info
    except Exception as e:
        # catch all unexpected exception to avoid halting all search
        errmsg = "Unexpected error on parsing ameba now {}: Msg -> {}"
        logger.error(errmsg.format(link, str(e)))
        return {}


def bot_handler(env, conf):
    logger.info('service "{}" started!"'.format(SERVICE_ID))
    now_table = get_dynamodb_table('ameba_now_watch', conf)
    api = get_tweepy_api(env['twitter_env'], conf)
    now_data = now_table.scan()
    indexes = env.get('latest_id_indexes', {})
    del_keys = indexes.keys()  # check if item in now_table is deleted
    for now_item in now_data['Items']:
        # now_item is available so remove id from delete list
        if now_item['id'] in del_keys:
            del_keys.remove(now_item['id'])
        latest_id = Decimal(indexes.get(now_item['id'], 0))
        try:
            # parameter validation
            body_format = now_item.get('body_format')
            if not body_format:
                raise KeyError("body_format must be defined")
            max_len = int(now_item.get('text_length', TEXT_DEFAULT_MAX))
            photo_sub = now_item.get('photo_sub', '')

            api_endpoint = AMEBA_NOW_HOST + '/api/entryList/' + now_item['id']
            parsed = _now_parsed_body(api_endpoint)
            for entry_id in sorted(parsed.keys()):
                if latest_id < entry_id:
                    entry = parsed[entry_id]
                    entry['url'] = \
                        AMEBA_NOW_HOST + entry['href'].encode('utf_8')
                    if len(entry['text']) > max_len:
                        entry['text'] = entry['text'][:max_len] + '...'
                    entry['photo_sub'] = ''
                    if entry.get('has_photo'):
                        entry['photo_sub'] = photo_sub

                    try:
                        twbody = body_format.format(**entry)
                    except KeyError as e:
                        errKey = str(e)[1:-1]
                        raise Exception(
                            "{%s} is not available in parsed ameblo now "
                            "entry. Please check body_format." % errKey)

                    try:
                        api.update_status(twbody)
                        # updated = True
                        logger.info('Tweet Success!\n' +
                                    twbody.encode('utf_8'))
                    except TweepError as e:
                        if 'Status is a duplicate.' not in e.reason:
                            logger.error(str(e))
                            raise e
                    latest_id = entry_id
        except Exception as e:
            errmsg = "Unexpected error on service {}: " + \
                     "Please check DB record (id: {}): Msg -> {}"
            logger.error(errmsg.format(SERVICE_ID, now_item.get('id'),
                                       str(e)))
        indexes[now_item['id']] = latest_id
    # delete unavailable article in ameba_now_table
    for k in del_keys:
        del indexes[k]
    env['latest_id_indexes'] = indexes  # update anytime
    return True
