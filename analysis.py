import argparse

parser = argparse.ArgumentParser(description='View data collected from Scouting App')
parser.add_argument('--config', '-c', required=True, help='Config filename')

args = parser.parse_args()

print(args.config)
