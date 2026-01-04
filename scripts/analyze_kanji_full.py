#!/usr/bin/env python3
import json

with open('web-app/static/game_data/kanji_details.json', 'r') as f:
    kanji_details = json.load(f)
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    semantic_graph = json.load(f)
with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
    jlpt_kanji = json.load(f)
with open('web-app/static/game_data/joyo_kanji.json', 'r') as f:
    joyo_kanji = json.load(f)

# Build semantic map
semantic_map = {}
def build_semantic_map(node, category='', subcategory=''):
    if 'char' in node:
        semantic_map[node['char']] = {
            'category': category, 
            'subcategory': subcategory, 
            'keyword': node.get('keyword', ''), 
            'meaning': node.get('meaning', '')
        }
        if node.get('simp'):
            semantic_map[node['simp']] = semantic_map[node['char']]
    if 'children' in node:
        for child in node['children']:
            if 'char' in child:
                build_semantic_map(child, category, subcategory or node.get('name', ''))
            else:
                new_cat = category if node.get('name') == 'Hanzi Universe' else node.get('name', '')
                build_semantic_map(child, new_cat, subcategory)

build_semantic_map(semantic_graph)

all_jlpt = jlpt_kanji['N5'] + jlpt_kanji['N4'] + jlpt_kanji['N3'] + jlpt_kanji['N2'] + jlpt_kanji['N1']

# Check missing
missing_semantic = [k for k in all_jlpt if k not in semantic_map]
missing_details = [k for k in all_jlpt if k not in kanji_details]

print('=== JLPT COVERAGE ===')
print(f'Total JLPT kanji: {len(all_jlpt)}')
print(f'Missing from semantic: {len(missing_semantic)}')
print(f'Missing from details: {len(missing_details)}')
if missing_semantic:
    print(f'Missing semantic: {missing_semantic}')
if missing_details:
    print(f'Missing details: {missing_details}')

# Joyo coverage
joyo_missing_semantic = [k for k in joyo_kanji if k not in semantic_map]
joyo_missing_details = [k for k in joyo_kanji if k not in kanji_details]

print('\n=== JOYO COVERAGE ===')
print(f'Total Joyo: {len(joyo_kanji)}')
print(f'Missing from semantic: {len(joyo_missing_semantic)}')
print(f'Missing from details: {len(joyo_missing_details)}')
if joyo_missing_semantic:
    print(f'Missing semantic: {joyo_missing_semantic}')
if joyo_missing_details:
    print(f'Missing details: {joyo_missing_details}')

# Print N5 analysis
print('\n=== N5 KANJI GLOSSES AND CATEGORIES ===')
for k in jlpt_kanji['N5']:
    detail = kanji_details.get(k, {})
    semantic = semantic_map.get(k, {})
    jp_meaning = detail.get('meaning', '?')
    kw = semantic.get('keyword', '?')
    cat = semantic.get('category', '?')
    subcat = semantic.get('subcategory', '?')
    print(f'{k}: JP="{jp_meaning}" | KW="{kw}" | Cat={cat}>{subcat}')

# Print N4 analysis  
print('\n=== N4 KANJI GLOSSES AND CATEGORIES ===')
for k in jlpt_kanji['N4']:
    detail = kanji_details.get(k, {})
    semantic = semantic_map.get(k, {})
    jp_meaning = detail.get('meaning', '?')
    kw = semantic.get('keyword', '?')
    cat = semantic.get('category', '?')
    subcat = semantic.get('subcategory', '?')
    print(f'{k}: JP="{jp_meaning}" | KW="{kw}" | Cat={cat}>{subcat}')

