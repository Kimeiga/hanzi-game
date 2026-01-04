#!/usr/bin/env python3
"""Fix remaining duplicates and refine the mismatch detection."""
import json

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

changes = []

def find_and_update(node, char, new_keyword, new_meaning=None):
    if 'char' in node and node['char'] == char:
        old_kw = node.get('keyword', '')
        node['keyword'] = new_keyword
        if new_meaning:
            node['meaning'] = new_meaning
        changes.append((char, old_kw, new_keyword))
        return True
    if 'children' in node:
        for child in node['children']:
            if find_and_update(child, char, new_keyword, new_meaning):
                return True
    return False

# Fix remaining duplicates
duplicates_fixes = [
    # 'department': ['部', '科']
    # 部 = section/department/part, 科 = department/branch/subject
    ('部', 'section', 'section; department; part'),
    ('科', 'department', 'department; branch; subject; science'),
    
    # 'hillside': ['坂', '阪']
    # 坂 = slope (common in Japanese), 阪 = Osaka (place name component)
    ('坂', 'slope', 'slope; hill'),
    ('阪', 'Osaka', 'Osaka; embankment'),
    
    # 'recommend': ['薦', '奨']
    # 薦 = recommend, 奨 = encourage/prize
    ('奨', 'prize/encourage', 'prize; encourage; recommend'),
    # 薦 stays as recommend
]

# Additional refinements for cleaner keywords
refinements = [
    # Clean up some slash keywords that are too long
    ('大', 'big', 'big; large; great'),
    ('川', 'river', 'river; stream'),  # Keep it simple
    ('万', 'ten-thousand', '10,000; ten thousand; myriad'),
]

print("Fixing remaining issues...")

for item in duplicates_fixes + refinements:
    char, new_kw, meaning = item
    find_and_update(graph, char, new_kw, meaning)

print(f"\nApplied {len(changes)} changes:")
for char, old, new in changes:
    print(f"  {char}: '{old}' -> '{new}'")

# Save
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("\nSaved hanzi_semantic_graph.json")

