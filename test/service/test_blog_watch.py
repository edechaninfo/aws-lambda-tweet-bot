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
from mock import patch
import time
import unittest


from aws_lambda_tweet_bot.service import blog_watch
from test import FakeTweepyApi, FakeRequests
from test.service.sample_data import sample_blog_data, sample_blog_data2, \
    sample_blog_data3, sample_ameblo_blog_body
from test.service.base import BaseTest
from test.utils import obj


PATH_BLOG_WATCH = "aws_lambda_tweet_bot.service.blog_watch"
T_TARGET = PATH_BLOG_WATCH + ".get_tweepy_api"


class FakeFeedparser(object):
    DEFAULT_RETURN = {
        "entries": [],
        "feed": {}
    }

    def __init__(self, results={}):
        self.results = results

    def parse(self, url):
        return self.results.get(url, self.DEFAULT_RETURN)


class TestBlogWatch(BaseTest):
    def setUp(self):
        super(TestBlogWatch, self).setUp()
        self.dynamo.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            TableName='test_blog_watch',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            },
        )
        self.service_id = blog_watch.SERVICE_ID

    def tearDown(self):
        super(TestBlogWatch, self).tearDown()
        self.dynamo.delete_table(TableName='test_blog_watch')

    def _mktime(self, strtime):
        return Decimal(
            time.mktime(time.strptime(strtime, '%Y/%m/%d %H:%M:%S')))

    def _bot_handler(self, conf, mock_tweepy, mock_feed):
        env = self.get_env_from_local_dynamodb(self.service_id)

        def _fake_feedparse(url):
            return mock_feed.parse(url)

        with patch(T_TARGET, return_value=mock_tweepy):
            with patch('feedparser.parse', _fake_feedparse):
                blog_watch.logger = self.logger
                ret = blog_watch.bot_handler(env, conf)
        # check output env
        self.set_env_to_local_dynamodb(self.service_id, env)
        return ret

    def test_blog_watch(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(2, len(tw._update_statuses))
        self.assertEqual(self._mktime('2016/09/12 23:59:59'),
                         env['pubdate_indexes']['feed'])

        result_status_1 = "[New Update] Ede: Yoru-night! -> " + \
            "https://ameblo.jp/fruits-box-blog/entry-12210698546.html " + \
            "#Ede-chan"
        result_status_2 = "[New Update] Ede: Pop in Q -> " + \
            "https://ameblo.jp/fruits-box-blog/entry-12208663602.html " + \
            "#Ede-chan"
        self.assertIn(result_status_1, tw._update_statuses)
        self.assertIn(result_status_2, tw._update_statuses)

    def test_blog_watch_unavailable_feed_index_deleted(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59'),
                   'unavail': self._mktime('2016/12/28 15:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(2, len(tw._update_statuses))
        self.assertEqual(self._mktime('2016/09/12 23:59:59'),
                         env['pubdate_indexes']['feed'])
        self.assertNotIn('unavail', env['pubdate_indexes'])

    def test_multiple_blog_watch(self):
        feed_item_1 = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        feed_item_2 = dict(
            id="feed_other",
            feed="http://otherexistsite.io/feed",
            latest_id="https://ameblo.jp/otakublo/entry-12290698546.html",
            search_condition="Hondo",
            body_format="[Guest Info] '{title}' -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch',
                                         [feed_item_1, feed_item_2])
        feed = FakeFeedparser({
            "http://existsite.io/feed": sample_blog_data,
            "http://otherexistsite.io/feed": sample_blog_data2})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59'),
                   'feed_other': self._mktime('2016/12/31 20:14:14')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(3, len(tw._update_statuses))
        # For blog 1
        self.assertEqual(self._mktime('2016/09/12 23:59:59'),
                         env['pubdate_indexes']['feed'])
        # For blog 2
        self.assertEqual(self._mktime('2017/01/21 23:14:14'),
                         env['pubdate_indexes']['feed_other'])

        result_status_1 = "[New Update] Ede: Yoru-night! -> " + \
            "https://ameblo.jp/fruits-box-blog/entry-12210698546.html " + \
            "#Ede-chan"
        result_status_2 = "[New Update] Ede: Pop in Q -> " + \
            "https://ameblo.jp/fruits-box-blog/entry-12208663602.html " + \
            "#Ede-chan"
        result_status_3 = "[Guest Info] 'Hondo-san has come as our guest'" + \
            " -> https://ameblo.jp/otakublo/entry-12311554968.html #Ede-chan"
        self.assertIn(result_status_1, tw._update_statuses)
        self.assertIn(result_status_2, tw._update_statuses)
        self.assertIn(result_status_3, tw._update_statuses)

    def test_multiple_blog_either_occurs_error(self):
        feed_item_1 = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        feed_item_2 = dict(
            id="feed_other",
            feed="http://otherexistsite.io/feed",
            latest_id="https://ameblo.jp/otakublo/entry-12290698546.html",
            search_condition="Hondo",
            body_format="[Guest Info] '{title}' -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch',
                                         [feed_item_1, feed_item_2])
        feed = FakeFeedparser({
            "http://existsite.io/feed": {},  # Feed result is unexpected
            "http://otherexistsite.io/feed": sample_blog_data2})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59'),
                   'feed_other': self._mktime('2016/12/31 20:14:14')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        # unchange blog 1
        self.assertEqual(self._mktime('2016/08/28 15:21:59'),
                         env['pubdate_indexes']['feed'])
        # for blog 2
        self.assertEqual(self._mktime('2017/01/21 23:14:14'),
                         env['pubdate_indexes']['feed_other'])
        self.assertEqual(1, len(tw._update_statuses))
        self.assertIn('Unexpected error on service blog-watch: '
                      'Please check DB record (id: feed)',
                      self.logger.lines_dict['error'][0])

    def test_empty_search_condition(self):
        # Empty search_condition is regarded as all posts are passed
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            body_format="[New Update] {title} -> {link}"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(3, len(tw._update_statuses))
        self.assertEqual(self._mktime('2016/09/12 23:59:59'),
                         env['pubdate_indexes']['feed'])

    def test_empty_body_format(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertEqual("Unexpected error on service blog-watch: "
                         "Please check DB record (id: feed)"
                         ": Msg -> 'body_format must be defined'",
                         self.logger.lines_dict['error'][0])
        # unchange blog 1
        self.assertEqual(self._mktime('2016/08/28 15:21:59'),
                         env['pubdate_indexes']['feed'])

    def test_invalid_body_format(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {itle} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertIn('{itle} is not available in blog entry.',
                      self.logger.lines_dict['error'][0])
        # unchange blog 1
        self.assertEqual(self._mktime('2016/08/28 15:21:59'),
                         env['pubdate_indexes']['feed'])

    def test_empty_pubdate_indexes(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}
        self.set_env_to_local_dynamodb(self.service_id, env)

        with patch('time.time', return_value=1500000000.3):
            self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(0, len(tw._update_statuses))
        # No tweet, but pubdate_indexes is added as current time
        self.assertEqual(1500000000.3, env['pubdate_indexes']['feed'])

    def test_no_new_blog_update(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12211554966.html",
            body_format="[New Update] {title} -> {link}",
            search_condition="Ede:"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/09/11 23:59:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(0, len(tw._update_statuses))
        # No update, but index is moved to latest pubdate
        self.assertEqual(self._mktime('2016/09/12 23:59:59'),
                         env['pubdate_indexes']['feed'])

    def test_update_fail_no_index_change(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12208663602.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link}"
        )
        tw = FakeTweepyApi(update_error=True)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 21:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(0, len(tw._update_statuses))
        # Tweet error, so index is not moved
        self.assertEqual(self._mktime('2016/08/28 21:21:59'),
                         env['pubdate_indexes']['feed'])

    def test_empty_blogs(self):
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [])
        feed = FakeFeedparser()
        env = {'twitter_env': 'test'}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertEqual(1, len(self.logger.lines_dict['info']))

    def test_not_found_feed(self):
        wrong_feed_item = dict(
            id="wrong_feed",
            feed="http://noexistsite.io/feed"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [wrong_feed_item])
        feed = FakeFeedparser()
        env = {'twitter_env': 'test'}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertIn('No entries. Please check feed url setting.',
                      self.logger.lines_dict['error'][0])

    def test_second_search_do_nothing(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/08/28 15:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(self._mktime('2016/09/12 23:59:59'),
                         env['pubdate_indexes']['feed'])

        # def fake function for _match_search_condition
        def _fake_msc(db_item, feed_entry, latest_date):
            match = False
            # Check if this entry should be searched
            if latest_date < time.mktime(feed_entry.published_parsed):
                raise Exception("2nd try has come")
            return match
        # blog_watch._match_search_condition = _fake_match_search_condition
        with patch(PATH_BLOG_WATCH + '._match_search_condition', _fake_msc):
            self._bot_handler(self.config, tw, feed)
        self.assertEqual(0, len(self.logger.lines_dict['error']))

    def test_blog_body_search_mock(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/ari-step/entry-12224195010.html",
            body_search=True,
            body_search_conditions=["Hondo-chan"],
            body_format="[New Update] {title} -> {link} #Ari-chan #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data3})
        req = FakeRequests(
            {'https://ameblo.jp/ari-step/entry-12226218315.html':
             sample_ameblo_blog_body})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/07/21 13:14:14')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        with patch(PATH_BLOG_WATCH + '.requests', req):
            self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        result_status = "[New Update] Look this -> " + \
            "https://ameblo.jp/ari-step/entry-12226218315.html " + \
            "#Ari-chan #Ede-chan"
        self.assertEqual(1, len(tw._update_statuses))
        self.assertIn(result_status, tw._update_statuses)
        self.assertEqual(self._mktime('2016/08/21 23:14:14'),
                         env['pubdate_indexes']['feed'])

    def test_blog_body_search_mock_no_match(self):
        # '4DX' word is found in link list but this should not be tweeted
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="https://ameblo.jp/ari-step/entry-12224195010.html",
            body_search=True,
            body_search_conditions=["4DX"],
            body_format="[New Update] {title} -> {link} #Ari-chan #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data3})
        req = FakeRequests(
            {'https://ameblo.jp/ari-step/entry-12226218315.html':
             sample_ameblo_blog_body})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'feed': self._mktime('2016/07/21 13:14:14')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        with patch(PATH_BLOG_WATCH + '.requests', req):
            self._bot_handler(self.config, tw, feed)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertEqual(self._mktime('2016/08/21 23:14:14'),
                         env['pubdate_indexes']['feed'])

    def test_blog_body_search_online(self):
        # Check if Ameblo spec is not changed
        # Yui Ogura Blog Data
        ogusan_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'version': 'rss20',
            'entries': [
                obj(published_parsed=time.strptime('2016/08/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Supply Water',
                    link='https://ameblo.jp/ogurayui-0815/'
                         'entry-12187666106.html'),
                obj(published_parsed=time.strptime('2016/08/01 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Hot and Spicy',
                    link='https://ameblo.jp/ogurayui-0815/'
                         'entry-12186656735.html'),
                obj(published_parsed=time.strptime('2016/07/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Summer Vacation',
                    link='https://ameblo.jp/ogurayui-0815/'
                         'entry-12186044375.html')
            ]
        }
        kyarisan_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'version': 'rss20',
            'entries': [
                obj(published_parsed=time.strptime('2016/08/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Pop in Q',
                    link='https://ameblo.jp/ishiharakaori-0806/'
                         'entry-12225358373.html'),
                obj(published_parsed=time.strptime('2016/08/01 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Cocon Poi Poi Cocotama',
                    link='https://ameblo.jp/ishiharakaori-0806/'
                         'entry-12224315509.html'),
                obj(published_parsed=time.strptime('2016/07/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Event',
                    link='https://ameblo.jp/ishiharakaori-0806/'
                         'entry-12223186447.html')
            ]
        }
        tanoway_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'version': 'rss20',
            'entries': [
                obj(published_parsed=time.strptime('2016/08/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Birthday',
                    link='https://ameblo.jp/tanoue-marina/'
                         'entry-12232581672.html'),
                obj(published_parsed=time.strptime('2016/08/01 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='VR',
                    link='https://ameblo.jp/tanoue-marina/'
                         'entry-12232298510.html'),
                obj(published_parsed=time.strptime('2016/07/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Greeting 2',
                    link='https://ameblo.jp/tanoue-marina/'
                         'entry-12231980149.html')
            ]
        }
        arichan_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'version': 'rss20',
            'entries': [
                obj(published_parsed=time.strptime('2016/08/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='In these days...',
                    link='https://ameblo.jp/ari-step/entry-12233144905.html'),
                obj(published_parsed=time.strptime('2016/08/01 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='Look this',
                    link='https://ameblo.jp/ari-step/entry-12226218315.html'),
                obj(published_parsed=time.strptime('2016/07/21 23:14:14',
                                                   '%Y/%m/%d %H:%M:%S'),
                    title='4DX!!',
                    link='https://ameblo.jp/ari-step/entry-12224195011.html')
            ]
        }
        ogusan_feed_item = dict(
            id="ogusan",
            feed="http://existsite.io/ogusan",
            latest_id="https://ameblo.jp/ogurayui-0815/entry-12184451116.html",
            body_format="[New Update] {title} -> {link} #Yui-chan #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u3048\u30fc\u3067\u3061\u3083\u3093"]
            # edechan in Hiragana
        )
        kyarisan_feed_item = dict(
            id="kyarisan",
            feed="http://existsite.io/kyarisan",
            latest_id="https://ameblo.jp/ishiharakaori-0806/"
                      "entry-12223056549.html",
            body_format="[New Update] {title} -> {link} #Kyari-san #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u672c\u6e21"]
            # hondo in Kanji
        )
        tanoway_feed_item = dict(
            id="tanoway",
            feed="http://existsite.io/tanoway",
            latest_id="https://ameblo.jp/tanoue-marina/entry-12231636584.html",
            body_format="[New Update] {title} -> {link} #Tano-way #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u672c\u6e21"]
            # hondo in Kanji
        )
        arichan_feed_item = dict(
            id="arichan",
            feed="http://existsite.io/arichan",
            latest_id="https://ameblo.jp/ari-step/entry-12223871525.html",
            body_format="[New Update] {title} -> {link} #Ari-chan #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u672c\u6e21"]
            # hondo in Kanji
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('blog_watch', [ogusan_feed_item,
                                                        kyarisan_feed_item,
                                                        tanoway_feed_item,
                                                        arichan_feed_item])
        feed = FakeFeedparser(
            {"http://existsite.io/ogusan": ogusan_blog_data,
             "http://existsite.io/kyarisan": kyarisan_blog_data,
             "http://existsite.io/tanoway": tanoway_blog_data,
             "http://existsite.io/arichan": arichan_blog_data})
        env = {'twitter_env': 'test',
               'pubdate_indexes': {
                   'ogusan': self._mktime('2016/06/28 15:21:59'),
                   'kyarisan': self._mktime('2016/06/28 15:21:59'),
                   'tanoway': self._mktime('2016/06/28 15:21:59'),
                   'arichan': self._mktime('2016/06/28 15:21:59')}}
        self.set_env_to_local_dynamodb(self.service_id, env)

        self._bot_handler(self.config, tw, feed)
        self.assertEqual(5, len(tw._update_statuses))


if __name__ == '__main__':
    unittest.main()
