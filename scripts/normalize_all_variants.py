#!/usr/bin/env python3
"""
Normalize all variant glosses to share the same base with appropriate suffixes.

Rules:
- Traditional form: "gloss (trad)"  
- Simplified (Chinese): "gloss (simp)"
- Japanese shinjitai: "gloss (jp)"
- Traditional also used in Japanese: "gloss (trad/jp)"
- If all forms identical: just "gloss"
"""
import json
import re
import opencc
from jp_shinjitai_mapping import JP_SHINJITAI

# Load data
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)
with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
    jlpt = json.load(f)
with open('web-app/static/game_data/joyo_kanji.json', 'r') as f:
    joyo = json.load(f)

jlpt_joyo = set(jlpt['N5'] + jlpt['N4'] + jlpt['N3'] + jlpt['N2'] + jlpt['N1'] + joyo)

# OpenCC converters
t2s = opencc.OpenCC('t2s')
s2t = opencc.OpenCC('s2t')

# Build char->node map
char_to_node = {}
def build_map(node):
    if 'char' in node:
        char_to_node[node['char']] = node
    if 'children' in node:
        for child in node['children']:
            build_map(child)
build_map(graph)

print(f"Total chars: {len(char_to_node)}")
print(f"JP shinjitai mappings: {len(JP_SHINJITAI)}")

# Build reverse mapping: trad -> jp
TRAD_TO_JP = {v: k for k, v in JP_SHINJITAI.items()}

def clean_keyword(kw):
    """Remove existing suffixes and clean up."""
    kw = re.sub(r'\s*\((jp|trad|simp|trad/jp|var|ii)\)\s*$', '', kw)
    kw = re.sub(r'\s+', ' ', kw).strip()
    return kw

def is_bad_keyword(kw):
    """Check if keyword needs fixing."""
    kw_lower = kw.lower()
    return ('variant of' in kw_lower or 
            kw_lower.startswith('[') or
            'japanese' in kw_lower and 'variant' in kw_lower)

changes = []

# Process all characters
for char, node in char_to_node.items():
    old_kw = node.get('keyword', '')
    if not old_kw:
        continue
    
    # Determine relationships
    is_jp_shinjitai = char in JP_SHINJITAI
    trad_form = JP_SHINJITAI.get(char)  # If this is JP, get its trad
    jp_form = TRAD_TO_JP.get(char)  # If this is trad, get its JP
    
    simp = t2s.convert(char)
    trad = s2t.convert(char)
    
    is_simplified = (trad != char)  # Has a different traditional form
    is_traditional = (simp != char)  # Has a different simplified form
    
    # Determine the "canonical" form to get base gloss from
    canonical = None
    suffix = ''
    
    if is_jp_shinjitai:
        # This is Japanese shinjitai - use traditional form's gloss
        canonical = trad_form
        suffix = '(jp)'
    elif jp_form and jp_form in jlpt_joyo:
        # This is traditional, and there's a JP shinjitai form in JLPT/Joyo
        suffix = '(trad)'
    elif is_simplified and not is_jp_shinjitai:
        # Chinese simplified
        suffix = '(simp)'
    elif is_traditional:
        # Traditional with Chinese simplified
        # Check if also used in Japanese (in JLPT/Joyo)
        if char in jlpt_joyo:
            suffix = '(trad/jp)'
        else:
            suffix = '(trad)'
    
    # Get base gloss
    if canonical and canonical in char_to_node:
        base = clean_keyword(char_to_node[canonical]['keyword'])
    else:
        base = clean_keyword(old_kw)
    
    # Fix bad keywords by looking up the referenced character
    if is_bad_keyword(base):
        match = re.search(r'variant of (\S+)', old_kw, re.IGNORECASE)
        if match:
            ref = match.group(1)
            ref = re.sub(r'[\[\(].*', '', ref).split('|')[0].strip()
            if len(ref) == 1 and ref in char_to_node:
                base = clean_keyword(char_to_node[ref]['keyword'])
                if not suffix:
                    suffix = '(var)'
    
    # Construct new keyword
    new_kw = f"{base} {suffix}".strip() if suffix else base
    
    if new_kw != old_kw:
        node['keyword'] = new_kw
        changes.append((char, old_kw, new_kw))

print(f"\nTotal changes: {len(changes)}")

# Show changes grouped
jp_changes = [(c,o,n) for c,o,n in changes if '(jp)' in n]
trad_changes = [(c,o,n) for c,o,n in changes if '(trad)' in n and '(trad/jp)' not in n]
simp_changes = [(c,o,n) for c,o,n in changes if '(simp)' in n]
tradjp_changes = [(c,o,n) for c,o,n in changes if '(trad/jp)' in n]
var_changes = [(c,o,n) for c,o,n in changes if '(var)' in n]

print(f"\n(jp) changes: {len(jp_changes)}")
for c,o,n in jp_changes[:10]:
    print(f"  {c}: '{o}' -> '{n}'")

print(f"\n(trad) changes: {len(trad_changes)}")
for c,o,n in trad_changes[:10]:
    print(f"  {c}: '{o}' -> '{n}'")

print(f"\n(simp) changes: {len(simp_changes)}")
for c,o,n in simp_changes[:10]:
    print(f"  {c}: '{o}' -> '{n}'")

print(f"\n(trad/jp) changes: {len(tradjp_changes)}")
for c,o,n in tradjp_changes[:10]:
    print(f"  {c}: '{o}' -> '{n}'")

print(f"\n(var) changes: {len(var_changes)}")
for c,o,n in var_changes[:10]:
    print(f"  {c}: '{o}' -> '{n}'")

# Save
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("\nSaved!")

