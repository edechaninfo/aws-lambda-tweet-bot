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

from mock import patch
import unittest

from requests.exceptions import ConnectionError

from config import Config
from aws_lambda_tweet_bot.service import blog_watch
from test import FakeDynamodbTable, FakeTweepyApi, FakeLogger
from test.service.sample_data import sample_blog_data, sample_blog_data2, \
    sample_blog_data3, sample_ameblo_blog_body
from test.utils import obj


PATH_BLOG_WATCH = "aws_lambda_tweet_bot.service.blog_watch"
D_TARGET = PATH_BLOG_WATCH + ".get_dynamodb_table"
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


class TestBlogWatch(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.logger = FakeLogger()

    def _bot_handler(self, env, conf, mock_tweepy, mock_dynamodb, mock_feed):
        def _fake_feedparse(url):
            return mock_feed.parse(url)

        with patch(D_TARGET, return_value=mock_dynamodb):
            with patch(T_TARGET, return_value=mock_tweepy):
                with patch('feedparser.parse', _fake_feedparse):
                    blog_watch.logger = self.logger
                    ret = blog_watch.bot_handler(env, conf)
        return ret

    def test_blog_watch(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(2, len(tw._update_statuses))
        item = dynamo.get_item(feed_item["id"])
        self.assertEqual(
            "http://ameblo.jp/fruits-box-blog/entry-12211554968.html",
            item['latest_id'])

        result_status_1 = "[New Update] Ede: Yoru-night! -> " + \
            "http://ameblo.jp/fruits-box-blog/entry-12210698546.html " + \
            "#Ede-chan"
        result_status_2 = "[New Update] Ede: Pop in Q -> " + \
            "http://ameblo.jp/fruits-box-blog/entry-12208663602.html " + \
            "#Ede-chan"
        self.assertIn(result_status_1, tw._update_statuses)
        self.assertIn(result_status_2, tw._update_statuses)

    def test_multiple_blog_watch(self):
        feed_item_1 = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        feed_item_2 = dict(
            id="feed_other",
            feed="http://otherexistsite.io/feed",
            latest_id="http://ameblo.jp/otakublo/entry-12290698546.html",
            search_condition="Hondo",
            body_format="[Guest Info] '{title}' -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item_1, feed_item_2])
        feed = FakeFeedparser({
            "http://existsite.io/feed": sample_blog_data,
            "http://otherexistsite.io/feed": sample_blog_data2})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(3, len(tw._update_statuses))
        # For blog 1
        item = dynamo.get_item(feed_item_1["id"])
        self.assertEqual(
            "http://ameblo.jp/fruits-box-blog/entry-12211554968.html",
            item['latest_id'])
        # For blog 2
        item = dynamo.get_item(feed_item_2["id"])
        self.assertEqual(
            "http://ameblo.jp/otakublo/entry-12311554968.html",
            item['latest_id'])

        result_status_1 = "[New Update] Ede: Yoru-night! -> " + \
            "http://ameblo.jp/fruits-box-blog/entry-12210698546.html " + \
            "#Ede-chan"
        result_status_2 = "[New Update] Ede: Pop in Q -> " + \
            "http://ameblo.jp/fruits-box-blog/entry-12208663602.html " + \
            "#Ede-chan"
        result_status_3 = "[Guest Info] 'Hondo-san has come as our guest'" + \
            " -> http://ameblo.jp/otakublo/entry-12311554968.html #Ede-chan"
        self.assertIn(result_status_1, tw._update_statuses)
        self.assertIn(result_status_2, tw._update_statuses)
        self.assertIn(result_status_3, tw._update_statuses)

    def test_multiple_blog_either_occurs_error(self):
        feed_item_1 = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        feed_item_2 = dict(
            id="feed_other",
            feed="http://otherexistsite.io/feed",
            latest_id="http://ameblo.jp/otakublo/entry-12290698546.html",
            search_condition="Hondo",
            body_format="[Guest Info] '{title}' -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item_1, feed_item_2])
        feed = FakeFeedparser({
            "http://existsite.io/feed": {},  # Feed result is unexpected
            "http://otherexistsite.io/feed": sample_blog_data2})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(1, len(tw._update_statuses))
        self.assertIn('Unexpected error on service blog-watch: '
                      'Please check DB record (id: feed)',
                      self.logger.lines_dict['error'][0])

    def test_empty_search_condition(self):
        # Empty search_condition is regarded as all conditions are rejected
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            body_format="[New Update] {title} -> {link}"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        item = dynamo.get_item(feed_item["id"])
        self.assertEqual(
            "http://ameblo.jp/fruits-box-blog/entry-12211554968.html",
            item['latest_id'])

    def test_empty_body_format(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertEqual("Unexpected error on service blog-watch: "
                         "Please check DB record (id: feed)"
                         ": Msg -> 'body_format must be defined'",
                         self.logger.lines_dict['error'][0])

    def test_invalid_body_format(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {titl} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertIn('{titl} is not available in blog entry.',
                      self.logger.lines_dict['error'][0])

    def test_empty_latest_id(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(2, len(tw._update_statuses))
        item = dynamo.get_item(feed_item["id"])
        self.assertEqual(
            "http://ameblo.jp/fruits-box-blog/entry-12211554968.html",
            item['latest_id'])

    def test_no_new_blog_update(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12211554966.html",
            body_format="[New Update] {title} -> {link}"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        # No update, but id is moved to latest id
        item = dynamo.get_item(feed_item["id"])
        self.assertEqual(
            "http://ameblo.jp/fruits-box-blog/entry-12211554968.html",
            item['latest_id'])

    def test_update_fail_no_index_change(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663602.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link}"
        )
        tw = FakeTweepyApi(update_error=True)
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        # Tweet error, so latest id is not moved
        item = dynamo.get_item(feed_item["id"])
        self.assertEqual(
            "http://ameblo.jp/fruits-box-blog/entry-12208663602.html",
            item['latest_id'])

    def test_empty_blogs(self):
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([])
        feed = FakeFeedparser()
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertEqual(1, len(self.logger.lines_dict['info']))

    def test_not_found_feed(self):
        wrong_feed_item = dict(
            id="wrong_feed",
            feed="http://noexistsite.io/feed"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([wrong_feed_item])
        feed = FakeFeedparser()
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertIn('No entries. Please check feed url setting.',
                      self.logger.lines_dict['error'][0])

    def test_second_search_do_nothing(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12208663600.html",
            search_condition="Ede:",
            body_format="[New Update] {title} -> {link} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        item = dynamo.get_item(feed_item["id"])
        self.assertEqual(
            "http://ameblo.jp/fruits-box-blog/entry-12211554968.html",
            item['latest_id'])

        # def fake function for _match_search_condition
        def _fake_msc(db_item, feed_entry, latest_id):
            match = False
            # Check if this entry should be searched
            if latest_id is None or latest_id < feed_entry.id:
                raise Exception("2nd try has come")
            return match
        # blog_watch._match_search_condition = _fake_match_search_condition
        with patch(PATH_BLOG_WATCH + '._match_search_condition', _fake_msc):
            self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(self.logger.lines_dict['error']))

    def test_blog_body_search_mock(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/ari-step/entry-12224195010.html",
            body_search=True,
            body_search_conditions=["Hondo-chan"],
            body_format="[New Update] {title} -> {link} #Ari-chan #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data3})
        req = FakeRequests(
            {'http://ameblo.jp/ari-step/entry-12226218315.html':
             sample_ameblo_blog_body})
        env = {'twitter_env': 'test'}

        with patch(PATH_BLOG_WATCH + '.requests', req):
            self._bot_handler(env, self.config, tw, dynamo, feed)
        result_status = "[New Update] Look this -> " + \
            "http://ameblo.jp/ari-step/entry-12226218315.html " + \
            "#Ari-chan #Ede-chan"
        self.assertEqual(1, len(tw._update_statuses))
        self.assertIn(result_status, tw._update_statuses)

    def test_blog_body_search_mock_no_match(self):
        # '4DX' word is found in link list but this should not be tweeted
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/ari-step/entry-12224195010.html",
            body_search=True,
            body_search_conditions=["4DX"],
            body_format="[New Update] {title} -> {link} #Ari-chan #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data3})
        req = FakeRequests(
            {'http://ameblo.jp/ari-step/entry-12226218315.html':
             sample_ameblo_blog_body})
        env = {'twitter_env': 'test'}

        with patch(PATH_BLOG_WATCH + '.requests', req):
            self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))

    def test_blog_body_search_online(self):
        # Check if Ameblo spec is not changed
        # Yui Ogura Blog Data
        ogusan_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'entries': [
                obj(id='http://ameblo.jp/ogurayui-0815/entry-12187666106.html',
                    title='Supply Water',
                    link='http://ameblo.jp/ogurayui-0815/'
                         'entry-12187666106.html'),
                obj(id='http://ameblo.jp/ogurayui-0815/entry-12186656735.html',
                    title='Hot and Spicy',
                    link='http://ameblo.jp/ogurayui-0815/'
                         'entry-12186656735.html'),
                obj(id='http://ameblo.jp/ogurayui-0815/entry-12186044375.html',
                    title='Summer Vacation',
                    link='http://ameblo.jp/ogurayui-0815/'
                         'entry-12186044375.html')
            ]
        }
        kyarisan_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'entries': [
                obj(id='http://ameblo.jp/ishiharakaori-0806/'
                        'entry-12225358373.html',
                    title='Pop in Q',
                    link='http://ameblo.jp/ishiharakaori-0806/'
                         'entry-12225358373.html'),
                obj(id='http://ameblo.jp/ishiharakaori-0806/'
                    'entry-12224315509.html',
                    title='Cocon Poi Poi Cocotama',
                    link='http://ameblo.jp/ishiharakaori-0806/'
                         'entry-12224315509.html'),
                obj(id='http://ameblo.jp/ishiharakaori-0806/'
                    'entry-12223186447.html',
                    title='Event',
                    link='http://ameblo.jp/ishiharakaori-0806/'
                         'entry-12223186447.html')
            ]
        }
        tanoway_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'entries': [
                obj(id='http://ameblo.jp/tanoue-marina/entry-12232581672.html',
                    title='Birthday',
                    link='http://ameblo.jp/tanoue-marina/'
                         'entry-12232581672.html'),
                obj(id='http://ameblo.jp/tanoue-marina/entry-12232298510.html',
                    title='VR',
                    link='http://ameblo.jp/tanoue-marina/'
                         'entry-12232298510.html'),
                obj(id='http://ameblo.jp/tanoue-marina/entry-12231980149.html',
                    title='Greeting 2',
                    link='http://ameblo.jp/tanoue-marina/'
                         'entry-12231980149.html')
            ]
        }
        arichan_blog_data = {
            'bozo_exception': {
                'message': 'document declared as us-ascii, but parsed as utf-8'
            },
            'encoding': 'utf-8',
            'entries': [
                obj(id='http://ameblo.jp/ari-step/entry-12233144905.html',
                    title='In these days...',
                    link='http://ameblo.jp/ari-step/entry-12233144905.html'),
                obj(id='http://ameblo.jp/ari-step/entry-12226218315.html',
                    title='Look this',
                    link='http://ameblo.jp/ari-step/entry-12226218315.html'),
                obj(id='http://ameblo.jp/ari-step/entry-12224195011.html',
                    title='4DX!!',
                    link='http://ameblo.jp/ari-step/entry-12224195011.html')
            ]
        }
        ogusan_feed_item = dict(
            id="ogusan",
            feed="http://existsite.io/ogusan",
            latest_id="http://ameblo.jp/ogurayui-0815/entry-12184451116.html",
            body_format="[New Update] {title} -> {link} #Yui-chan #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u3048\u30fc\u3067\u3061\u3083\u3093"]
            # edechan in Hiragana
        )
        kyarisan_feed_item = dict(
            id="kyarisan",
            feed="http://existsite.io/kyarisan",
            latest_id="http://ameblo.jp/ishiharakaori-0806/"
                      "entry-12223056549.html",
            body_format="[New Update] {title} -> {link} #Kyari-san #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u672c\u6e21"]
            # hondo in Kanji
        )
        tanoway_feed_item = dict(
            id="tanoway",
            feed="http://existsite.io/tanoway",
            latest_id="http://ameblo.jp/tanoue-marina/entry-12231636584.html",
            body_format="[New Update] {title} -> {link} #Tano-way #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u672c\u6e21"]
            # hondo in Kanji
        )
        arichan_feed_item = dict(
            id="tanoway",
            feed="http://existsite.io/arichan",
            latest_id="http://ameblo.jp/ari-step/entry-12223871525.html",
            body_format="[New Update] {title} -> {link} #Ari-chan #Ede-chan",
            body_search=True,
            body_search_conditions=[u"\u672c\u6e21"]
            # hondo in Kanji
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([ogusan_feed_item, kyarisan_feed_item,
                                    tanoway_feed_item, arichan_feed_item])
        feed = FakeFeedparser(
            {"http://existsite.io/ogusan": ogusan_blog_data,
             "http://existsite.io/kyarisan": kyarisan_blog_data,
             "http://existsite.io/tanoway": tanoway_blog_data,
             "http://existsite.io/arichan": arichan_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(5, len(tw._update_statuses))


if __name__ == '__main__':
    unittest.main()
