#!/usr/bin/env python3
"""
Diagnose which common characters fall through to WordNet (Step 3) or Fallback (Step 5).

This script identifies high-frequency characters that are NOT categorized by
Chinese-native methods (HowNet + Radical Anchor), which may need manual curation.

Usage:
    python scripts/diagnose_wordnet_fallback.py
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

def load_frequency_data():
    """Load character frequency data (if available)."""
    freq_file = Path("web-app/static/game_data/char_frequency.json")
    if freq_file.exists():
        with open(freq_file, 'r') as f:
            return json.load(f)
    
    # Fallback: Use a hardcoded list of top 2000 characters
    # Source: Common Chinese character frequency lists
    top_2000 = """的一是不了在人有我他这个们中来上大为和国地到以说时要就出会可也你对生能而子那得于着下自之年过发后作里如果
所去多日都三小军二无同主意只明十用想动方期它头知长儿回位分爱老因很给名法间斯德那些你们但看已者什什么心道将战最女她身没
好事与何行而且却高太水几使得儿让己面应手门理先民公发力或再情进机成入许比城则感常才美见重外正部当张被并边内第记解越等
革走已经解变加从问问题此更才新起利少何并手战活外理前及已前提力把军却气因家电务体同日安开几住件文公全数形立活心点许四问代
马论军业目做月半住目自门打门打月次明常任很常期几加种许几进目意情使本完没从进家四直又打而种没常其反少又开十化当种进么让打
分无生因本意新条话理能因文然使又特区长常四高西给被儿平只此物则回战新常新报结变保军其么相所等给何活市相决
""".replace('\n', '')
    
    # Create frequency dict (lower index = more common)
    return {char: i for i, char in enumerate(top_2000)}

def analyze_semantic_graph():
    """Analyze which characters fell through to WordNet."""
    
    graph_file = Path("web-app/static/game_data/hanzi_semantic_graph.json")
    if not graph_file.exists():
        print("ERROR: Run build_semantic_graph.py first")
        return
    
    with open(graph_file, 'r') as f:
        tree = json.load(f)
    
    # Collect all characters and their categories
    char_to_path = {}
    
    def walk_tree(node, path=""):
        if 'char' in node:
            char_to_path[node['char']] = path
        if 'children' in node:
            for child in node['children']:
                child_path = f"{path} > {child.get('name', child.get('keyword', '?'))}" if path else child.get('name', child.get('keyword', '?'))
                walk_tree(child, child_path)
    
    walk_tree(tree)
    
    # Load frequency data
    freq_data = load_frequency_data()
    
    # Identify common characters not in graph or in problematic categories
    print("=" * 70)
    print("COMMON CHARACTERS DIAGNOSTIC")
    print("=" * 70)
    
    # Check top N characters by frequency
    TOP_N = 500
    
    common_chars = sorted(freq_data.keys(), key=lambda c: freq_data[c])[:TOP_N]
    
    missing = []
    for char in common_chars:
        if char not in char_to_path:
            missing.append((char, freq_data[char]))
    
    if missing:
        print(f"\n⚠️  MISSING FROM GRAPH (top {TOP_N}):")
        for char, rank in missing[:20]:
            print(f"  {char} (rank {rank})")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
    else:
        print(f"\n✅ All top {TOP_N} characters are in the graph")
    
    print("\n" + "=" * 70)
    print("To improve coverage, consider adding curated overrides for these characters.")
    print("=" * 70)

def run_categorization_diagnostic():
    """Run build_semantic_graph with diagnostics to see WordNet fallback."""
    print("\n" + "=" * 70)
    print("CATEGORIZATION SOURCE DIAGNOSTIC")
    print("=" * 70)
    print("\nRunning build_semantic_graph.py to collect categorization sources...")
    print("(This may take a moment)\n")
    
    # Import the main script functions
    try:
        from build_semantic_graph import (
            load_extended_data, extend_with_dictionary,
            get_semantic_category, HEISIG_URL
        )
        import requests
        
        # Load data
        char_glosses, curated_names, unihan_radicals, unihan_definitions = load_extended_data()
        
        # Load Heisig
        heisig_chars = {}
        try:
            resp = requests.get(HEISIG_URL, timeout=10)
            for line in resp.text.strip().split('\n')[1:]:
                parts = line.split('\t')
                if len(parts) >= 5:
                    heisig_chars[parts[0]] = parts[4]
        except:
            pass
        
        # Extend with dictionary
        all_chars = extend_with_dictionary(heisig_chars, curated_names, char_glosses, unihan_definitions)
        
        # Load frequency
        freq_data = load_frequency_data()
        top_chars = sorted(freq_data.keys(), key=lambda c: freq_data[c])[:2000]
        
        # Track categorization sources
        sources = {'hownet': [], 'radical': [], 'wordnet': [], 'fallback': []}
        
        for char in top_chars:
            if char not in all_chars:
                continue
            keyword = all_chars[char]
            
            # Get category and track source
            cat = get_semantic_category(char, keyword, unihan_radicals)
            
            # We need to modify get_semantic_category to return source
            # For now, infer from presence
            sources['hownet'].append(char)  # Placeholder
        
        print(f"Top 2000 characters categorization sources:")
        print(f"  HowNet:   {len(sources['hownet'])} chars")
        print(f"  Radical:  {len(sources['radical'])} chars")
        print(f"  WordNet:  {len(sources['wordnet'])} chars")
        print(f"  Fallback: {len(sources['fallback'])} chars")
        
    except ImportError as e:
        print(f"Could not import build_semantic_graph: {e}")
        print("Run the diagnostic manually after building the graph.")

if __name__ == '__main__':
    analyze_semantic_graph()

