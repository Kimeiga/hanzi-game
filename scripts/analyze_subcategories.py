#!/usr/bin/env python3
"""Analyze potential subcategories using WordNet hypernyms."""

import json
import re
from collections import Counter
from nltk.corpus import wordnet as wn

# Load the current tree
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, '..', 'web-app', 'static', 'game_data', 'hanzi_semantic_graph.json')
with open(json_path, 'r') as f:
    tree = json.load(f)

# Find all characters and their categories
def collect_chars(node, path=''):
    chars = []
    if 'name' in node:
        new_path = f"{path} > {node['name']}" if path else node['name']
        for child in node.get('children', []):
            if 'char' in child:
                chars.append((child['char'], child.get('keyword', ''), new_path))
            else:
                chars.extend(collect_chars(child, new_path))
    return chars

all_chars = collect_chars(tree)
print(f"Total characters: {len(all_chars)}")

# Filter for large categories and analyze WordNet hypernyms
large_categories = ['Animals', 'Actions', 'Tools', 'Relations', 'Qualities', 'Elements']

for cat in large_categories:
    cat_chars = [(c, kw) for c, kw, path in all_chars if cat in path]
    print(f"\n{'='*60}")
    print(f"{cat}: {len(cat_chars)} characters")
    print('='*60)
    
    # Get hypernym statistics
    hypernym_counter = Counter()
    
    for char, keyword in cat_chars[:500]:  # Sample first 500
        if not keyword:
            continue
        clean_kw = re.sub(r'[^a-zA-Z\s]', '', keyword).strip().split()
        if not clean_kw:
            continue
        word = clean_kw[0].lower()
        
        synsets = wn.synsets(word)
        if synsets:
            synset = synsets[0]
            paths = synset.hypernym_paths()
            if paths and len(paths[0]) > 3:
                # Get 2-3 levels up for subcategory
                for level in [-3, -4]:
                    if len(paths[0]) > abs(level):
                        hypernym = paths[0][level].name().split('.')[0]
                        hypernym_counter[hypernym] += 1
    
    print("Top potential subcategories:")
    for hyp, count in hypernym_counter.most_common(15):
        if count >= 5:
            print(f"  {hyp}: {count}")

