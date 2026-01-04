#!/usr/bin/env python3
"""
Normalize glosses for character variants (trad/simp/jp) to share the same base gloss.

Rules:
- If char is simplified: "gloss (simp)"
- If char is traditional: "gloss (trad)"
- If char is Japanese shinjitai: "gloss (jp)"
- If trad and jp are same form: "gloss (trad/jp)"
- If all forms are identical: just "gloss" (no suffix)
"""
import json
import opencc
import re

# Load data
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)
with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
    jlpt = json.load(f)
with open('web-app/static/game_data/joyo_kanji.json', 'r') as f:
    joyo = json.load(f)

jlpt_joyo = set(jlpt['N5'] + jlpt['N4'] + jlpt['N3'] + jlpt['N2'] + jlpt['N1'] + joyo)

# OpenCC converters (t2jp/jp2t not available)
t2s = opencc.OpenCC('t2s')  # Traditional to Simplified
s2t = opencc.OpenCC('s2t')  # Simplified to Traditional

# Build character -> keyword map
char_to_info = {}

def build_map(node, cat='', subcat=''):
    if 'char' in node:
        char_to_info[node['char']] = {
            'keyword': node.get('keyword', ''),
            'meaning': node.get('meaning', ''),
            'simp': node.get('simp'),
            'node': node  # Keep reference for updating
        }
    if 'children' in node:
        for child in node['children']:
            build_map(child)

build_map(graph)

print(f"Total characters in graph: {len(char_to_info)}")

# Build trad->simp mappings from the graph's simp field
trad_to_simp = {}
simp_to_trad = {}

for char, info in char_to_info.items():
    simp = info.get('simp')
    if simp and simp != char:
        trad_to_simp[char] = simp
        simp_to_trad[simp] = char

print(f"Found {len(trad_to_simp)} trad->simp mappings in graph")

# Detect Japanese shinjitai:
# - Is in JLPT/Joyo
# - Different from Chinese simplified
# - Not the traditional form
jp_shinjitai = set()
for char in jlpt_joyo:
    if char not in char_to_info:
        continue

    # Check if there's a traditional form that simplifies to something else
    trad = s2t.convert(char)
    simp = t2s.convert(char)

    # If char is in JLPT/Joyo and:
    # - char != trad (it's some kind of simplified)
    # - simp of trad != char (Chinese simplified is different)
    if trad != char:
        chinese_simp = t2s.convert(trad)
        if chinese_simp != char and chinese_simp != trad:
            # This is likely Japanese shinjitai
            jp_shinjitai.add(char)

print(f"Detected {len(jp_shinjitai)} potential Japanese shinjitai characters")

changes = []

def clean_suffix(kw):
    """Remove existing variant suffixes."""
    return re.sub(r'\s*\((jp|trad|simp|trad/jp|var)\)\s*$', '', kw).strip()

def get_suffix(char):
    """Determine what suffix a character should have."""
    trad = s2t.convert(char)
    simp = t2s.convert(char)

    # Check if it's Japanese shinjitai
    if char in jp_shinjitai:
        return '(jp)'

    # Check if it's simplified (different from traditional)
    if trad != char:
        return '(simp)'

    # Check if it's traditional (different from simplified)
    if simp != char:
        # Check if same as Japanese (char is trad, but also used in Japanese)
        if char in jlpt_joyo:
            return '(trad/jp)'
        return '(trad)'

    # No variant - standalone character
    return ''

# Process specific JLPT/Joyo characters we know need fixing
# These are characters where we explicitly want to normalize the gloss
specific_fixes = [
    # (char, base_gloss) - we'll add the appropriate suffix
    ('来', 'come'),
    ('読', 'read'),
    ('国', 'country'),
    ('毎', 'every'),
    ('売', 'sell'),
    ('賣', 'sell'),
]

print("\nApplying specific fixes...")
for char, base_gloss in specific_fixes:
    if char not in char_to_info:
        continue
    
    suffix = get_suffix(char)
    new_kw = f"{base_gloss} {suffix}".strip() if suffix else base_gloss
    
    old_kw = char_to_info[char]['keyword']
    if old_kw != new_kw:
        char_to_info[char]['node']['keyword'] = new_kw
        changes.append((char, old_kw, new_kw))
        print(f"  {char}: '{old_kw}' -> '{new_kw}'")

# Now fix any remaining "variant of X" patterns
print("\nFixing 'variant of' patterns...")
variant_pattern = re.compile(r'(?:old |Japanese )?variant of (\S+)', re.IGNORECASE)

for char, info in char_to_info.items():
    kw = info['keyword']
    match = variant_pattern.search(kw)
    if match:
        ref_char = match.group(1)
        # Clean up the reference (remove brackets, pinyin, etc.)
        ref_char = re.sub(r'[\[\(].*', '', ref_char).strip()
        ref_char = ref_char.split('|')[0] if '|' in ref_char else ref_char
        
        if len(ref_char) == 1 and ref_char in char_to_info:
            # Get the gloss of the referenced character
            ref_kw = char_to_info[ref_char]['keyword']
            base = clean_suffix(ref_kw)
            suffix = get_suffix(char) or '(var)'
            new_kw = f"{base} {suffix}".strip()
            
            if new_kw != kw:
                info['node']['keyword'] = new_kw
                changes.append((char, kw, new_kw))

print(f"\nTotal changes: {len(changes)}")
for char, old, new in changes[:30]:
    print(f"  {char}: '{old}' -> '{new}'")
if len(changes) > 30:
    print(f"  ... and {len(changes) - 30} more")

# Save
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("\nSaved hanzi_semantic_graph.json")

