"""
json command parser module

This demonstrates simple command base creation using data from example.json.
"""

import json
import os

db = {}
"""Key is tag, value is hash command."""

command = {}
"""Key is hash command, value is item."""

uberset = set()
"""# Array of all keys (to be used with sets)."""

for json_file_name in os.listdir(os.path.dirname(__file__)):
    if json_file_name.endswith('.json'):
        json_file = os.path.join(os.path.dirname(__file__), json_file_name)
        json_data = open(json_file)
        data = json.load(json_data)

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
    # tags have to be in an array! Checking is omitted so be careful.
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
