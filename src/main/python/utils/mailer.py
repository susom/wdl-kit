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

import logging
import argparse
import requests
import os
import sys
from google.cloud import storage
from urllib.parse import urlparse

logging.basicConfig(level=logging.ERROR)


def send_notification(mailgun_api_url, mailgun_api_uri, sender, mailto, subject, body):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(mailgun_api_uri[0])
    api_key_blob = bucket.blob(mailgun_api_uri[1])
    api_key = api_key_blob.download_as_text()
    return requests.post(
        mailgun_api_url,
        auth=("api", api_key),
        data={"from": sender,
              "to": mailto,
              "subject": subject,
              "html": body})


def type_uri(value):
    value = value.lower()
    if not value.startswith("gs://"):
        raise argparse.ArgumentTypeError(
            "must be in the form gs://bucket/object, you specified {}".format(value))
    parsed = urlparse(value)
    return parsed.netloc, parsed.path[1:]


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Simple email message utility")
    parser.add_argument('--mailgun_api_url', required=True,
                        help='URL of the mailgun api that we will use to send the email.')
    parser.add_argument('--mailgun_api_uri', required=True, type=type_uri,
                        help='URI to GCS object containing mailgun API key')
    parser.add_argument(
        '--mailto', help='email address(es) to send result (comma-separated)', required=True)
    parser.add_argument('--message', help='email body', required=True)
    parser.add_argument('--subject', help='email subject', required=True)
    parser.add_argument(
        '--sender', help='email sender, eg. "Sender <sender@sender.stanford.edu>"', required=True)
    parser.add_argument('--credentials', required=False,
                        help='Specify path to a GCP JSON credentials file')
    parser.add_argument('--project_id', required=False, help='GCP project id')

    args = parser.parse_args()

    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.project_id is not None:
        os.environ['GCLOUD_PROJECT'] = args.project_id

    response = send_notification(args.mailgun_api_url, args.mailgun_api_uri,
                                 args.sender, args.mailto, args.subject, args.message)
    response.raise_for_status()


if __name__ == '__main__':
    sys.exit(main())
