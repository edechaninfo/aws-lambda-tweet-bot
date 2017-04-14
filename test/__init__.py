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

from collections import defaultdict
import copy
import logging
import sys

from requests.exceptions import ConnectionError
from tweepy import TweepError

from test.utils import validate_data_for_dynamo_db


class FakeLogger(logging.Logger, object):
    store_in = {
        logging.ERROR: 'error',
        logging.WARNING: 'warning',
        logging.INFO: 'info',
        logging.DEBUG: 'debug',
        logging.CRITICAL: 'critical',
    }

    def __init__(self, *args, **kwargs):
        self._clear()
        self.name = 'swift.unit.fake_logger'
        self.level = logging.NOTSET
        if 'facility' in kwargs:
            self.facility = kwargs['facility']
        self.statsd_client = None
        self.thread_locals = None
        self.parent = None

    def _log(self, level, msg, *args, **kwargs):
        store_name = self.store_in[level]
        cargs = [msg]
        if any(args):
            cargs.extend(args)
        captured = dict(kwargs)
        if 'exc_info' in kwargs and \
                not isinstance(kwargs['exc_info'], tuple):
            captured['exc_info'] = sys.exc_info()
        self.log_dict[store_name].append((tuple(cargs), captured))
        super(FakeLogger, self)._log(level, msg, *args, **kwargs)

    def _clear(self):
        self.log_dict = defaultdict(list)
        self.lines_dict = {'critical': [], 'error': [], 'info': [],
                           'warning': [], 'debug': []}

    def _handle(self, record):
        try:
            line = record.getMessage()
        except TypeError:
            print('WARNING: unable to format log message %r %% %r' % (
                record.msg, record.args))
            raise
        self.lines_dict[record.levelname.lower()].append(line)

    def handle(self, record):
        self._handle(record)


class FakeDynamodbTable(object):
    def __init__(self, items):
        self.items = copy.deepcopy(items)
        self._map = dict()
        self._put_item_count = 0
        for item in items:
            validate_data_for_dynamo_db(item)
            # 'id' is always regarded as ID of record
            self._map[item['id']] = copy.deepcopy(item)
        self._put_items = list()

    def scan(self):
        return {"Items": self.items}

    def put_item(self, item):
        validate_data_for_dynamo_db(item)
        self._map[item['id']] = item
        self._put_item_count += 1

    def get_item(self, key):
        return self._map.get(key)


class FakeStatus(object):
    def __init__(self, status, extended=False):
        self.status = status
        self.extended = extended

    @property
    def id(self):
        return self.status['id']

    @property
    def text(self):
        if self.extended:
            raise AttributeError("'Status' object has no attribute 'text'")
        return self.status['text']

    @property
    def full_text(self):
        if not self.extended:
            raise AttributeError(
                "'Status' object has no attribute 'full_text'")
        return self.status['full_text']

    @property
    def extended_entities(self):
        return self.status['extended_entities']

    @property
    def retweeted_status(self):
        return FakeStatus(self.status['retweeted_status'], self.extended)


class FakeTweepyApi(object):
    def __init__(self, statuses={}, update_error=False):
        self._retweet_ids = list()
        self._retweet_error_count = 0
        self._update_statuses = list()
        self._update_status_error_count = 0
        self._set_statuses(statuses)
        self._update_error = update_error

    def _set_statuses(self, statuses):
        self._statuses = copy.deepcopy(statuses)

    def __get_timeline(self, tl, tweet_mode):
        if isinstance(tl, TweepError):
            raise tl
        statuses = list()
        extended = tweet_mode == 'extended'
        for status_dict in tl:
            statuses.append(FakeStatus(status_dict, extended))
        return statuses

    def user_timeline(self, account, since_id, tweet_mode=None):
        # ignore since_id in this mock
        return self.__get_timeline(self._statuses['user'][account],
                                   tweet_mode)

    def list_timeline(self, owner_screen_name, slug, since_id,
                      tweet_mode=None):
        # ignore since_id in this mock
        return self.__get_timeline(
            self._statuses['list'][owner_screen_name][slug], tweet_mode)

    def retweet(self, status_id):
        if status_id in self._retweet_ids:
            self._retweet_error_count += 1
            raise TweepError('You have already retweeted this tweet.')
        self._retweet_ids.append(status_id)

    def update_status(self, body):
        if self._update_error:
            raise TweepError('Internal error')
        if body in self._update_statuses:
            self._update_status_error_count += 1
            raise TweepError('Status is a duplicate.')
        self._update_statuses.append(body)


class FakeRequests(object):
    def __init__(self, url_body_pairs={}):
        self.url_body_pairs = url_body_pairs

    def get(self, url):
        class FakeResponseClass(object):
            def __init__(self, body):
                self._text = body

            @property
            def text(self):
                return self._text
        body = self.url_body_pairs.get(url)
        if body is not None:
            return FakeResponseClass(body)
        else:
            raise ConnectionError()
