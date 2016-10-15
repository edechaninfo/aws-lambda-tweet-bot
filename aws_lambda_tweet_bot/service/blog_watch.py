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


import feedparser

from tweepy import TweepError
from aws_lambda_tweet_bot.utils import get_dynamodb_table, get_tweepy_api


SERVICE_ID = 'blog-watch'


def bot_handler(env, conf):
    blog_table = get_dynamodb_table('blog_watch', conf)
    blog_data = blog_table.scan()
    for blog_item in blog_data['Items']:
        feed_url = blog_item['feed']
        latest_id = blog_item['latest_id']
        updated = False
        news_dic = feedparser.parse(feed_url)
        for entry in news_dic['entries']:
            if (latest_id < entry.id and
                    blog_item['search_condition'] in entry.title):
                twbody = blog_item['body_format'].format(**entry)
                api = get_tweepy_api(env['twitter_env'], conf)

                tw_success = True
                try:
                    api.update_status(twbody)
                    updated = True
                    print 'Tweet Success!\n' + twbody.encode('utf_8')
                except TweepError as e:
                    if 'Status is a duplicate.' not in e.reason:
                        tw_success = False
                        print str(e)
                if tw_success:
                    blog_item['latest_id'] = entry.id
                    blog_table.put_item(Item=blog_item)
                break
        if not updated:
            print "No blog update"
    return None  # no need to update env
