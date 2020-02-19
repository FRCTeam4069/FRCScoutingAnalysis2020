import argparse

parser = argparse.ArgumentParser(description='View data collected from Scouting App')
parser.add_argument('--database', '-d', required=True, help='Choose database')
parser.add_argument('--teams', '-t', nargs='+', required=True, help='')
parser.add_argument('--x_axis', '-x', nargs='+', required=True, help='')
parser.add_argument('--y_axis', '-y', nargs='+', required=True, help='')

args = parser.parse_args()

print(args.teams)
