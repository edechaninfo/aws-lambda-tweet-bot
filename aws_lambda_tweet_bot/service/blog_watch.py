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

from HTMLParser import HTMLParser
import logging

import feedparser
import requests

from tweepy import TweepError
from aws_lambda_tweet_bot.utils import get_dynamodb_table, get_tweepy_api


SERVICE_ID = 'blog-watch'
logger = logging.getLogger('aws_lambda_tweet_bot.service.blog_watch')
logger.setLevel(logging.INFO)


class AmebloBodyParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_main_body = False
        self.count_div_in = 0
        self.articleText = ""
        self.article_classes = ['articleText', 'skin-entryBody']

    # handle unicode error in ameblo
    def parse_starttag(self, i):
        try:
            return HTMLParser.parse_starttag(self, i)
        except UnicodeDecodeError:
            pass

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.in_main_body:
                self.count_div_in += 1
            else:
                for attr in attrs:
                    key, val = attr
                    if key == 'class' and val in self.article_classes:
                        self.in_main_body = True

    def handle_data(self, data):
        if self.in_main_body:
            self.articleText += data

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_main_body:
            if self.count_div_in > 0:
                self.count_div_in -= 1
            else:
                self.in_main_body = False


def _blog_body(link):
    # stab
    try:
        r = requests.get(link)
        parser = AmebloBodyParser()
        parser.feed(r.text)
        parser.close()
        return parser.articleText
    except Exception as e:
        # catch all unexpected exception to avoid halting all search
        errmsg = "Unexpected error on parsing blog {}: Msg -> {}"
        logger.error(errmsg.format(link, str(e)))
        return ""


def _match_search_condition(db_item, feed_entry, latest_id):
    match = False
    # Check if this entry should be searched
    if latest_id is None or latest_id < feed_entry.id:
        title_search_condition = db_item.get('search_condition', None)
        if title_search_condition is not None:
            # title match
            match = title_search_condition in feed_entry.title
        if not match and db_item.get('body_search', False):
            # blog body match
            body = _blog_body(feed_entry.link)
            for cond in db_item.get('body_search_conditions', []):
                if cond in body:
                    match = True
                    break
    return match


def bot_handler(env, conf):
    logger.info('service "{}" started!"'.format(SERVICE_ID))
    blog_table = get_dynamodb_table('blog_watch', conf)
    blog_data = blog_table.scan()
    for blog_item in blog_data['Items']:
        try:
            feed_url = blog_item.get('feed', "")
            latest_id = blog_item.get('latest_id', None)
            tw_fail = False
            news_dic = feedparser.parse(feed_url)
            if len(news_dic['entries']) <= 0:
                raise Exception("No entries. Please check feed url setting.")
            for entry in news_dic['entries']:
                # Hack rss10/rss20 difference for Ameblo
                if not entry.get('id'):
                    setattr(entry, 'id', entry.link)
                if _match_search_condition(blog_item, entry, latest_id):
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

                    # tw_success = True
                    try:
                        api.update_status(twbody)
                        # updated = True
                        logger.info('Tweet Success!\n' +
                                    twbody.encode('utf_8'))
                    except TweepError as e:
                        if 'Status is a duplicate.' not in e.reason:
                            tw_fail = True
                            logger.error(str(e))
                if (blog_item.get('latest_id') is None or
                        blog_item['latest_id'] < entry.id):
                    blog_item['latest_id'] = entry.id
            if not tw_fail:
                blog_table.put_item(Item=blog_item)
            else:
                logger.info("Tweet is failed. Retry next attempt.")
        except Exception as e:
            errmsg = "Unexpected error on service {}: " + \
                     "Please check DB record (id: {}): Msg -> {}"
            logger.error(errmsg.format(SERVICE_ID, blog_item.get('id'),
                                       str(e)))
    return None  # no need to update env
