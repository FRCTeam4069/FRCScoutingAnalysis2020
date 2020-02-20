import argparse
import firebase_admin
import matplotlib.pyplot as plt
from firebase_admin import firestore

# Arguments for output graph
parser = argparse.ArgumentParser(description='View data collected from Scouting App')
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

# Graph stuff
current_axis = plt.gca()

# Blank lists for values collected for graphing
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
            x[args.teams.index(response_dict['Team Number'])][x_value].append(float(response_dict[args.x_axis[x_value]]))
        for y_value in range(0, len(args.y_axis)):
            y[args.teams.index(response_dict['Team Number'])][y_value].append(float(response_dict[args.y_axis[y_value]]))

for team in range(len(args.teams)):
    for i in range(len(args.y_axis)):
        mean = sum(y[team][i]) / len(y[team][i])
        color = next(current_axis._get_lines.prop_cycler)['color']

        plt.plot(sorted(x[team][0]), [x for _, x in sorted(zip(x[team][0], y[team][i]))],
                 label=args.teams[team], color=color)
        plt.plot(range(int(max(x[team][0]))), [mean for x in range(int(max(x[team][0])))],
                 label=args.teams[team]+' Mean', linestyle='--', color=color)

plt.legend()
plt.show()