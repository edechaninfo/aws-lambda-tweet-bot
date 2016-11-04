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

from test.utils import obj


sample_user_statuses = [
    {
        "id": 789035945014145025,
        "text": "Ede-chan is promising voice actor"
    },
    {
        "id": 789029558014135025,
        "text": "Recording will start soon :)",
        "extended_entities": {
            'media': [
                {
                    'id': 794502295782232064,
                    'media_url': 'http://pbs.twimg.com/media/hogehoge.jpg',
                    'type': 'photo'
                },
                {
                    'id': 794502295782232065,
                    'media_url': 'http://pbs.twimg.com/media/fugafuga.jpg',
                    'type': 'photo'
                }
            ]
        }
    },
    {
        "id": 789025958014135025,
        "text": "New anime program will be available soon"
    },
    {
        "id": 789025945014135025,
        "text": "We will invite Ede-chan for ANIME Fes!!"
    }
]

sample_list_statuses = [
    {
        "id": 789085945014145025,
        "text": "New cast announcement: Kaede Hondo!"
    },
    {
        "id": 789075958014135025,
        "text": "Blu-ray of KEIJO vol.1 is on sale!"
    },
    {
        "id": 789065945014135025,
        "text": "I went to Disney Land with my friend Ede-chan"
    },
    {
        "id": 789058945014135025,
        "text": "Ede-chan likes to behave like Maria-chan"
    }
]

sample_blog_data = {
    'bozo_exception': {
        'message': 'document declared as us-ascii, but parsed as utf-8'
    },
    'encoding': 'utf-8',
    'entries': [
        obj(id='http://ameblo.jp/fruits-box-blog/entry-12211554968.html',
            title='Minyami: Wake up, girls',
            link='http://ameblo.jp/fruits-box-blog/entry-12211554968.html'),
        obj(id='http://ameblo.jp/fruits-box-blog/entry-12210698546.html',
            title='Ede: Yoru-night!',
            link='http://ameblo.jp/fruits-box-blog/entry-12210698546.html'),
        obj(id='http://ameblo.jp/fruits-box-blog/entry-12208663602.html',
            title='Ede: Pop in Q',
            link='http://ameblo.jp/fruits-box-blog/entry-12208663602.html')
    ]
}

sample_blog_data2 = {
    'bozo_exception': {
        'message': 'document declared as us-ascii, but parsed as utf-8'
    },
    'encoding': 'utf-8',
    'entries': [
        obj(id='http://ameblo.jp/otakublo/entry-12311554968.html',
            title='Hondo-san has come as our guest',
            link='http://ameblo.jp/otakublo/entry-12311554968.html'),
        obj(id='http://ameblo.jp/otakublo/entry-12290698546.html',
            title="We will invite secret guest for today's program'",
            link='http://ameblo.jp/otakublo/entry-12290698546.html'),
        obj(id='http://ameblo.jp/otakublo/entry-12258663602.html',
            title='Next program will feature girlish number',
            link='http://ameblo.jp/otakublo/entry-12258663602.html')
    ]
}
