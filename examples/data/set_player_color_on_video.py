import examples
from argparse import ArgumentParser

from wystia import WistiaHelper


parser = ArgumentParser(
    description='Set the player color for a Wistia video')
parser.add_argument(
    'video_id',
    help='The hashed ID for a video on Wistia (ex. abc1234567)'
)
parser.add_argument(
    '-c', '--player-color',
    help='Player color to set on the video',
    default='#34d3c9'
)
parser.add_argument(
    '-p', '--pretty',
    action='store_true',
    help='Print the prettified JSON string representation of the data.'
)

args = parser.parse_args()
video_id = args.video_id
player_color = args.player_color

customizations = WistiaHelper.customize_video_on_wistia(
    video_id,
    player_color
)

print('Updated customizations:')
print('--')

if args.pretty:
    print(customizations.to_json(indent=4))
else:
    print(customizations)
