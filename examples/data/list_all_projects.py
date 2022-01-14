import examples
from argparse import ArgumentParser

from wystia import WistiaApi


parser = ArgumentParser(description='Script to list all projects in a Wistia account')
parser.add_argument(
    '-p', '--pretty',
    action='store_true',
    help='Print the prettified JSON string representation of the data.'
)

args = parser.parse_args()

projects = WistiaApi.list_all_projects()

print('Project Count:', len(projects))
print()
print('Projects:')
print('--')

if args.pretty:
    print(projects.prettify())
else:
    print(projects)
