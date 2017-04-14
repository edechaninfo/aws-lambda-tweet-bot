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
import os
import sys

from config import Config
from aws_lambda_tweet_bot.utils import get_dynamodb_table
from aws_lambda_tweet_bot.service import blog_watch, conditional_rt, \
    ameba_now_watch


SERVICES = [
    blog_watch,
    conditional_rt,
    ameba_now_watch
]
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def tweet_bot_main(event, context, conf):
    logger.info('got event {}'.format(event))
    env_table = get_dynamodb_table('env', conf)
    envs = env_table.scan()
    for env in envs['Items']:
        for srv in SERVICES:
            if srv.SERVICE_ID == env['service_id']:
                try:
                    success = srv.bot_handler(env, conf)
                    if success:
                        # update env
                        env_table.put_item(Item=env)
                except Exception as e:
                    logger.error("Error in executing '%s' service: %s" %
                                 (srv.SERVICE_ID, str(e)))
                break


def lambda_handler(event, context):
    """
    This is a start point from AWS Lambda
    """
    dir = os.path.dirname(__file__)
    conf_file = os.path.join(dir, 'credentials.conf')
    conf = Config(conf_file)
    tweet_bot_main(event, context, conf)


if __name__ == "__main__":
    # This handler is used for local env debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s '
                                  '- %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    lambda_handler(None, None)
