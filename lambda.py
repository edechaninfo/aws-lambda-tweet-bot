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


from aws_lambda_tweet_bot.utils import get_dynamodb_table
from aws_lambda_tweet_bot.service import blog_watch, conditional_rt


SERVICES = [
    blog_watch,
    conditional_rt
]


def lambda_handler(event, context):
    env_table = get_dynamodb_table('env')
    envs = env_table.scan()
    for env in envs['Items']:
        for srv in SERVICES:
            if srv.SERVICE_ID == env['service_id']:
                try:
                    success = srv.bot_handler(env)
                    if success:
                        # update env
                        env_table.put_item(Item=env)
                except Exception as e:
                    print "Error in executing '%s' service: %s" % \
                        (srv.SERVICE_ID, str(e))
                break


if __name__ == "__main__":
    lambda_handler(None, None)