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

from config import Config
from aws_lambda_tweet_bot.service import blog_watch
from test import FakeDynamodbTable, FakeTweepyApi, FakeLogger
from test.service.sample_data import sample_blog_data, sample_blog_data2


D_TARGET = "aws_lambda_tweet_bot.service.blog_watch.get_dynamodb_table"
T_TARGET = "aws_lambda_tweet_bot.service.blog_watch.get_tweepy_api"


class FakeFeedparser(object):
    DEFAULT_RETURN = {
        "entries": [],
        "feed": {}
    }

    def __init__(self, results={}):
        self.results = results

    def parse(self, url):
        return self.results.get(url, self.DEFAULT_RETURN)


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
            "http://ameblo.jp/fruits-box-blog/entry-12210698546.html",
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
            "http://ameblo.jp/fruits-box-blog/entry-12210698546.html",
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
        # Empty search_condition is regarded as all conditions are passed
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
        self.assertEqual(3, len(tw._update_statuses))
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
            "http://ameblo.jp/fruits-box-blog/entry-12210698546.html",
            item['latest_id'])

    def test_no_new_blog_update(self):
        feed_item = dict(
            id="feed",
            feed="http://existsite.io/feed",
            latest_id="http://ameblo.jp/fruits-box-blog/"
                      "entry-12211554968.html",
            body_format="[New Update] {title} -> {link}"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([feed_item])
        feed = FakeFeedparser({"http://existsite.io/feed": sample_blog_data})
        env = {'twitter_env': 'test'}

        self._bot_handler(env, self.config, tw, dynamo, feed)
        self.assertEqual(0, len(tw._update_statuses))
        self.assertEqual("No blog update", self.logger.lines_dict['info'][-1])

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


if __name__ == '__main__':
    unittest.main()
