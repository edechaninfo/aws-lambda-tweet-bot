    Copyright 2016 edechaninfo

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

# Twitter Bot on AWS Lambda

English version will be available soon...

このソフトウェアは[AWS Lambda](https://aws.amazon.com/lambda/)と[Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
を使ってTwitterのBot機能を提供するものです。

動作中のアカウント[@edechaninfo](https://twitter.com/edechaninfo)

# 開発目的

声優の本渡楓さんに関するアニメ、ラジオ、イベント出演の情報などを、タイムリーに伝えることを目的として開発しています。

しかし、コードを可能な限り汎用化し、多目的に利用できるTwitter BOTを作成することを目指しています。

# デザインポリシー

- 設定（チェックするブログ、Twitterアカウントや検索条件）は全てDBで管理。認証以外の設定のためのソフトウェアの再デプロイは不要であること。
- マルチアカウント対応であること

# 実装済み機能

- ブログ更新情報通知機能（現在、アメブロのみ対応）
- Twitterアカウント、リストのタイムラインの条件付きRetweet機能（文字列部分一致のみ対応）
