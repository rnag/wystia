import examples
from argparse import ArgumentParser

from wystia import WistiaApi


parser = ArgumentParser(description='Script to list videos in a Wistia project')
parser.add_argument(
    'project_id',
    help='The hashed ID for a project on Wistia (ex. abc1234567)'
)
parser.add_argument(
    '-p', '--pretty',
    action='store_true',
    help='Print the prettified JSON string representation of the data.'
)

args = parser.parse_args()
project_id = args.project_id

videos = WistiaApi.list_videos(project_id)

print('Video Count:', len(videos))
print()
print('Videos:')
print('--')

if args.pretty:
    print(videos.prettify())
else:
    print(videos)
