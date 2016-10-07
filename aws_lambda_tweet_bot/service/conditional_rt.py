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


from tweepy import TweepError

from aws_lambda_tweet_bot.utils import get_dynamodb_table, get_tweepy_api


SERVICE_ID = 'conditional-rt'


def bot_handler(env):
    tapi = get_tweepy_api(env['twitter_env'])
    watch_tbl = get_dynamodb_table('tweet_watch')
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
                print "Skip '%v' because of unknown account type" % condition
                continue
        except TweepError as e:
            print "Cannot get timeline for " \
                  "{type}:{account} [id {id}]".format(**condition)
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
                    print "Retweeted successfully: " + \
                        status.text.encode('utf_8')
                except TweepError as e:
                    if 'You have already retweeted this tweet.' \
                        not in e.reason:
                        success = False
                        print str(e)
            if since_id < status.id:
                since_id = status.id

    if success:
        env['since_id'] = since_id
    return success