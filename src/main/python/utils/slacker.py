# Copyright 2022 The Board of Trustees of The Leland Stanford Junior University.
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

import os
import logging
import argparse
import sys
from urllib.parse import urlparse
from slack_sdk import WebClient
from google.cloud import storage
from slack_sdk.errors import SlackApiError


def main(args=None):

    parser = argparse.ArgumentParser(
        description="Utility to send Slack messages from WDL")

    parser.add_argument('--project_id', metavar='PROJECT_ID', type=str,
                        help='Project ID when creating a new client (default: infer from environment)')

    parser.add_argument('--credentials', metavar='KEY.JSON', type=str,
                        help='JSON credentials file (default: infer from environment)')
    parser.add_argument('--slack_uri', type=str,
                        help='Uri that points to the file that contains the bot token for the slack API.')
    parser.add_argument('--channel', type=str,
                        help='Channel to send the slack message to.')
    parser.add_argument('--message', type=str,
                        help='Message to send to specified slack channel.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR)

    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.project_id is not None:
        os.environ['GCLOUD_PROJECT'] = args.project_id

    slackToken = args.slack_uri
    if slackToken.startswith("gs://"):
        parsed = urlparse(slackToken)
        storage_client = storage.Client()
        bucket = storage_client.bucket(parsed.netloc)
        token_blob = bucket.blob(parsed.path[1:])
        slackToken = token_blob.download_as_string().decode('ASCII')

    if slackToken is None:
        slackToken = os.environ["SLACK_API_TOKEN"]

    message = args.message
    channel = args.channel
    client = WebClient(token=slackToken)

    response = client.chat_postMessage(
        as_user=True,
        channel=channel,
        text=message
    )


if __name__ == '__main__':
    sys.exit(main())
