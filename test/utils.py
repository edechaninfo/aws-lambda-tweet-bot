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


class obj(dict):
    def __init__(self, *args, **kwargs):
        super(obj, self).__init__(**kwargs)
        self.d = kwargs

    def __getattr__(self, attr):
        return self.d[attr]


E_MSG_FLOAT = 'Float types are not supported. Use Decimal types instead.'


def validate_data_for_dynamo_db(data):
    # data should be dict type
    for k, v in data.items():
        if isinstance(v, dict):
            validate_data_for_dynamo_db(v)
        elif isinstance(v, list):
            for val in v:
                if isinstance(val, float):
                    raise TypeError(E_MSG_FLOAT)
        elif isinstance(v, tuple):
            for val in v:
                if isinstance(val, float):
                    raise TypeError(E_MSG_FLOAT)
        else:
            if isinstance(v, float):
                raise TypeError(E_MSG_FLOAT)
