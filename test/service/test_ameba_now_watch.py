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

from aws_lambda_tweet_bot.service import ameba_now_watch
from test import FakeTweepyApi, FakeRequests
from test.service.sample_data import sample_ameblo_now_xml_body
from test.service.base import BaseTest


PATH_NOW_WATCH = "aws_lambda_tweet_bot.service.ameba_now_watch"
T_TARGET = PATH_NOW_WATCH + ".get_tweepy_api"


class TestAmebaNowWatch(BaseTest):
    def setUp(self):
        super(TestAmebaNowWatch, self).setUp()
        self.dynamo.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            TableName='test_ameba_now_watch',
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
        self.service_id = ameba_now_watch.SERVICE_ID

    def tearDown(self):
        super(TestAmebaNowWatch, self).tearDown()
        self.dynamo.delete_table(TableName='test_ameba_now_watch')

    def _bot_handler(self, conf, mock_tweepy, mock_req):
        env = self.get_env_from_local_dynamodb(self.service_id)

        with patch(T_TARGET, return_value=mock_tweepy):
            with patch(PATH_NOW_WATCH + '.requests', mock_req):
                ameba_now_watch.logger = self.logger
                ret = ameba_now_watch.bot_handler(env, conf)
        # check output env
        self.set_env_to_local_dynamodb(self.service_id, env)
        return ret

    def test_ameba_now_watch(self):
        now_item = dict(
            id="edechan",
            body_format="[Now Update] {text} {time} -> {url} #Ede-chan"
        )
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('ameba_now_watch', [now_item])
        env = {'twitter_env': 'test',
               'latest_id_indexes': {'edechan': Decimal(2023933629)}}
        self.set_env_to_local_dynamodb(self.service_id, env)
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(self.config, tw, req)

        env = self.get_env_from_local_dynamodb(self.service_id)
        self.assertEqual(5, len(tw._update_statuses))
        self.assertEqual(Decimal(2024494193),
                         env['latest_id_indexes']['edechan'])

        result_status_1 = \
            "[Now Update] All 12 stories of \"Konobi!\" in niconico anime" + \
            " special program. Yo-ho!!... " + \
            "[4/1 19:44] -> http://now.ameba.jp/hondo-kaede/2023952830/ " + \
            "#Ede-chan"
        result_status_2 = \
            "[Now Update] I watched Hokkyoku Ramen on TV " + \
            "[4/1 23:42] -> http://now.ameba.jp/hondo-kaede/2023952834/ " + \
            "#Ede-chan"
        result_status_3 = \
            "[Now Update] Thank you for coming to Girlish Number's Event!" + \
            " Please take a rest! I ... " + \
            "[4/10 00:29] -> http://now.ameba.jp/hondo-kaede/2024209752/ " + \
            "#Ede-chan"
        result_status_4 = \
            "[Now Update] I felt that this service should be closed.  " + \
            "internal URL testing. " + \
            "[4/15 06:17] -> http://now.ameba.jp/hondo-kaede/2024361621/ " + \
            "#Ede-chan"
        result_status_5 = \
            "[Now Update] Thank you for placing comments to me. I'm " + \
            "repeating the song Fifteenth... " + \
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
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('ameba_now_watch', [now_item])
        env = {'twitter_env': 'test',
               'latest_id_indexes': {'edechan': Decimal(2024361621)}}
        self.set_env_to_local_dynamodb(self.service_id, env)
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(self.config, tw, req)

        env = self.get_env_from_local_dynamodb(self.service_id)
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
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('ameba_now_watch', [now_item])
        env = {'twitter_env': 'test',
               'latest_id_indexes': {'edechan': Decimal(2024361621)}}
        self.set_env_to_local_dynamodb(self.service_id, env)
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(self.config, tw, req)

        env = self.get_env_from_local_dynamodb(self.service_id)
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
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('ameba_now_watch', [now_item])
        env = {'twitter_env': 'test'}
        self.set_env_to_local_dynamodb(self.service_id, env)
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(self.config, tw, req)

        env = self.get_env_from_local_dynamodb(self.service_id)
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
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('ameba_now_watch', [now_item])
        env = {'twitter_env': 'test'}
        self.set_env_to_local_dynamodb(self.service_id, env)
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(self.config, tw, req)

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
        tw = FakeTweepyApi(config=self.config)
        self.add_items_to_local_dynamodb('ameba_now_watch', [now_item])
        env = {'twitter_env': 'test'}
        self.set_env_to_local_dynamodb(self.service_id, env)
        req = FakeRequests(
            {'http://now.ameba.jp/api/entryList/edechan':
             sample_ameblo_now_xml_body})

        self._bot_handler(self.config, tw, req)

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
