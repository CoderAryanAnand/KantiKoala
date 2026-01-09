import os
import re

versions_dir = 'migrations/versions'
files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]

revisions = {}
down_revisions = {}

for f in files:
    with open(os.path.join(versions_dir, f), 'r') as file:
        content = file.read()
        rev_match = re.search(r"revision = '(.*?)'", content)
        down_match = re.search(r"down_revision = '(.*?)'", content)
        
        if rev_match:
            rev = rev_match.group(1)
            down = down_match.group(1) if down_match else None
            revisions[rev] = f
            if down:
                down_revisions[down] = rev

# Find heads (revisions that are not down_revision of any other)
heads = [r for r in revisions if r not in down_revisions.values()]

print("Migration Heads:", heads)
