#!/usr/bin/env python3
"""
Comprehensive analysis of JLPT/Joyo kanji issues.
Focus on:
1. Keyword uniqueness - each character should have unique keyword
2. Keyword quality - no formatting issues, appropriate length
3. Japanese meaning alignment - keyword should match Japanese usage
4. Missing entries
"""
import json
from collections import defaultdict

# Load data
with open('web-app/static/game_data/kanji_details.json', 'r') as f:
    kanji_details = json.load(f)
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    semantic_graph = json.load(f)
with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
    jlpt_kanji = json.load(f)
with open('web-app/static/game_data/joyo_kanji.json', 'r') as f:
    joyo_kanji = json.load(f)

# Build maps
semantic_map = {}  # char -> {keyword, meaning, category, pinyin}
keyword_to_chars = defaultdict(list)  # keyword -> [chars] for finding duplicates

def build_semantic_map(node, category='', subcategory=''):
    if 'char' in node:
        char = node['char']
        kw = node.get('keyword', '')
        semantic_map[char] = {
            'keyword': kw,
            'meaning': node.get('meaning', ''),
            'category': category,
            'subcategory': subcategory,
            'pinyin': node.get('pinyin', '')
        }
        if kw:
            keyword_to_chars[kw.lower()].append(char)
        if node.get('simp'):
            semantic_map[node['simp']] = semantic_map[char]
    if 'children' in node:
        for child in node['children']:
            if 'char' in child:
                build_semantic_map(child, category, subcategory or node.get('name', ''))
            else:
                new_cat = category if node.get('name') == 'Hanzi Universe' else node.get('name', '')
                build_semantic_map(child, new_cat, subcategory)

build_semantic_map(semantic_graph)

all_jlpt = jlpt_kanji['N5'] + jlpt_kanji['N4'] + jlpt_kanji['N3'] + jlpt_kanji['N2'] + jlpt_kanji['N1']

print("=" * 80)
print("JLPT/JOYO KANJI ANALYSIS REPORT")
print("=" * 80)

# 1. Coverage
print("\n1. COVERAGE")
print("-" * 40)
missing_jlpt = [k for k in all_jlpt if k not in semantic_map]
missing_joyo = [k for k in joyo_kanji if k not in semantic_map]
missing_details = [k for k in joyo_kanji if k not in kanji_details]
print(f"JLPT total: {len(all_jlpt)}, missing from graph: {len(missing_jlpt)}")
print(f"Joyo total: {len(joyo_kanji)}, missing from graph: {len(missing_joyo)}")
print(f"Joyo missing from kanji_details: {len(missing_details)}")
if missing_jlpt:
    print(f"Missing JLPT: {missing_jlpt}")
if missing_joyo:
    print(f"Missing Joyo: {missing_joyo}")

# 2. Keyword formatting issues
print("\n2. KEYWORD FORMATTING ISSUES")
print("-" * 40)
format_issues = []
for k in joyo_kanji:
    if k not in semantic_map:
        continue
    kw = semantic_map[k]['keyword']
    issues = []
    if '[' in kw or ']' in kw:
        issues.append('brackets')
    if 'variant of' in kw.lower():
        issues.append('variant reference')
    if len(kw) > 30:
        issues.append('too long')
    if kw.startswith('(') or kw.startswith('-'):
        issues.append('bad prefix')
    if issues:
        format_issues.append((k, kw, issues))

print(f"Found {len(format_issues)} kanji with keyword formatting issues:")
for k, kw, issues in format_issues:
    print(f"  {k}: '{kw}' - {', '.join(issues)}")

# 3. Major meaning mismatches (JP vs keyword)
print("\n3. SIGNIFICANT MEANING MISMATCHES (N5/N4 only)")
print("-" * 40)
print("These may need manual review - keyword doesn't match primary Japanese meaning:")
mismatches = []
for level in ['N5', 'N4']:
    for k in jlpt_kanji[level]:
        if k not in semantic_map or k not in kanji_details:
            continue
        jp = kanji_details[k].get('meaning', '').lower()
        kw = semantic_map[k]['keyword'].lower()
        # Normalize for comparison
        jp_words = set(jp.replace(';', ' ').replace(',', ' ').split())
        kw_words = set(kw.split())
        # Check if there's ANY overlap
        if not jp_words.intersection(kw_words):
            # No overlap - might be an issue
            mismatches.append((k, level, kanji_details[k]['meaning'], semantic_map[k]['keyword']))

for k, level, jp, kw in mismatches[:25]:
    print(f"  {k} ({level}): JP='{jp}' vs KW='{kw}'")
print(f"  ... {len(mismatches)} total potential mismatches")

# 4. Duplicate keywords (violates uniqueness)
print("\n4. DUPLICATE KEYWORDS (among JLPT/Joyo kanji)")
print("-" * 40)
jlpt_joyo_set = set(all_jlpt) | set(joyo_kanji)
dup_count = 0
for kw, chars in sorted(keyword_to_chars.items()):
    # Filter to only JLPT/Joyo chars
    relevant = [c for c in chars if c in jlpt_joyo_set]
    if len(relevant) > 1:
        dup_count += 1
        if dup_count <= 20:
            print(f"  '{kw}': {relevant}")
print(f"  ... {dup_count} total duplicate keywords")

# 5. Kanji_details meaning issues
print("\n5. KANJI_DETAILS POTENTIAL ERRORS")
print("-" * 40)
detail_issues = []
for k in all_jlpt[:250]:  # Check first 250 most common
    if k not in kanji_details:
        continue
    jp = kanji_details[k].get('meaning', '')
    # Check for clearly wrong meanings
    if k == '校' and 'school' not in jp.lower():
        detail_issues.append((k, jp, 'should be "school"'))
    if k == '駅' and 'station' not in jp.lower():
        detail_issues.append((k, jp, 'should be "station"'))
    # Add more checks as needed

if detail_issues:
    for k, jp, issue in detail_issues:
        print(f"  {k}: '{jp}' - {issue}")
else:
    print("  No obvious errors found in checked kanji")

print("\n" + "=" * 80)
print("END OF REPORT")

