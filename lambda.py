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
