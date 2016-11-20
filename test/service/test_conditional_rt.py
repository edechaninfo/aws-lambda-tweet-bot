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

from tweepy import TweepError

from aws_lambda_tweet_bot.service import conditional_rt
from config import Config
from test import FakeDynamodbTable, FakeTweepyApi, FakeLogger
from test.service.sample_data import sample_user_statuses, \
    sample_list_statuses


D_TARGET = "aws_lambda_tweet_bot.service.conditional_rt.get_dynamodb_table"
T_TARGET = "aws_lambda_tweet_bot.service.conditional_rt.get_tweepy_api"


class TestConditionalRT(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.logger = FakeLogger()

    def _bot_handler(self, env, conf, mock_tweepy, mock_dynamodb):
        with patch(D_TARGET, return_value=mock_dynamodb):
            with patch(T_TARGET, return_value=mock_tweepy):
                conditional_rt.logger = self.logger
                ret = conditional_rt.bot_handler(env, conf)
        return ret

    def test_user_timeline(self):
        tweet_watches = [
            dict(id=5, type='user', account='acc', match_strings=['Ede-chan'])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(user=dict(acc=sample_user_statuses)))
        env = dict(twitter_env='test', since_id=709025945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(2, len(mock_tweepy._retweet_ids))
        self.assertEqual(789035945014145025, env['since_id'])
        self.assertIn(789035945014145025, mock_tweepy._retweet_ids)
        self.assertIn(789025945014135025, mock_tweepy._retweet_ids)

    def test_list_timeline(self):
        tweet_watches = [
            dict(id=6, type='list', account='acc', slug='list',
                 match_strings=['Ede-chan'])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(list=dict(acc=dict(
            list=sample_list_statuses))))
        env = dict(twitter_env='test', since_id=788058945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(2, len(mock_tweepy._retweet_ids))
        self.assertEqual(789085945014145025, env['since_id'])
        self.assertIn(789065945014135025, mock_tweepy._retweet_ids)
        self.assertIn(789058945014135025, mock_tweepy._retweet_ids)

    def test_user_timeline_with_photo(self):
        tweet_watches = [
            dict(id=5, type='user', account='acc', match_strings=['Ede-chan'],
                 photo=True)
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(user=dict(acc=sample_user_statuses)))
        env = dict(twitter_env='test', since_id=709025945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(3, len(mock_tweepy._retweet_ids))
        self.assertEqual(789035945014145025, env['since_id'])
        self.assertIn(789035945014145025, mock_tweepy._retweet_ids)
        self.assertIn(789029558014135025, mock_tweepy._retweet_ids)
        self.assertIn(789025945014135025, mock_tweepy._retweet_ids)

    def test_list_timeline_with_blacklist(self):
        tweet_watches = [
            dict(id=6, type='list', account='acc', slug='list',
                 match_strings=['Ede-chan'],
                 blacklist_keywords=['Maria-chan'])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(list=dict(acc=dict(
            list=sample_list_statuses))))
        env = dict(twitter_env='test', since_id=788058945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(1, len(mock_tweepy._retweet_ids))
        self.assertEqual(789085945014145025, env['since_id'])
        self.assertIn(789065945014135025, mock_tweepy._retweet_ids)
        self.assertIn("Keyword 'Maria-chan' is blacklist so following "
                      "tweet is not retweeted",
                      self.logger.lines_dict['info'][-1])

    def test_multiple_timeline(self):
        tweet_watches = [
            dict(id=5, type='user', account='acc',
                 match_strings=['Ede-chan']),
            dict(id=6, type='list', account='acc', slug='list',
                 match_strings=['Ede-chan'])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(
            user=dict(acc=sample_user_statuses),
            list=dict(acc=dict(list=sample_list_statuses))))
        env = dict(twitter_env='test', since_id=788058945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(4, len(mock_tweepy._retweet_ids))
        self.assertEqual(789085945014145025, env['since_id'])

    def test_multiple_match_strings(self):
        tweet_watches = [
            dict(id=6, type='list', account='acc', slug='list',
                 match_strings=['Ede-chan', 'Hondo'])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(list=dict(acc=dict(
            list=sample_list_statuses))))
        env = dict(twitter_env='test', since_id=788058945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(3, len(mock_tweepy._retweet_ids))
        self.assertEqual(789085945014145025, env['since_id'])
        self.assertIn(789085945014145025, mock_tweepy._retweet_ids)
        self.assertIn(789065945014135025, mock_tweepy._retweet_ids)
        self.assertIn(789058945014135025, mock_tweepy._retweet_ids)

    def test_mulliple_timelines_incl_invalid(self):
        tweet_watches = [
            dict(id=7, type='user', match_strings=['Ede-chan']),
            dict(id=5, type='user', account='acc',
                 match_strings=['Ede-chan']),
            dict(id=9, type='account', account='acc',
                 match_strings=['Ede-chan']),
            dict(id=8, type='list', account='acc',
                 match_strings=['Ede-chan']),
            dict(id=6, type='list', account='acc', slug='list',
                 match_strings=['Ede-chan']),
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(
            user=dict(acc=sample_user_statuses),
            list=dict(acc=dict(list=sample_list_statuses))))
        env = dict(twitter_env='test', since_id=788058945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(4, len(mock_tweepy._retweet_ids))
        self.assertEqual(789085945014145025, env['since_id'])
        self.assertIn('account field is required',
                      self.logger.lines_dict['error'][0])
        self.assertIn('slug field is required for list type',
                      self.logger.lines_dict['error'][1])
        self.assertIn('unknown account type',
                      self.logger.lines_dict['warning'][0])

    def test_empty_match_strings_no_retweet(self):
        tweet_watches = [
            dict(id=5, type='user', account='acc', match_strings=[])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(user=dict(acc=sample_user_statuses)))
        env = dict(twitter_env='test', since_id=709025945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(0, len(mock_tweepy._retweet_ids))
        self.assertEqual(789035945014145025, env['since_id'])

    def test_empty_match_strings_and_photo(self):
        tweet_watches = [
            dict(id=5, type='user', account='acc', photo=True)
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(user=dict(acc=sample_user_statuses)))
        env = dict(twitter_env='test', since_id=709025945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(1, len(mock_tweepy._retweet_ids))
        self.assertIn(789029558014135025, mock_tweepy._retweet_ids)
        self.assertEqual(789035945014145025, env['since_id'])

    def test_list_timeline_get_error(self):
        tweet_watches = [
            dict(id=6, type='list', account='acc', slug='list',
                 match_strings=['Ede-chan'])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(
            list=dict(acc=dict(list=TweepError('something happened')))))
        env = dict(twitter_env='test', since_id=788058945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(0, len(mock_tweepy._retweet_ids))
        self.assertEqual("Cannot get timeline for list:acc:list [id 6]: "
                         "message=something happened",
                         self.logger.lines_dict['error'][0])

    def test_one_timeline_get_failed(self):
        # In the first try, user timeline retweet fails due to unexpected
        # reason. This time, since_id should not be updated because some
        # tweets of failure account might be missed to retweet if since_id is
        # updated. In the next try, tweet issue is fixed so user timeline will
        # be retweeted properly. In this time, list timeline tweets can
        # (be attempted to) be retweeted, but tweepy client will return
        # TweepError. This service needs to skip 'already retweeted' error.
        tweet_watches = [
            dict(id=5, type='user', account='acc',
                 match_strings=['Ede-chan']),
            dict(id=6, type='list', account='acc', slug='list',
                 match_strings=['Ede-chan'])
        ]
        mock_dynamodb = FakeDynamodbTable(tweet_watches)
        mock_tweepy = FakeTweepyApi(dict(
            user=dict(acc=TweepError('something happened')),
            list=dict(acc=dict(list=sample_list_statuses))))
        env = dict(twitter_env='test', since_id=788058945014135025)

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(2, len(mock_tweepy._retweet_ids))
        self.assertEqual(0, mock_tweepy._retweet_error_count)
        self.assertEqual(788058945014135025, env['since_id'])
        self.assertEqual("Cannot get timeline for user:acc [id 5]: "
                         "message=something happened",
                         self.logger.lines_dict['error'][0])

        # 2nd try
        mock_tweepy._set_statuses(dict(
            user=dict(acc=sample_user_statuses),
            list=dict(acc=dict(list=sample_list_statuses))))

        self._bot_handler(env, self.config, mock_tweepy, mock_dynamodb)
        self.assertEqual(4, len(mock_tweepy._retweet_ids))
        self.assertEqual(2, mock_tweepy._retweet_error_count)
        self.assertEqual(789085945014145025, env['since_id'])


if __name__ == '__main__':
    unittest.main()
