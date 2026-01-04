#!/usr/bin/env python3
"""
Fix JLPT/Joyo kanji glosses:
1. Fix formatting issues (brackets, variant references, bad prefixes)
2. Use slash format for multi-meaning characters (most common first)
3. Fix meaning mismatches with unique glosses
4. Check uniqueness and swap if needed
"""
import json
from collections import defaultdict

# Load data
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)
with open('web-app/static/game_data/kanji_details.json', 'r') as f:
    details = json.load(f)

# Build keyword usage map
keyword_to_char = {}  # lowercase keyword -> char (for uniqueness check)

def build_keyword_map(node):
    if 'char' in node:
        kw = node.get('keyword', '').lower().strip()
        if kw and kw not in keyword_to_char:
            keyword_to_char[kw] = node['char']
    if 'children' in node:
        for child in node['children']:
            build_keyword_map(child)

build_keyword_map(graph)

# Track what we change
changes = []

def is_unique(keyword):
    """Check if keyword is unique (not used by another character)."""
    return keyword.lower().strip() not in keyword_to_char

def reserve_keyword(keyword, char):
    """Reserve a keyword for a character."""
    keyword_to_char[keyword.lower().strip()] = char

def find_and_update(node, char, new_keyword, new_meaning=None):
    """Find a character in the graph and update its keyword/meaning."""
    if 'char' in node and node['char'] == char:
        old_kw = node.get('keyword', '')
        node['keyword'] = new_keyword
        if new_meaning:
            node['meaning'] = new_meaning
        changes.append((char, old_kw, new_keyword))
        # Update keyword map
        if old_kw.lower() in keyword_to_char:
            del keyword_to_char[old_kw.lower()]
        reserve_keyword(new_keyword, char)
        return True
    if 'children' in node:
        for child in node['children']:
            if find_and_update(child, char, new_keyword, new_meaning):
                return True
    return False

# === FIXES ===

# 1. Formatting fixes (these have broken keywords)
formatting_fixes = {
    '着': ('arrive/wear', 'arrive; wear; attach'),
    '売': ('sell', 'sell'),
    '芸': ('art/skill', 'art; skill; craft'),
    '坂': ('slope', 'slope; hill'),
    '挙': ('raise/elect', 'raise; elect; enumerate'),
    '著': ('author/notable', 'author; notable; write'),
    '弾': ('bullet/play', 'bullet; play (instrument); spring'),
    '了': ('finish', 'finish; complete; understand'),
    '耐': ('endure', 'endure; withstand; bear'),
    '戯': ('play/frolic', 'play; frolic; drama'),
    '恒': ('constant', 'constant; permanent; always'),
    '奨': ('encourage', 'encourage; prize; recommend'),
}

# 2. Multi-meaning characters (use slash, most common Japanese meaning first)
multi_meaning_fixes = {
    '行': ('go/row', 'go; walk; row; line'),  # いく is most common in JP
    '気': ('spirit/air', 'spirit; energy; mood; air'),  # き means spirit in JP
    '書': ('write/book', 'write; book; document'),  # かく (write) is primary verb
    '生': ('life/birth', 'life; birth; raw; grow'),
    '分': ('divide/minute', 'divide; part; minute; understand'),
    '間': ('interval/room', 'interval; space; room; between'),
    '時': ('time/hour', 'time; hour; occasion'),
    '何': ('what', 'what; which; how many'),  # Clean up the weird keyword
    '会': ('meet/society', 'meet; gather; society; association'),
    '発': ('emit/depart', 'emit; departure; start'),
}

# 3. Meaning alignment fixes (JP meaning should be primary)
meaning_fixes = {
    '本': ('book/origin', 'book; origin; main; counter for long things'),
    '出': ('exit/go out', 'exit; go out; leave; put out'),
    '前': ('front/before', 'front; before; previous'),
    '後': ('after/behind', 'after; behind; later'),
    '学': ('learn/study', 'learn; study; science'),
    '高': ('high/tall', 'high; tall; expensive'),
    '先': ('ahead/before', 'ahead; before; previous; tip'),
    '川': ('river', 'river; stream'),  # Just use river
    '聞': ('hear/listen', 'hear; listen; ask'),
    '語': ('language/word', 'language; word; talk; tell'),
    '天': ('heaven/sky', 'heaven; sky'),
    '万': ('ten thousand', 'ten thousand; myriad'),
    '土': ('earth/soil', 'earth; soil; ground'),
    '校': ('school', 'school; proofreading'),  # Primary JP meaning
    '自': ('self', 'self; oneself'),
    '者': ('person/-er', 'person; someone; -er (suffix)'),
    '事': ('thing/matter', 'thing; matter; affair; fact'),
    '思': ('think', 'think; consider'),
    '的': ('target/-tic', 'target; -tic; -like (suffix)'),
    '方': ('direction/way', 'direction; way; person; method'),
    '地': ('ground/earth', 'ground; earth; place'),
    '場': ('place/場', 'place; site; occasion'),
    '代': ('replace/age', 'replace; age; era; generation'),
    '立': ('stand', 'stand; establish'),
    '物': ('thing/object', 'thing; object; matter'),
    '体': ('body/form', 'body; form; style'),
    '動': ('move', 'move; motion'),
    '社': ('company/shrine', 'company; shrine; society'),
    '知': ('know', 'know; wisdom'),
    '理': ('reason/logic', 'reason; logic; arrange'),
    '同': ('same', 'same; together'),
    '心': ('heart/mind', 'heart; mind; spirit'),
    '作': ('make/do', 'make; do; create; work'),
    '新': ('new', 'new'),
    '世': ('world/generation', 'world; generation; era'),
    '度': ('degree/time', 'degree; time; occasion'),
    '明': ('bright/clear', 'bright; clear; light'),
    '力': ('power/force', 'power; force; strength'),
    '意': ('meaning/idea', 'meaning; idea; intention'),
    '用': ('use', 'use; utilize; business'),
    '主': ('main/master', 'main; master; lord; chief'),
    '通': ('pass/communicate', 'pass; commute; communicate'),
    '文': ('writing/sentence', 'writing; sentence; literature'),
}

print("Applying fixes...")

# Apply all fixes
all_fixes = {}
all_fixes.update(formatting_fixes)
all_fixes.update(multi_meaning_fixes)
all_fixes.update(meaning_fixes)

for char, (new_kw, new_meaning) in all_fixes.items():
    # Check uniqueness
    if not is_unique(new_kw):
        existing_char = keyword_to_char.get(new_kw.lower())
        if existing_char != char:
            print(f"  WARNING: '{new_kw}' already used by {existing_char}, skipping {char}")
            continue
    find_and_update(graph, char, new_kw, new_meaning)

# Fix kanji_details for 校
if '校' in details:
    old = details['校']['meaning']
    details['校']['meaning'] = 'school'
    details['校']['description'] = '校 is a Japanese kanji that means school. 校 has 10 strokes.'
    print(f"Fixed kanji_details 校: '{old}' -> 'school'")

print(f"\nApplied {len(changes)} keyword changes:")
for char, old, new in changes[:30]:
    print(f"  {char}: '{old}' -> '{new}'")
if len(changes) > 30:
    print(f"  ... and {len(changes) - 30} more")

# Save
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("\nSaved hanzi_semantic_graph.json")

with open('web-app/static/game_data/kanji_details.json', 'w') as f:
    json.dump(details, f, ensure_ascii=False, indent=2)
print("Saved kanji_details.json")

