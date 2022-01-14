import examples
from argparse import ArgumentParser

from wystia import WistiaApi
from wystia.models import LanguageCode


parser = ArgumentParser(description='Script to list the captions on a Wistia video')
parser.add_argument(
    'video_id',
    help='The hashed ID for a video on Wistia (ex. abc1234567)'
)
parser.add_argument(
    '-l', '--language',
    help='The language code for the Captions file',
    default=None
)
parser.add_argument(
    '-p', '--pretty',
    action='store_true',
    help='Print the prettified JSON string representation of the data.'
)

args = parser.parse_args()
video_id = args.video_id
pretty = args.pretty
lang = args.language

print('Captions:')
print('--')

if lang:
    lang_code = LanguageCode(lang)
    captions = WistiaApi.get_captions(video_id, lang_code)
    print(captions.to_json(indent=4)) if pretty else print(captions)

else:
    captions = WistiaApi.list_captions(video_id)
    if pretty:
        print(captions.to_pretty_json())
    else:
        print(captions)
