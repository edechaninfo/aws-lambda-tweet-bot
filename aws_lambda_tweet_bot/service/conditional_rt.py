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

import logging

from tweepy import TweepError

from aws_lambda_tweet_bot.utils import get_dynamodb_table, get_tweepy_api


SERVICE_ID = 'conditional-rt'
logger = logging.getLogger('aws_lambda_tweet_bot.service.conditional_rt')
logger.setLevel(logging.INFO)


def bot_handler(env, conf):
    logger.info('service "{}" started!"'.format(SERVICE_ID))
    tapi = get_tweepy_api(env['twitter_env'], conf)
    watch_tbl = get_dynamodb_table('tweet_watch', conf)
    scan_data = watch_tbl.scan()
    since_id = env['since_id']
    success = True
    for condition in scan_data['Items']:
        tweets = []
        try:
            if condition['type'] == 'user':
                tweets = tapi.user_timeline(condition['account'],
                                            since_id=env['since_id'])
            elif condition['type'] == 'list':
                tweets = tapi.list_timeline(
                    owner_screen_name=condition['account'],
                    slug=condition['slug'],
                    since_id=env['since_id'])
            else:
                logger.warning("Skip '%v' because of unknown account type" %
                               condition)
                continue
        except TweepError as e:
            logger.error("Cannot get timeline for "
                         "{type}:{account} [id {id}]".format(**condition))
            continue

        for status in tweets:
            matches = False
            for str_cond in condition.get('match_strings', []):
                if str_cond in status.text:
                    matches = True
                    break
            if matches:
                try:
                    tapi.retweet(status.id)
                    logger.info("Retweeted successfully: \n" +
                                status.text.encode('utf_8'))
                except TweepError as e:
                    if 'You have already retweeted this tweet.' \
                            not in e.reason:
                        success = False
                        logger.error(str(e))
            if since_id < status.id:
                since_id = status.id

    if success:
        env['since_id'] = since_id
    return success
