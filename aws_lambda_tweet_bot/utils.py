import boto3
import tweepy

from config import tenant_id, aws_config, twitter_config


def get_dynamodb_table_name(table_name):
    '''
    For multiple tenant feature, each dynamo DB's table name should start with
    tenant_id.
    '''
    return '%s_%s' % (tenant_id, table_name)


def get_dynamodb_table(table_name):
    dynamo = boto3.resource('dynamodb', **aws_config)
    env_table_name = get_dynamodb_table_name(table_name)
    return dynamo.Table(env_table_name)


def get_tweepy_api(env):
    auth = tweepy.OAuthHandler(twitter_config[env]['consumer_key'],
                               twitter_config[env]['consumer_secret'])
    auth.set_access_token(twitter_config[env]['access_token'],
                          twitter_config[env]['access_secret'])
    return tweepy.API(auth)
