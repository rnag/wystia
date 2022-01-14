import examples
from argparse import ArgumentParser

from wystia import WistiaApi


parser = ArgumentParser(description='Script to show customization settings (Embed Options) on a Wistia video')
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

customizations = WistiaApi.get_customizations(video_id)

print('Video Customizations:')
print('--')

if args.pretty:
    print(customizations.to_json(indent=4))
else:
    print(customizations)
