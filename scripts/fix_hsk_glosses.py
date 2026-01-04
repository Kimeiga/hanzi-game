#!/usr/bin/env python3
"""Fix HSK gloss formatting issues."""
import json
import re

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

changes = []

# Specific fixes
MANUAL_FIXES = {
    '説': 'speak (trad/jp)',
    '麽': '(suffix) (simp)',
    '兩': 'two (trad)',
    '俻': 'prepare',
    '讀': 'read (trad)',
    '說': 'speak (trad)',
    '冷': 'cold',
}

def fix_node(node):
    if 'keyword' in node:
        kw = node['keyword']
        char = node.get('char', '?')

        # Apply manual fixes
        if char in MANUAL_FIXES:
            new_kw = MANUAL_FIXES[char]
            if new_kw != kw:
                changes.append((char, kw, new_kw))
                node['keyword'] = new_kw
                return

        # Fix "Word Word" patterns with suffix
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', kw):
            suffix_match = re.search(r'(\s*\([^)]+\))$', kw)
            if suffix_match:
                suffix = suffix_match.group(1)
                base = kw[:suffix_match.start()]
                new_kw = base.split()[0].lower() + suffix
                if new_kw != kw:
                    changes.append((char, kw, new_kw))
                    node['keyword'] = new_kw
            elif '(trad' not in kw and '(jp' not in kw and '(simp' not in kw:
                words = kw.split()
                new_kw = words[0].lower()
                if new_kw != kw:
                    changes.append((char, kw, new_kw))
                    node['keyword'] = new_kw

        # Fix too-long keywords
        elif len(kw) > 30:
            if '(' in kw:
                match = re.match(r'^(.+?)(\s*\([^)]+\))$', kw)
                if match:
                    base, suffix = match.groups()
                    new_base = base.split()[0].lower()
                    new_kw = new_base + suffix
                    if len(new_kw) <= 30:
                        changes.append((char, kw, new_kw))
                        node['keyword'] = new_kw

    if 'children' in node:
        for child in node['children']:
            fix_node(child)

fix_node(graph)

print(f"Fixed {len(changes)} glosses:")
for char, old, new in changes:
    print(f"  {char}: \"{old}\" -> \"{new}\"")

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("Saved!")

