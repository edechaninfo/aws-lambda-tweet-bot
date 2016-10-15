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


import boto3
import tweepy


def get_dynamodb_table_name(tenant_id, table_name):
    '''
    For multiple tenant feature, each dynamo DB's table name should start with
    tenant_id.
    '''
    return '%s_%s' % (tenant_id, table_name)


def get_dynamodb_table(table_name, conf):
    dynamo = boto3.resource('dynamodb', **conf.aws_config)
    env_table_name = get_dynamodb_table_name(conf.tenant_id, table_name)
    return dynamo.Table(env_table_name)


def get_tweepy_api(env, conf):
    twitter_config = conf.twitter_config
    auth = tweepy.OAuthHandler(twitter_config[env]['consumer_key'],
                               twitter_config[env]['consumer_secret'])
    auth.set_access_token(twitter_config[env]['access_token'],
                          twitter_config[env]['access_secret'])
    return tweepy.API(auth)
