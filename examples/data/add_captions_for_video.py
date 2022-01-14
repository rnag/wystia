import examples
from argparse import ArgumentParser
from pathlib import Path

from wystia import WistiaApi
from wystia.models import LanguageCode

default_file_path = str(
    Path(__file__).parent.parent.parent
    / 'tests' / 'testdata' / 'sample-captions.srt'
)

parser = ArgumentParser(description='Script to upload sample captions to a Wistia video')
parser.add_argument(
    'video_id',
    help='The hashed ID for a video on Wistia (ex. abc1234567)'
)
parser.add_argument(
    '-f', '--file_path',
    help='Path to an SRT captions file to upload',
    default=default_file_path
)
parser.add_argument(
    '-l', '--language',
    help='The language code for the Captions file',
    default='eng'
)

args = parser.parse_args()
file_path = args.file_path
video_id = args.video_id
lang_code = LanguageCode(args.language)

WistiaApi.create_captions(video_id, lang_code, srt_file=file_path)

print(f'Successfully uploaded {lang_code} captions for the video.')
