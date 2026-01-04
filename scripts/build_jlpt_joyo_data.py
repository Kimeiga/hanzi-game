#!/usr/bin/env python3
"""
Build JLPT and Joyo Kanji data files from external sources.

JLPT levels:
- N5: 80 kanji (beginner)
- N4: 170 kanji
- N3: 370 kanji
- N2: 380 kanji
- N1: 1135 kanji (advanced)
Total: 2136 (complete Joyo kanji list)

The Joyo kanji (常用漢字) are the 2136 characters designated by the 
Japanese Ministry of Education as essential for everyday use.
"""

import json
import urllib.request
from pathlib import Path

# Constants
JLPT_SOURCE_URL = "https://raw.githubusercontent.com/AnchorI/jlpt-kanji-dictionary/main/jlpt-kanji.json"
OUTPUT_DIR = Path(__file__).parent.parent / "web-app" / "static" / "game_data"

def download_jlpt_data():
    """Download JLPT kanji data from GitHub."""
    print("Downloading JLPT kanji data...")
    with urllib.request.urlopen(JLPT_SOURCE_URL) as response:
        data = json.loads(response.read().decode('utf-8'))
    print(f"  Downloaded {len(data)} kanji entries")
    return data

def build_jlpt_lists(data):
    """Build JLPT level lists similar to HSK format."""
    jlpt_lists = {
        'N5': [],
        'N4': [],
        'N3': [],
        'N2': [],
        'N1': []
    }
    
    joyo_list = []  # All Joyo kanji
    
    for entry in data:
        kanji = entry['kanji']
        level = entry.get('jlpt')
        
        # Add to Joyo list (all kanji in this dataset are Joyo)
        joyo_list.append(kanji)
        
        # Add to JLPT level
        if level and level in jlpt_lists:
            jlpt_lists[level].append(kanji)
    
    # Print stats
    print("\nJLPT distribution:")
    for level in ['N5', 'N4', 'N3', 'N2', 'N1']:
        print(f"  {level}: {len(jlpt_lists[level])} kanji")
    print(f"\nTotal Joyo kanji: {len(joyo_list)}")
    
    return jlpt_lists, joyo_list

def build_kanji_details(data):
    """Build detailed kanji info for display."""
    details = {}
    
    for entry in data:
        kanji = entry['kanji']
        
        # Extract meaning from description
        desc = entry.get('description', '')
        meaning = ''
        if 'means' in desc:
            # Extract meaning between "means" and "."
            parts = desc.split('means ')
            if len(parts) > 1:
                meaning = parts[1].split('.')[0].strip()
        
        details[kanji] = {
            'kanji': kanji,
            'strokes': entry.get('strokes'),
            'jlpt': entry.get('jlpt'),
            'frequency': entry.get('frequency'),
            'meaning': meaning,
            'description': desc
        }
    
    return details

def main():
    # Download data
    data = download_jlpt_data()
    
    # Build lists
    jlpt_lists, joyo_list = build_jlpt_lists(data)
    kanji_details = build_kanji_details(data)
    
    # Save JLPT words file (similar to hsk_words.json)
    jlpt_file = OUTPUT_DIR / "jlpt_kanji.json"
    with open(jlpt_file, 'w', encoding='utf-8') as f:
        json.dump(jlpt_lists, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {jlpt_file}")
    
    # Save Joyo list
    joyo_file = OUTPUT_DIR / "joyo_kanji.json"
    with open(joyo_file, 'w', encoding='utf-8') as f:
        json.dump(joyo_list, f, ensure_ascii=False, indent=2)
    print(f"Saved: {joyo_file}")
    
    # Save detailed kanji info
    details_file = OUTPUT_DIR / "kanji_details.json"
    with open(details_file, 'w', encoding='utf-8') as f:
        json.dump(kanji_details, f, ensure_ascii=False, indent=2)
    print(f"Saved: {details_file}")
    
    print("\nDone!")

if __name__ == '__main__':
    main()

