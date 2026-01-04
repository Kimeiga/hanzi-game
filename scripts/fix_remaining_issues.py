#!/usr/bin/env python3
"""Fix remaining keyword issues."""
import json

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

changes = []

def find_and_update(node, char, new_keyword):
    if 'char' in node and node['char'] == char:
        old_kw = node.get('keyword', '')
        node['keyword'] = new_keyword
        changes.append((char, old_kw, new_keyword))
        return True
    if 'children' in node:
        for child in node['children']:
            if find_and_update(child, char, new_keyword):
                return True
    return False

# Fix too-long keywords (keep suffix format)
too_long_fixes = [
    ('繰', 'reel silk (trad/jp)'),
    ('届', 'reach (simp)'),
    ('銃', 'gun (trad/jp)'),
    ('鉢', 'bowl (trad/jp)'),
    ('嵐', 'storm (trad/jp)'),
    ('絹', 'silk (trad/jp)'),
    ('唄', 'song (trad/jp)'),
    ('箇', 'counter (trad/jp)'),
    ('錮', 'imprison (trad/jp)'),
]

# Fix duplicates (differentiate meanings)
duplicate_fixes = [
    # 'bosom': ['胸', '懐']
    ('胸', 'chest'),  # physical chest
    ('懐', 'bosom (trad/jp)'),  # figurative/nostalgic
    
    # 'bribe (trad/jp)': ['賄', '賂']
    ('賄', 'bribe (trad/jp)'),
    ('賂', 'bribery (trad/jp)'),
    
    # 'careful (trad/jp)': ['謹', '諦']
    ('謹', 'respectful (trad/jp)'),  # 謹 = respectful/careful
    ('諦', 'abandon (trad/jp)'),  # 諦 = give up/resign
    
    # 'general (jp)': ['将', '総']
    ('将', 'commander (jp)'),  # military general
    ('総', 'general (jp)'),  # overall/total
    
    # 'night': ['夜', '晩']
    ('夜', 'night'),
    ('晩', 'evening'),
    
    # 'rest': ['憩', '休']
    ('憩', 'repose'),  # leisure rest
    ('休', 'rest'),  # regular rest
    
    # 'summon': ['徴', '召']
    ('徴', 'levy (trad/jp)'),  # collect/conscript
    ('召', 'summon'),  # call forth
]

# Also fix 気 which should include "spirit"
# And fix a few other meaning issues noted
meaning_fixes = [
    ('気', 'spirit (jp)'),  # 気 is more "spirit/mind" in Japanese
    ('会', 'meet (jp)'),  # 会 primary meaning is "meet"
]

print("Fixing too-long keywords...")
for char, new_kw in too_long_fixes:
    find_and_update(graph, char, new_kw)

print("Fixing duplicate keywords...")
for char, new_kw in duplicate_fixes:
    find_and_update(graph, char, new_kw)

print("Fixing meaning issues...")
for char, new_kw in meaning_fixes:
    find_and_update(graph, char, new_kw)

print(f"\nApplied {len(changes)} changes:")
for char, old, new in changes:
    print(f"  {char}: '{old}' -> '{new}'")

# Also need to update the traditional forms to match
# Find traditional forms and update them too
import opencc
t2s = opencc.OpenCC('t2s')
s2t = opencc.OpenCC('s2t')

def get_keyword(char):
    def find_kw(node):
        if 'char' in node and node['char'] == char:
            return node.get('keyword', '')
        if 'children' in node:
            for child in node['children']:
                r = find_kw(child)
                if r:
                    return r
        return None
    return find_kw(graph)

# For simplified chars that we changed, update their traditional forms
print("\nSyncing traditional forms...")
sync_changes = []
for char, new_kw in duplicate_fixes + meaning_fixes:
    trad = s2t.convert(char)
    if trad != char:
        # Get base without suffix
        import re
        base = re.sub(r'\s*\([^)]+\)\s*$', '', new_kw)
        trad_kw = f"{base} (trad)"
        current = get_keyword(trad)
        if current and current != trad_kw:
            find_and_update(graph, trad, trad_kw)
            sync_changes.append((trad, current, trad_kw))

for char, old, new in sync_changes:
    print(f"  {char}: '{old}' -> '{new}'")

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("\nSaved!")

