#!/usr/bin/env python3

import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
import firebase_admin
from firebase_admin import firestore

# Arguments for output graph
parser = argparse.ArgumentParser(description='View data collected from Scouting App')
parser.add_argument('--teams', '-t', nargs='+', required=True, help='Enter in team numbers to be displayed')
parser.add_argument('--x_axis', '-x', required=True, help='Values displayed on x-axis')
parser.add_argument('--y_axis', '-y', required=True, help='Values displayed on y-axis')
parser.add_argument('--cred', '-c', required=True, help='Path to database credentials')

args = parser.parse_args()

# Initialize firebase
# Enter path to JSON credentials
cred = firebase_admin.credentials.Certificate(args.cred)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Blank lists for values collected for graphing
x = [[] for i in range(len(args.teams))]
y = [[] for i in range(len(args.teams))]

# Make sure we find all the teams; if not, exit with an error
found_teams = {num: False for num in args.teams}

# Go through each response and collect data needed for graph and teams
for response in db.collection('response').stream():
    response_dict = response.to_dict()

    # Make sure response is valid
    if 'Team Number' not in response_dict:
        continue

    # Only save data to relevant teams
    if response_dict['Team Number'] in args.teams:
        # Do this for the x and y axis values
        for attr, array in [(args.x_axis, x), (args.y_axis, y)]:
            team_number = response_dict['Team Number']
            found_teams[team_number] = True
            team_idx = args.teams.index(team_number)
            # Sometimes there are blank strings
            try:
                attr_value = float(response_dict[attr])
            except ValueError:
                attr_value = np.nan
            array[team_idx].append(attr_value)

teams_not_found = []
for num in args.teams:
    if not found_teams[num]:
        teams_not_found.append(num)
if teams_not_found:
    print('Teams', teams_not_found, 'not found')
    sys.exit()

fig, (line_ax, hist_ax) = plt.subplots(1, 2)

for team in range(len(args.teams)):
    color = next(line_ax._get_lines.prop_cycler)['color']

    # Sort the X axis values so that the line graph looks right
    sort_order = np.argsort(x[team])
    x_values = np.array(x[team])[sort_order]
    y_values = np.array(y[team])[sort_order]
    line_ax.plot(x_values, y_values, label=args.teams[team], color=color)

    # Draw a secondary line containing the mean for that team
    mean = np.nanmean(y_values)
    x_range = [np.nanmin(x_values), np.nanmax(x_values)]
    line_ax.plot(x_range, [mean, mean], label=args.teams[team]+' Mean', linestyle='--', color=color)

    # Also create a histogram of the variable for this team
    hist_ax.hist(y_values, color=color, histtype='stepfilled', alpha=0.2)

line_ax.set_xlabel(args.x_axis)
line_ax.set_ylabel(args.y_axis)
hist_ax.set_xlabel(args.y_axis)
hist_ax.set_ylabel('Occurrences')
fig.legend()
plt.show()
