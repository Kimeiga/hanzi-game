#!/usr/bin/env python3
"""Find and report issues with kanji glosses and semantic categories."""
import json

with open('web-app/static/game_data/kanji_details.json', 'r') as f:
    kanji_details = json.load(f)
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    semantic_graph = json.load(f)
with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
    jlpt_kanji = json.load(f)

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

# Issue categories
gloss_mismatches = []  # JP meaning doesn't match keyword well
category_issues = []   # Category seems wrong for the meaning
keyword_issues = []    # Keyword has formatting issues

for level in ['N5', 'N4', 'N3', 'N2', 'N1']:
    for k in jlpt_kanji[level]:
        detail = kanji_details.get(k, {})
        semantic = semantic_map.get(k, {})
        jp = detail.get('meaning', '')
        kw = semantic.get('keyword', '')
        cat = semantic.get('category', '')
        subcat = semantic.get('subcategory', '')
        
        # Check for keyword formatting issues (brackets, weird chars)
        if '[' in kw or ']' in kw or kw.startswith('(') or len(kw) > 30:
            keyword_issues.append((k, level, jp, kw, f'{cat}>{subcat}'))
        
        # Check for obvious category mismatches
        # Body parts should be in Body category
        body_words = ['hand', 'foot', 'eye', 'ear', 'mouth', 'head', 'face', 'leg', 'arm', 
                      'heart', 'stomach', 'finger', 'tooth', 'tongue', 'nose', 'bone', 'skin']
        if any(b in jp.lower() for b in body_words) and cat not in ['Body', 'Human']:
            category_issues.append((k, level, jp, kw, f'{cat}>{subcat}', 'Should be Body'))
        
        # Actions should have verb-like meanings
        action_cat = cat == 'Actions' or subcat == 'Actions'
        action_jp = any(w in jp.lower() for w in ['walk', 'run', 'eat', 'drink', 'write', 'read',
                        'speak', 'go', 'come', 'make', 'do', 'move', 'build', 'cut', 'send'])
        
        # Numbers should be in Abstract>Numbers
        if jp.lower() in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 
                          'ten', 'hundred', 'thousand'] and subcat != 'Numbers':
            category_issues.append((k, level, jp, kw, f'{cat}>{subcat}', 'Should be Numbers'))
        
        # Family should be in Relations>Family
        family = ['father', 'mother', 'brother', 'sister', 'child', 'parent', 'son', 'daughter']
        if any(f in jp.lower() for f in family) and subcat != 'Family':
            category_issues.append((k, level, jp, kw, f'{cat}>{subcat}', 'Should be Family'))
        
        # Animals
        animals = ['dog', 'cat', 'horse', 'cow', 'bird', 'fish', 'sheep', 'pig', 'chicken']
        if any(a in jp.lower() for a in animals) and cat != 'Animals':
            category_issues.append((k, level, jp, kw, f'{cat}>{subcat}', 'Should be Animals'))

print(f'=== KEYWORD FORMATTING ISSUES ({len(keyword_issues)}) ===')
for k, level, jp, kw, path in keyword_issues[:30]:
    print(f'{k} ({level}): JP="{jp}" | KW="{kw}" | {path}')

print(f'\n=== CATEGORY ISSUES ({len(category_issues)}) ===')
for k, level, jp, kw, path, issue in category_issues[:30]:
    print(f'{k} ({level}): JP="{jp}" | KW="{kw}" | {path} - {issue}')

# Sample of N5/N4 that need review
print('\n=== N5 KANJI NEEDING REVIEW ===')
review_n5 = []
for k in jlpt_kanji['N5']:
    detail = kanji_details.get(k, {})
    semantic = semantic_map.get(k, {})
    jp = detail.get('meaning', '')
    kw = semantic.get('keyword', '')
    cat = semantic.get('category', '')
    subcat = semantic.get('subcategory', '')
    
    # Flag items where JP meaning and keyword are quite different
    jp_simple = jp.lower().split(';')[0].split(',')[0].strip()
    kw_simple = kw.lower().split()[0] if kw else ''
    
    if jp_simple != kw_simple and jp_simple not in kw.lower() and kw_simple not in jp.lower():
        review_n5.append((k, jp, kw, f'{cat}>{subcat}'))

for k, jp, kw, path in review_n5:
    print(f'{k}: JP="{jp}" vs KW="{kw}" | {path}')

