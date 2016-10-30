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

import feedparser

from tweepy import TweepError
from aws_lambda_tweet_bot.utils import get_dynamodb_table, get_tweepy_api


SERVICE_ID = 'blog-watch'
logger = logging.getLogger('aws_lambda_tweet_bot.service.blog_watch')
logger.setLevel(logging.INFO)


def bot_handler(env, conf):
    logger.info('service "{}" started!"'.format(SERVICE_ID))
    blog_table = get_dynamodb_table('blog_watch', conf)
    blog_data = blog_table.scan()
    for blog_item in blog_data['Items']:
        try:
            feed_url = blog_item.get('feed', "")
            latest_id = blog_item.get('latest_id', None)
            updated = False
            news_dic = feedparser.parse(feed_url)
            if len(news_dic['entries']) <= 0:
                raise Exception("No entries. Please check feed url setting.")
            for entry in news_dic['entries']:
                if ((latest_id is None or latest_id < entry.id) and
                        blog_item.get('search_condition', '') in entry.title):
                    if not blog_item.get('body_format'):
                        raise KeyError("body_format must be defined")

                    try:
                        twbody = blog_item['body_format'].format(**entry)
                    except KeyError as e:
                        errKey = str(e)[1:-1]
                        raise Exception("{%s} is not available in blog "
                                        "entry. Please check body_format." %
                                        errKey)
                    api = get_tweepy_api(env['twitter_env'], conf)

                    tw_success = True
                    try:
                        api.update_status(twbody)
                        updated = True
                        logger.info('Tweet Success!\n' +
                                    twbody.encode('utf_8'))
                    except TweepError as e:
                        if 'Status is a duplicate.' not in e.reason:
                            tw_success = False
                            logger.error(str(e))
                    if tw_success and (blog_item.get('latest_id') is None or
                                       blog_item['latest_id'] < entry.id):
                        blog_item['latest_id'] = entry.id
            if updated:
                blog_table.put_item(Item=blog_item)
            else:
                logger.info("No blog update")
        except Exception as e:
            errmsg = "Unexpected error on service {}: " + \
                     "Please check DB record (id: {}): Msg -> {}"
            logger.error(errmsg.format(SERVICE_ID, blog_item.get('id'),
                                       str(e)))
    return None  # no need to update env
