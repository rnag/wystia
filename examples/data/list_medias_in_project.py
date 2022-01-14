import examples
from argparse import ArgumentParser

from wystia import WistiaApi


parser = ArgumentParser(description='Script to list medias in a Wistia project')
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

medias = WistiaApi.list_project(project_id)

print('Media Count:', len(medias))
print()
print('Medias:')
print('--')

if args.pretty:
    print(medias.prettify())
else:
    print(medias)
