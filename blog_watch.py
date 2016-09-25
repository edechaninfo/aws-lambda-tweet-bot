# -*- coding: utf-8 -*-

import boto3
import feedparser
import tweepy
from tweepy import TweepError

from config import aws_config, twitter_config

SERVICE_ID = 'blog-watch'
dynamo = boto3.resource('dynamodb', **aws_config)


def _get_twitter_api(env):
    auth = tweepy.OAuthHandler(twitter_config[env]['consumer_key'],
                               twitter_config[env]['consumer_secret'])
    auth.set_access_token(twitter_config[env]['access_token'],
                          twitter_config[env]['access_secret'])
    return tweepy.API(auth)


def lambda_handler(event, context):
    blog_table = dynamo.Table('blog_watch')
    blog_item = blog_table.get_item(Key={'id': 'hondo'})
    feed_url = blog_item['Item']['feed']
    latest_id = blog_item['Item']['latest_id']

    updated = False
    hondo_news_dic = feedparser.parse(feed_url)
    for entry in hondo_news_dic['entries']:
        if (latest_id < entry.id and 
            blog_item['Item']['search_condition'] in entry.title):
            twbody = blog_item['Item']['body_format'].format(**entry)

            env_table = dynamo.Table('env')
            env_item = env_table.get_item(Key={'service_id': SERVICE_ID})
            api = _get_twitter_api(env_item['Item']['twitter_env'])

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
                blog_item['Item']['latest_id'] = entry.id
                blog_table.put_item(Item=blog_item['Item'])
            break
    if not updated:
        print "No blog update"


if __name__ == "__main__":
    lambda_handler(None, None)
