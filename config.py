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
from ConfigParser import SafeConfigParser


logger = logging.getLogger('config')
logger.setLevel(logging.INFO)


class Config(object):
    # default values
    values = dict(
        tenant_id=None,
        aws_config=dict(
            aws_access_key_id=None,
            aws_secret_access_key=None,
            region_name=None,
            endpoint_url=None,
        ),
        twitter_config=dict(
            development=dict(
                consumer_key=None,
                consumer_secret=None,
                access_token=None,
                access_secret=None,
            ),
            production=dict(
                consumer_key=None,
                consumer_secret=None,
                access_token=None,
                access_secret=None,
            ),
            test=dict(
                consumer_key=None,
                consumer_secret=None,
                access_token=None,
                access_secret=None,
            )
        )
    )

    def __init__(self, conf_file=None):
        if conf_file is None:
            # conf_file is not specified. Return empty config
            return
        if not os.path.exists(conf_file):
            logger.warning("Not Found Config File: " + conf_file)
            return
        p = SafeConfigParser()
        p.read(conf_file)

        self.values['tenant_id'] = self._safe_parse('default', 'tenant_id', p)

        for key in ['aws_access_key_id', 'aws_secret_access_key',
                    'region_name', 'endpoint_url']:
            self.values['aws_config'][key] = self._safe_parse('aws', key, p)

        for type in ['production', 'development', 'test']:
            for key in ['consumer_key', 'consumer_secret', 'access_token',
                        'access_secret']:
                self.values['twitter_config'][type][key] = \
                    self._safe_parse('twitter:' + type, key, p)

        self._fill_by_environment_variables()

    def _fill_by_environment_variables(self):
        """
        Fill None twitter config values with following environment variables.
        Basically, that will be filled in CI system
        - TW_{TYPE}_CONSUMER_KEY: consumer_key
        - TW_{TYPE}_CONSUMER_SECRET: consumer_secret
        - TW_{TYPE}_ACCESS_TOKEN: access_token
        - TW_{TYPE}_ACCESS_SECRET: access_secret
        """
        for type in ['production', 'development', 'test']:
            for key in ['consumer_key', 'consumer_secret', 'access_token',
                        'access_secret']:
                if self.values['twitter_config'][type][key] is None:
                    self.values['twitter_config'][type][key] = \
                        os.environ.get('TW_{}_{}'.format(type.upper(),
                                                         key.upper()))

    def _safe_parse(self, section, option, parser):
        try:
            return parser.get(section, option)
        except Exception:
            logger.warning("Read config error: section: %s, option: %s" %
                           (section, option))
        return None

    @property
    def tenant_id(self):
        return self.values['tenant_id']

    @property
    def aws_config(self):
        return self.values['aws_config']

    @property
    def twitter_config(self):
        return self.values['twitter_config']

    def __str__(self):
        return str(self.values)


if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    conf_file = os.path.join(dir, 'credentials.conf')
    conf = Config(conf_file)
    print conf
