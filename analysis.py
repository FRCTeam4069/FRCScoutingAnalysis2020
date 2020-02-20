#!/usr/bin/env python3

import argparse
import firebase_admin
import matplotlib.pyplot as plt
import numpy as np
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
        # Do this for the x and y axis values
        for axis_args, array in [(args.x_axis, x), (args.y_axis, y)]:
            for i, attr in enumerate(axis_args):
                team_number = response_dict['Team Number']
                team_idx = args.teams.index(team_number)
                # Sometimes there are blank strings
                try:
                    attr_value = float(response_dict[attr])
                except ValueError:
                    attr_value = np.nan
                array[team_idx][i].append(attr_value)

print(x)
print(y)

for team in range(len(args.teams)):
    for i in range(len(args.y_axis)):
        color = next(current_axis._get_lines.prop_cycler)['color']
        # Sort the X axis values so that the line graph looks right
        sort_order = np.argsort(x[team][0])
        x_values = np.array(x[team][0])[sort_order]
        y_values = np.array(y[team][i])[sort_order]
        plt.plot(x_values, y_values, label=args.teams[team], color=color)

        # Draw a secondary line containing the mean for that team
        mean = np.nanmean(y_values)
        x_range = [np.nanmin(x_values), np.nanmax(x_values)]
        plt.plot(x_range, [mean, mean], label=args.teams[team]+' Mean', linestyle='--', color=color)

plt.legend()
plt.show()
