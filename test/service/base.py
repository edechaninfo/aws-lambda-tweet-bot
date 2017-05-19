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

import os
import unittest

import boto3

from aws_lambda_tweet_bot.utils import get_dynamodb_table
from config import Config

from test import FakeLogger


class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        basepath = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(
            os.path.join(basepath, '../credentials_local.conf'))
        cls.config = Config(filepath)
        cls.dynamo = boto3.client('dynamodb', **cls.config.aws_config)
        resp = cls.dynamo.list_tables()
        for table_name in resp.get('TableNames', []):
            cls.dynamo.delete_table(TableName=table_name)

    def setUp(self):
        self.logger = FakeLogger()
        self.dynamo.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'service_id',
                    'AttributeType': 'S'
                },
            ],
            TableName='test_env',
            KeySchema=[
                {
                    'AttributeName': 'service_id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            },
        )

    def tearDown(self):
        self.dynamo.delete_table(TableName='test_env')

    def add_items_to_local_dynamodb(self, table_name, items):
        table = get_dynamodb_table(table_name, self.config)
        for item in items:
            table.put_item(Item=item)

    def get_env_from_local_dynamodb(self, service_id):
        table = get_dynamodb_table('env', self.config)
        resp = table.get_item(Key={'service_id': service_id})
        return resp['Item']

    def set_env_to_local_dynamodb(self, service_id, item):
        item['service_id'] = service_id
        self.add_items_to_local_dynamodb('env', [item])
