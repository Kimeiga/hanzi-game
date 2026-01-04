#!/usr/bin/env python3
"""Analyze JLPT/Joyo kanji semantic categorization."""

import json
import sys

# Load data
with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
    jlpt_data = json.load(f)
with open('web-app/static/game_data/kanji_details.json', 'r') as f:
    kanji_details = json.load(f)
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)
with open('web-app/static/game_data/char_glosses.json', 'r') as f:
    glosses = json.load(f)

# Build character to path/keyword lookup
char_info = {}
def walk_tree(node, path=[]):
    if 'char' in node:
        char_info[node['char']] = {
            'keyword': node.get('keyword', '?'),
            'path': ' > '.join(path)
        }
    if 'children' in node:
        for child in node['children']:
            child_path = path + [child['name']] if 'name' in child else path
            walk_tree(child, child_path)

walk_tree(graph)

def analyze_level(level):
    """Analyze kanji for a specific JLPT level."""
    kanji_list = jlpt_data.get(level, [])
    print(f"\n{'='*70}")
    print(f"JLPT {level}: {len(kanji_list)} kanji")
    print('='*70)
    
    # Group by category
    by_category = {}
    issues = []
    
    for kanji in kanji_list:
        info = char_info.get(kanji, {})
        path = info.get('path', 'Uncategorized')
        keyword = info.get('keyword', '?')
        details = kanji_details.get(kanji, {})
        jp_meaning = details.get('meaning', '')
        
        # Get top-level category
        parts = path.split(' > ')
        top_cat = parts[1] if len(parts) > 1 else 'Other'
        
        if top_cat not in by_category:
            by_category[top_cat] = []
        by_category[top_cat].append((kanji, keyword, path, jp_meaning))
        
        # Flag potential issues
        if keyword == '?':
            issues.append((kanji, 'NO KEYWORD', jp_meaning))
        elif path == 'Uncategorized':
            issues.append((kanji, 'UNCATEGORIZED', jp_meaning))
    
    # Show distribution
    print("\nCategory distribution:")
    for cat in sorted(by_category.keys(), key=lambda x: -len(by_category[x])):
        count = len(by_category[cat])
        print(f"  {cat}: {count} ({100*count/len(kanji_list):.1f}%)")
    
    # Show issues
    if issues:
        print(f"\nPotential issues ({len(issues)}):")
        for kanji, issue, meaning in issues[:20]:
            print(f"  {kanji} ({meaning}): {issue}")
    
    return by_category, issues

def show_category_samples(level, category):
    """Show sample kanji from a category."""
    kanji_list = jlpt_data.get(level, [])
    
    print(f"\n{level} kanji in '{category}':")
    count = 0
    for kanji in kanji_list:
        info = char_info.get(kanji, {})
        path = info.get('path', '')
        if category.lower() in path.lower():
            keyword = info.get('keyword', '?')
            details = kanji_details.get(kanji, {})
            jp_meaning = details.get('meaning', '')
            print(f"  {kanji}  {keyword:20s}  {jp_meaning:20s}  {path}")
            count += 1
            if count >= 50:
                print(f"  ... and more")
                break

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python analyze_jlpt_categorization.py <level>     - Analyze a JLPT level (N5, N4, etc)")
        print("  python analyze_jlpt_categorization.py all         - Analyze all levels")
        print("  python analyze_jlpt_categorization.py <level> <category> - Show samples")
        sys.exit(1)
    
    arg = sys.argv[1].upper()
    
    if arg == 'ALL':
        for level in ['N5', 'N4', 'N3', 'N2', 'N1']:
            analyze_level(level)
    elif len(sys.argv) >= 3:
        show_category_samples(arg, sys.argv[2])
    else:
        analyze_level(arg)

