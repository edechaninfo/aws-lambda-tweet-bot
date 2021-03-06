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
        try:
            try:
                type = condition['type']
                account = condition['account']
            except KeyError as e:
                errKey = str(e)[1:-1]
                raise KeyError('%s field is required' % errKey)
            tweets = []
            env_since_id = env.get('since_id', 1)
            if type == 'user':
                try:
                    tweets = tapi.user_timeline(account,
                                                since_id=env_since_id,
                                                tweet_mode='extended')
                except TweepError as e:
                    errMsg = ("Cannot get timeline for user:{account} "
                              "[id {id}]").format(**condition)
                    logger.error("%s: message=%s", errMsg, str(e))
                    success = False
                    continue
            elif type == 'list':
                slug = condition.get('slug')
                if not slug:
                    raise KeyError('slug field is required for list type')
                try:
                    tweets = tapi.list_timeline(owner_screen_name=account,
                                                slug=slug,
                                                since_id=env_since_id,
                                                tweet_mode='extended')
                except TweepError as e:
                    errMsg = ("Cannot get timeline for list:{account}:"
                              "{slug} [id {id}]").format(**condition)
                    logger.error("%s: message=%s", errMsg, str(e))
                    success = False
                    continue
            else:
                logger.warning("Skip '%s' because of unknown account type" %
                               condition)
                continue

            rt_of_rt = condition.get('rt_of_rt', False)
            for status in tweets:
                matches = False
                full_text = status.full_text

                # if retweet of retweet is allowed, full_text is
                # rewritten by retweeted_status.full_text if
                # retweeted_status is available because
                # retweeted_status.full_text is 'real' full text
                if rt_of_rt and hasattr(status, 'retweeted_status'):
                    full_text = status.retweeted_status.full_text

                # check inclusion conditions
                for str_cond in condition.get('match_strings', []):
                    if str_cond in full_text:
                        matches = True
                        break
                if condition.get('photo'):
                    if hasattr(status, 'extended_entities'):
                        matches = True

                # check exclusion conditions

                if matches and full_text.startswith('@'):
                    # reply tweet must not be retweeted
                    matches = False
                if matches:
                    # retweet of retweet is 'not allowed', retweet status
                    # is not allowed
                    if not rt_of_rt and hasattr(status, 'retweeted_status'):
                        logger.info("Following tweet is not made by original "
                                    "author so not retweeted:\n%s",
                                    full_text.encode('utf_8'))
                        matches = False
                if matches:
                    # Even if condition matches, tweets are filtered by
                    # blacklist keywords
                    for blk_word in condition.get('blacklist_keywords', []):
                        if blk_word in full_text:
                            matches = False
                            msg = ("Keyword '%s' is blacklist so following "
                                   "tweet is not retweeted:\n%s")
                            logger.info(msg %
                                        (blk_word, full_text.encode('utf_8')))
                            break

                # finally condition matches, this status will be retweeted
                if matches:
                    try:
                        tapi.retweet(status.id)
                        logger.info("Retweeted successfully: \n" +
                                    full_text.encode('utf_8'))
                    except TweepError as e:
                        if 'You have already retweeted this tweet.' \
                                not in e.reason:
                            success = False
                            logger.error(str(e))

                # get latest status id from which is searched in next cycle
                if since_id < status.id:
                    since_id = status.id
        except Exception as e:
            errmsg = "Unexpected error on service {}: " + \
                     "Please check DB record (id: {}): Msg -> {}"
            logger.error(errmsg.format(SERVICE_ID, condition.get('id'),
                                       str(e)))

    if success:
        env['since_id'] = since_id
    return success
