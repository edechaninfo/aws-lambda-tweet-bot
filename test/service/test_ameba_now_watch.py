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
import unittest

from config import Config
from aws_lambda_tweet_bot.service import ameba_now_watch
from test import FakeDynamodbTable, FakeTweepyApi, FakeLogger, FakeRequests
from test.service.sample_data import sample_ameblo_now_xml_body
from test.utils import validate_data_for_dynamo_db


PATH_NOW_WATCH = "aws_lambda_tweet_bot.service.ameba_now_watch"
D_TARGET = PATH_NOW_WATCH + ".get_dynamodb_table"
T_TARGET = PATH_NOW_WATCH + ".get_tweepy_api"


class TestAmebaNowWatch(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.logger = FakeLogger()

    def _bot_handler(self, env, conf, mock_tweepy, mock_dynamodb, mock_req):
        # check input env
        validate_data_for_dynamo_db(env)

        with patch(D_TARGET, return_value=mock_dynamodb):
            with patch(T_TARGET, return_value=mock_tweepy):
                with patch(PATH_NOW_WATCH + '.requests', mock_req):
                    ameba_now_watch.logger = self.logger
                    ret = ameba_now_watch.bot_handler(env, conf)
        # check output env
        validate_data_for_dynamo_db(env)
        return ret

    def test_ameba_now_watch(self):
        now_item = dict(
            id="edechan",
            body_format="[Now Update] {text} {time} -> {url} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([now_item])
        env = {'twitter_env': 'test',
               'latest_id_indexes': {'edechan': Decimal(2023933629)}}
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(env, self.config, tw, dynamo, req)
        self.assertEqual(5, len(tw._update_statuses))
        self.assertEqual(Decimal(2024494193),
                         env['latest_id_indexes']['edechan'])

        result_status_1 = \
            "[Now Update] All 12 stories of \"Konobi!\" in niconico anime" + \
            " special program. Yo-ho!!  " + \
            "[4/1 19:44] -> http://now.ameba.jp/hondo-kaede/2023952830/ " + \
            "#Ede-chan"
        result_status_2 = \
            "[Now Update] I watched Hokkyoku Ramen on TV " + \
            "[4/1 23:42] -> http://now.ameba.jp/hondo-kaede/2023952834/ " + \
            "#Ede-chan"
        result_status_3 = \
            "[Now Update] Thank you for coming to Girlish Number's Event!" + \
            " Please take a rest! I will post ... " + \
            "[4/10 00:29] -> http://now.ameba.jp/hondo-kaede/2024209752/ " + \
            "#Ede-chan"
        result_status_4 = \
            "[Now Update] I felt that this service should be closed.  " + \
            "internal URL testing. " + \
            "[4/15 06:17] -> http://now.ameba.jp/hondo-kaede/2024361621/ " + \
            "#Ede-chan"
        result_status_5 = \
            "[Now Update] Thank you for placing comments to me. I'm " + \
            "repeating the song Fifteenth Moon infi... " + \
            "[4/19 15:22] -> http://now.ameba.jp/hondo-kaede/2024494193/ " + \
            "#Ede-chan"
        self.assertIn(result_status_1, tw._update_statuses)
        self.assertIn(result_status_2, tw._update_statuses)
        self.assertIn(result_status_3, tw._update_statuses)
        self.assertIn(result_status_4, tw._update_statuses)
        self.assertIn(result_status_5, tw._update_statuses)

    def test_ameba_now_watch_short(self):
        now_item = dict(
            id="edechan",
            text_length=Decimal(15),
            body_format="[Now Update] {text} {time} -> {url} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([now_item])
        env = {'twitter_env': 'test',
               'latest_id_indexes': {'edechan': Decimal(2024361621)}}
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(env, self.config, tw, dynamo, req)
        self.assertEqual(1, len(tw._update_statuses))
        self.assertEqual(Decimal(2024494193),
                         env['latest_id_indexes']['edechan'])

        result_status_1 = \
            "[Now Update] Thank you for p... " + \
            "[4/19 15:22] -> http://now.ameba.jp/hondo-kaede/2024494193/ " + \
            "#Ede-chan"
        self.assertIn(result_status_1, tw._update_statuses)

    def test_ameba_now_watch_short_with_truncate_sub(self):
        now_item = dict(
            id="edechan",
            text_length=Decimal(15),
            body_format="[Now Update] {text} {time} -> {url} #Ede-chan",
            truncate_sub="...(truncated)"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([now_item])
        env = {'twitter_env': 'test',
               'latest_id_indexes': {'edechan': Decimal(2024361621)}}
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(env, self.config, tw, dynamo, req)
        self.assertEqual(1, len(tw._update_statuses))
        self.assertEqual(Decimal(2024494193),
                         env['latest_id_indexes']['edechan'])

        result_status_1 = \
            "[Now Update] Thank you for p...(truncated) " + \
            "[4/19 15:22] -> http://now.ameba.jp/hondo-kaede/2024494193/ " + \
            "#Ede-chan"
        self.assertIn(result_status_1, tw._update_statuses)

    def test_ameba_now_watch_empty_latest_index(self):
        now_item = dict(
            id="edechan",
            body_format="[Now Update] {text} {time} -> {url} #Ede-chan"
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([now_item])
        env = {'twitter_env': 'test'}
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(env, self.config, tw, dynamo, req)
        self.assertEqual(8, len(tw._update_statuses))
        self.assertEqual(Decimal(2024494193),
                         env['latest_id_indexes']['edechan'])

    def test_ameba_now_watch_photo_sub_format(self):
        now_item = dict(
            id="edechan",
            body_format="[Now Update] {text} {photo_sub} -> {url} #Ede-chan",
            photo_sub="[Photo Available]",
            text_length=Decimal(15)
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([now_item])
        env = {'twitter_env': 'test'}
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(env, self.config, tw, dynamo, req)
        self.assertEqual(8, len(tw._update_statuses))

        result_status_1 = \
            "[Now Update] Oh (;_;) Love a... [Photo Available] " + \
            "-> http://now.ameba.jp/hondo-kaede/2023810192/ " + \
            "#Ede-chan"
        # space is increased
        result_status_8 = \
            "[Now Update] Thank you for p...  " + \
            "-> http://now.ameba.jp/hondo-kaede/2024494193/ " + \
            "#Ede-chan"
        self.assertEqual(result_status_1, tw._update_statuses[0])
        self.assertEqual(result_status_8, tw._update_statuses[7])

    def test_ameba_now_watch_photo_sub_format_without_photo_sub_value(self):
        now_item = dict(
            id="edechan",
            body_format="[Now Update] {text} {photo_sub} -> {url} #Ede-chan",
            text_length=Decimal(15)
        )
        tw = FakeTweepyApi()
        dynamo = FakeDynamodbTable([now_item])
        env = {'twitter_env': 'test'}
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(env, self.config, tw, dynamo, req)
        self.assertEqual(8, len(tw._update_statuses))

        result_status_1 = \
            "[Now Update] Oh (;_;) Love a...  " + \
            "-> http://now.ameba.jp/hondo-kaede/2023810192/ " + \
            "#Ede-chan"
        # space is increased
        result_status_8 = \
            "[Now Update] Thank you for p...  " + \
            "-> http://now.ameba.jp/hondo-kaede/2024494193/ " + \
            "#Ede-chan"
        self.assertEqual(result_status_1, tw._update_statuses[0])
        self.assertEqual(result_status_8, tw._update_statuses[7])


if __name__ == '__main__':
    unittest.main()
