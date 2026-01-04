#!/usr/bin/env python3
"""
Fix the remaining keyword conflicts by either:
1. Using a unique variant for the JLPT/Joyo kanji
2. Swapping keywords if the JLPT kanji should have priority
"""
import json

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

# Track changes
changes = []

def find_and_update(node, char, new_keyword, new_meaning=None):
    """Find a character and update its keyword."""
    if 'char' in node and node['char'] == char:
        old_kw = node.get('keyword', '')
        node['keyword'] = new_keyword
        if new_meaning:
            node['meaning'] = new_meaning
        changes.append((char, old_kw, new_keyword))
        return True
    if 'children' in node:
        for child in node['children']:
            if find_and_update(child, char, new_keyword, new_meaning):
                return True
    return False

# Conflicts to resolve:
# Format: JLPT kanji -> (new keyword, meaning), conflicting char -> (new keyword for it)
# The JLPT/Joyo kanji gets priority since it's more commonly studied

resolutions = [
    # 売 conflicts with 賣 (traditional of 卖 sell)
    # 売 is Japanese shinjitai, 賣 is traditional - give 売 "sell" and 賣 "sell (trad)"
    ('売', 'sell', 'sell'),
    ('賣', 'sell (trad)', 'sell; to sell'),
    
    # 坂 conflicts with 坡 (slope)
    # 坂 is Japanese for slope/hill, 坡 is Chinese for slope - different chars
    ('坂', 'hillside', 'slope; hill; hillside'),
    
    # 了 conflicts with 完 (finish/complete)
    # 了 is completion particle, 完 is "complete" - different nuances
    ('了', 'complete', 'finish; complete; particle'),
    ('完', 'finish', 'finish; complete; end'),
    
    # 耐 conflicts with 忍 (endure)
    # 耐 is "withstand/resist", 忍 is "endure/bear" - slightly different
    ('耐', 'withstand', 'withstand; endure; resist'),
    
    # 恒 conflicts with 㔰 (constant)
    # 恒 is common, 㔰 is rare - give 恒 "constant"
    ('恒', 'permanent', 'permanent; constant; always'),
    
    # 奨 conflicts with 勵 (encourage)  
    # 奨 is "recommend/prize", 勵 is "encourage/urge"
    ('奨', 'recommend', 'recommend; encourage; prize'),
    
    # 何 conflicts with 倽 (what)
    # 何 is very common, 倽 is rare - give 何 the clean keyword
    ('何', 'what/how', 'what; how; which'),
    ('倽', 'what (rare)', 'what'),
    
    # 川 conflicts with 河 (river)
    # 川 is "stream/river", 河 is "river" (often large rivers) - different nuance
    ('川', 'stream', 'stream; river'),
    
    # 万 conflicts with 萬 (ten thousand)
    # 万 is shinjitai, 萬 is traditional
    ('万', 'myriad', 'ten thousand; myriad'),
    ('萬', 'ten thousand', 'ten thousand'),
    
    # 自 conflicts with 己 (self)
    # Both mean self but 自 is "oneself/from", 己 is "self/ego"
    ('自', 'oneself', 'oneself; self; from'),
    
    # 思 conflicts with 想 (think)
    # 思 is "think/consider", 想 is "think/want/miss"
    ('思', 'think', 'think; consider'),
    ('想', 'think of', 'think of; want; miss'),
    
    # 用 conflicts with 使 (use)
    # 用 is "use/employ", 使 is "use/cause/envoy"
    ('用', 'utilize', 'use; utilize; employ'),
]

print("Resolving keyword conflicts...")
for item in resolutions:
    char, new_kw, meaning = item
    find_and_update(graph, char, new_kw, meaning)

print(f"\nApplied {len(changes)} changes:")
for char, old, new in changes:
    print(f"  {char}: '{old}' -> '{new}'")

# Save
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("\nSaved hanzi_semantic_graph.json")

