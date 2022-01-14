import examples
from argparse import ArgumentParser

from wystia import WistiaHelper


parser = ArgumentParser(
    description='Disable captions & audio descriptions in the player '
                'settings for a video on Wistia')
parser.add_argument(
    'video_id',
    help='The hashed ID for a video on Wistia (ex. abc1234567)'
)
parser.add_argument(
    '-o', '--on-by-default',
    action='store_true',
    help='Controls if captions are on by default when video starts playing'
)
parser.add_argument(
    '-p', '--pretty',
    action='store_true',
    help='Print the prettified JSON string representation of the data.'
)

args = parser.parse_args()
video_id = args.video_id
obd = args.on_by_default

customizations = WistiaHelper.disable_captions_and_ad(
    video_id,
    on_by_default=obd
)

print('Updated customizations:')
print('--')

if args.pretty:
    print(customizations.to_json(indent=4))
else:
    print(customizations)
