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

import json
import os
import sys
import argparse
from itertools import count
from logging import INFO, WARNING, DEBUG, getLogger
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from importlib_metadata import version
from pathlib import Path
from typing import Iterable, List, Optional
from google.cloud import storage

try:
    __version__ = version('stanford-wdl-kit')
except:
    __version__ = "development"

LOG = getLogger(__name__)


def delete_blobs(blobs: List[storage.Blob], client: storage.Client):
    """Deletes a list of blobs"""
    for b in blobs:
        b.delete(client)


def generate_chunks(slices: List, chunk_size: int = 32) -> Iterable[List]:
    """Given an indefinitely long list, return the list in 32 item chunks."""
    while len(slices):
        chunk = slices[:chunk_size]
        yield chunk
        slices = slices[chunk_size:]


def sequencer() -> Iterable[str]:
    """Generate an indefinite sequence of _0000.tmp,... string prefixes."""
    for s in count(0):
        yield f"_{s:04d}.tmp"


def _compose(destination: str, blobs: List[storage.Blob], seq: List[str], client: storage.Client, delete: bool = False) -> List[storage.Blob]:
    """Performs a single pass over a list of blobs, composing every 32 or less blobs into a new blob.
    Arguments:
        destination {str} -- prefix blob name for temporary blobs
        blobs {list} -- list of blobs to compose on
        seq {iterable function} -- returns a unique string to append to temp file
        delete {bool} -- delete source files after composition
        client {storage.Client} -- GCS storage client
    Returns:
        List[blob] -- a list of the composed blobs
    """
    chonks: List[storage.Blob] = []
    for blob_list in generate_chunks(blobs):
        chonk = storage.Blob.from_string(destination + next(seq))
        chonk.compose(blob_list, client)
        chonks.append(chonk)
    if delete:
        delete_blobs(blobs, client)
    return chonks


@dataclass_json
@dataclass
# https://cloud.google.com/storage/docs/json_api/v1/objects/compose
class ComposeConfig():
    # gs:// URI to final composed object
    destination: str
    # URI prefix used to find source blobs
    sourcePrefix: str
    # Delimiter for prefix, usually /
    sourceDelimiter: Optional[str] = None
    # Deletes source files after successful composition
    deleteSources: Optional[bool] = False


def compose(config: ComposeConfig):
    """
    Composes GCS blobs into a single concatenated blob (supports > 32 blobs)
    """
    client = storage.Client()

    final_blob = storage.Blob.from_string(config.destination)

    blobs = list(client.list_blobs(
        final_blob.bucket, prefix=config.sourcePrefix, delimiter=config.sourceDelimiter))

    if len(blobs) == 0:
        sys.exit("Could not find any storage objects matching {} using delimiter {}".format(
            config.sourcePrefix, config.sourceDelimiter))

    if len(blobs) > 32:
        seq = sequencer()
        chunks = _compose(config.destination, blobs, seq, client)
        while len(chunks) > 32:
            chunks = _compose(config.destination, chunks,
                              seq, client, delete=True)
        final_blob.compose(chunks, client)
        delete_blobs(chunks, client)
    else:
        final_blob.compose(blobs, client)

    if config.deleteSources:
        delete_blobs(blobs, client)

    print(json.dumps(final_blob._properties, indent=2, sort_keys=True))


@dataclass_json
@dataclass
class DownloadConfig():
    # Source bucket
    sourceBucket: str
    # prefix used to find source blobs in bucket
    sourcePrefix: str
    # Delimiter for prefix, usually /
    sourceDelimiter: Optional[str] = None
    # Deletes source files after successful download
    deleteSources: Optional[bool] = False
    # By default, objects in a path eg. a/b/c/d.txt download as 'd.txt', as WDL doesn't support subdirs
    # Set this to 'True' to embed the path in the filename using underscores, eg. "a/b/c/d.txt -> a_b_c_d.txt"
    keepPrefix: Optional[bool] = False


def download(config: DownloadConfig):
    """
    Downloads all GCS objects matching a prefix to a local directory
    """
    client = storage.Client()

    final_blob = storage.Blob.from_string(config.sourceBucket)

    blobs = list(client.list_blobs(
        final_blob.bucket, prefix=config.sourcePrefix, delimiter=config.sourceDelimiter))

    if len(blobs) == 0:
        sys.exit("Could not find any storage objects matching {} using delimiter {}".format(
            config.sourcePrefix, config.sourceDelimiter))

    blob: storage.Blob
    files: List[str] = []
    # Do NOT add multithreading here, to encourage 'scatter' parallelism+caching in WDL
    for blob in blobs:
        if config.keepPrefix:
            destination_uri = blob.name.replace("/", "_")
        else:
            destination_uri = blob.name.split('/')[blob.name.count('/')]
        
        blob.download_to_filename(destination_uri)
        files.append(destination_uri)

    if config.deleteSources:
        delete_blobs(blobs, client)

    print(json.dumps(files, indent=2, sort_keys=True))

@dataclass_json
@dataclass
class UploadConfig():
    # Source bucket
    sourceBucket: str
    # prefix used to find source blobs in bucket
    sourcePrefix: str
    # source file for upload
    sourceFile: str

def upload(config: UploadConfig):
    """
    Upload a file to a local directory
    """
    client = storage.Client()
    
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # sourceBucket = "your-bucket-name"
    # The path to your file to upload
    # sourceFile = "local/path/to/file"
    # The ID of your GCS object
    # sourcePrefix = "storage-object-name"

    bucket = client.bucket(config.sourceBucket)
    blob = bucket.blob(config.sourcePrefix)

    blob.upload_from_filename(config.sourceFile)

    print(json.dumps(blob._properties, indent=2, sort_keys=True))


def main(args=None):
    parser = argparse.ArgumentParser(description="JSON GCS utilities")

    parser.add_argument('--project_id', metavar='PROJECT_ID', type=str,
                        help='Project ID when creating a new client (default: infer from environment)')

    parser.add_argument('--credentials', metavar='KEY.JSON', type=str,
                        help='JSON credentials file (default: infer from environment)')

    parser.add_argument('command', choices=[
                        'download', 'compose', 'upload'], type=str.lower, help='command to execute')

    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('config', help='JSON configuration file for command')
    args = parser.parse_args()

    config = Path(args.config).read_text()

    if args.project_id is not None:
        os.environ['GCP_PROJECT'] = args.project_id
    if args.credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    if args.command == "compose":
        compose(config=ComposeConfig.from_json(config))

    if args.command == "download":
        download(config=DownloadConfig.from_json(config))

    if args.command == "upload":
        upload(config=UploadConfig.from_json(config))

if __name__ == '__main__':
    sys.exit(main())
