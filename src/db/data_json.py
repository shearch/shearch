"""
json command parser module

This demonstrates simple command base creation using data from example.json.
"""

import json
import os

json_file = os.path.join(os.path.dirname(__file__), 'example.json')
json_data = open(json_file)
data = json.load(json_data)

db = {}
"""Key is tag, value is hash command."""

command = {}
"""Key is hash command, value is item."""

uberset = set()
"""# Array of all keys (to be used with sets)."""

for item in data['item']:
    key = hash(item['command'])
    command[key] = item
    uberset.add(key)

    tags = item['tag']
    for tag in tags:
        if tag not in db:
            db[tag] = []
        db[tag].append(key)

def get_commands(tags):
    # tags have to be an array! Checking is omitted so be careful.
    result = []
    common = uberset

    for tag in tags:
        # Return empty array if tag has no commands.
        if tag not in db:
            return result
        common = common.intersection(set(db[tag]))

    for key in common:
        result.append(command[key])

    return result
