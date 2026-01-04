#!/usr/bin/env python3
"""
Analyze HSK character glosses and semantic categorization.
Extracts unique single characters from HSK words and checks their categorization.
"""

import json
import sys

def load_data():
    with open('web-app/static/game_data/hsk_words.json', 'r') as f:
        hsk_data = json.load(f)
    with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
        semantic_graph = json.load(f)
    return hsk_data, semantic_graph

def build_char_info(semantic_graph):
    """Build character to info lookup from semantic graph."""
    char_info = {}

    def walk_tree(node, path=[]):
        if 'char' in node:
            char_info[node['char']] = {
                'keyword': node.get('keyword', '?'),
                'breadcrumb': ' > '.join(path)
            }
        if 'children' in node:
            for child in node['children']:
                child_path = path + [child['name']] if 'name' in child else path
                walk_tree(child, child_path)

    walk_tree(semantic_graph)
    return char_info

def extract_single_chars(hsk_words):
    """Extract unique single Chinese characters from HSK words."""
    chars = set()
    for word in hsk_words:
        for char in word:
            if '\u4e00' <= char <= '\u9fff':
                chars.add(char)
    return sorted(chars)

# Manual review categories - show chars in these categories for review
REVIEW_CATEGORIES = [
    'Society > Government',  # Often has misplaced chars
    'Human > Body',  # Animals/food sometimes end up here
    'Objects > Food',  # Check for non-food items
    'Abstract > Qualities',  # Check for actions/emotions
]

def analyze_by_category(char_info, filter_categories=None):
    """Group characters by their category for review."""
    by_category = {}
    for char, info in char_info.items():
        bc = info['breadcrumb']
        if bc not in by_category:
            by_category[bc] = []
        by_category[bc].append((char, info['keyword']))

    # Sort by category name
    for cat in sorted(by_category.keys()):
        if filter_categories and not any(f in cat for f in filter_categories):
            continue
        chars = by_category[cat]
        print(f"\n{'=' * 80}")
        print(f"{cat} ({len(chars)} characters)")
        print('=' * 80)
        for char, kw in sorted(chars, key=lambda x: x[1].lower()):
            print(f"  {char}\t{kw}")

def find_issues(char, info):
    """Check for problems with a character's gloss."""
    import re
    kw = info.get('keyword', '')
    path = info.get('breadcrumb', '')
    problems = []

    if not kw:
        problems.append('MISSING')
    elif 'variant of' in kw.lower():
        problems.append('VARIANT_OF')
    elif re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', kw):
        if '(trad' not in kw and '(jp' not in kw and '(simp' not in kw:
            problems.append('BAD_CAPS')
    elif len(kw) > 30:
        problems.append('TOO_LONG')

    if not path:
        problems.append('NOT_IN_GRAPH')

    return problems

def main():
    hsk_data, semantic_graph = load_data()
    char_info = build_char_info(semantic_graph)

    mode = sys.argv[1] if len(sys.argv) > 1 else '1'

    if mode == 'issues':
        # Find issues in a specific level
        level = sys.argv[2] if len(sys.argv) > 2 else '1'
        chars = extract_single_chars(hsk_data[level])
        issues = []
        for char in chars:
            info = char_info.get(char, {})
            probs = find_issues(char, info)
            if probs:
                issues.append((char, info.get('keyword', ''), probs))
        print(f"HSK {level}: {len(chars)} chars, {len(issues)} issues\n")
        for char, kw, probs in issues:
            print(f'{char}: "{kw}" - {probs}')
    elif mode == 'review':
        filter_cat = sys.argv[2] if len(sys.argv) > 2 else None
        if filter_cat:
            analyze_by_category(char_info, [filter_cat])
        else:
            analyze_by_category(char_info, REVIEW_CATEGORIES)
    elif mode == 'cat':
        cat_filter = sys.argv[2] if len(sys.argv) > 2 else 'Government'
        analyze_by_category(char_info, [cat_filter])
    else:
        level = mode
        if level not in hsk_data:
            print(f"Unknown level: {level}. Available: {list(hsk_data.keys())}")
            return
        chars = extract_single_chars(hsk_data[level])
        print(f"HSK {level} - {len(chars)} unique characters")
        print("=" * 80)
        for char in chars:
            info = char_info.get(char, {})
            print(f"{char}\t{info.get('keyword', '?')}\t{info.get('breadcrumb', 'Uncategorized')}")

if __name__ == '__main__':
    main()

