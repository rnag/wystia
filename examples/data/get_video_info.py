import examples
from argparse import ArgumentParser

from wystia import WistiaApi


parser = ArgumentParser(description='Script to show info on a Wistia video')
parser.add_argument(
    'video_id',
    help='The hashed ID for a video on Wistia (ex. abc1234567)'
)
parser.add_argument(
    '-p', '--pretty',
    action='store_true',
    help='Print the prettified JSON string representation of the data.'
)

args = parser.parse_args()
video_id = args.video_id

vd = WistiaApi.get_video(video_id)

print('Video Data:')
print('--')

if args.pretty:
    print(vd.to_json(indent=4))
else:
    print(vd)
