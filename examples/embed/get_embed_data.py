import examples
from argparse import ArgumentParser

from wystia import WistiaEmbedApi


parser = ArgumentParser(description='Script to retrieve embed data on a Wistia video')
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

embed_data = WistiaEmbedApi.get_data(video_id)

original_asset_url = WistiaEmbedApi.asset_url(video_id, embed_data)

print(f'Original Asset Url = {original_asset_url}')
print('Has Audio Description:', embed_data.has_audio_description)
print()

print('Video Embed Data:')
print('--')

if args.pretty:
    print(embed_data.to_json(indent=4))
else:
    print(embed_data)
