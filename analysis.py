import argparse
import firebase_admin
from firebase_admin import firestore

# Arguments for output graph
parser = argparse.ArgumentParser(description='View data collected from Scouting App')
parser.add_argument('--database', '-d', required=True, help='Choose database')
parser.add_argument('--teams', '-t', nargs='+', required=True, help='Enter in team numbers to be displayed')
parser.add_argument('--x_axis', '-x', nargs='+', required=True, help='Values displayed on x-axis')
parser.add_argument('--y_axis', '-y', nargs='+', required=True, help='Values displayed on y-axis')
parser.add_argument('--cred', '-c', required=True, help='Path to database credentials')

args = parser.parse_args()

# Initialize firebase
# Enter path to JSON credentials
cred = firebase_admin.credentials.Certificate(args.cred)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Blank lists for values collected for graphing
# x = [[[]]*len(args.x_axis)]*len(args.teams) idk why tf this doesn't work
# y = [[[]]*len(args.y_axis)]*len(args.teams) or this
x = [[[] for i in range(len(args.x_axis))] for i in range(len(args.teams))]
y = [[[] for i in range(len(args.y_axis))] for i in range(len(args.teams))]

# Go through each response and collect data needed for graph and teams
for response in db.collection('response').stream():
    response_dict = response.to_dict()

    # Make sure response is valid
    if 'Team Number' not in response_dict:
        continue

    # Only save data to relevant teams
    if response_dict['Team Number'] in args.teams:
        for x_value in range(len(args.x_axis)):
            x[args.teams.index(response_dict['Team Number'])][x_value].append(response_dict[args.x_axis[x_value]])
        for y_value in range(0, len(args.y_axis)):
            y[args.teams.index(response_dict['Team Number'])][y_value].append(response_dict[args.y_axis[y_value]])

