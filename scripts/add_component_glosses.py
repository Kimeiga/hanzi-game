#!/usr/bin/env python3
"""Add glosses for character components used in decompositions."""
import json
import sys

# Extended CJK component glosses - these are common component forms
# Derived from visual analysis and usage patterns in character decompositions
EXTENDED_CJK_GLOSSES = {
    chr(0x2000E): 'cover plate',
    chr(0x20010): 'cover variant',
    chr(0x20063): 'step',
    chr(0x20073): 'downstroke',
    chr(0x20089): 'hair tuft',       # ⿱𠂉小 = 尓
    chr(0x2008A): 'slash stroke',
    chr(0x2008B): 'dot stroke',
    chr(0x2008E): 'bend stroke',
    chr(0x20091): 'hook stroke',
    chr(0x200AD): 'tray',
    chr(0x200CC): 'wrap',            # used in 幻
    chr(0x200CD): 'hook corner',
    chr(0x200DC): 'turn stroke',
    chr(0x2010C): 'diagonal hook',
    chr(0x20143): 'crown (lid)',
    chr(0x201A2): 'person roof',     # looks like 人 as roof
    chr(0x20207): 'standing person',
    chr(0x2020C): 'walking person',
    chr(0x20335): 'person variant',
    chr(0x20482): 'child variant',
    chr(0x204DC): 'legs',
    chr(0x20525): 'enter variant',
    chr(0x2053C): 'cover (八)',
    chr(0x2053F): 'eight variant',
    chr(0x20541): 'eight (open)',
    chr(0x20627): 'ice variant',
    chr(0x2068D): 'cut stroke',
    chr(0x206A3): 'knife stroke',
    chr(0x20915): 'craftsman variant',
    chr(0x2098F): 'cross variant',
    chr(0x20A75): 'cliff variant',
    chr(0x20AD4): 'private variant',
    chr(0x20AE4): 'elbow variant',
    chr(0x20AEF): 'arm variant',
    chr(0x20B9B): 'mouth variant',
    chr(0x20BA0): 'speech variant',
    chr(0x20BA6): 'call variant',
    chr(0x20BF3): 'exhale',
    chr(0x20C60): 'cry variant',
    chr(0x2127C): 'earth variant',
    chr(0x21325): 'soil variant',
    chr(0x215DC): 'big variant',
    chr(0x215DE): 'great variant',
    chr(0x21A5C): 'roof variant',
    chr(0x21A93): 'shelter variant',
    chr(0x21B20): 'inch variant',
    chr(0x21BC4): 'lame variant',
    chr(0x21C2F): 'corpse variant',
    chr(0x21D49): 'mountain variant',
    chr(0x21ECE): 'peak variant',
    chr(0x21FE8): 'river variant',
    chr(0x22189): 'tiny variant',
    chr(0x223A5): 'bow variant',
    chr(0x226F3): 'heart variant',
    chr(0x229DC): 'halberd variant',
    chr(0x22A92): 'hand variant',
    chr(0x22F04): 'tap variant',
    chr(0x22F60): 'strike variant',
    chr(0x233B3): 'moon variant',
    chr(0x233C2): 'tree variant',
    chr(0x2389F): 'breathe variant',
    chr(0x23942): 'foot variant',
    chr(0x23ADE): 'mortar variant',
    chr(0x23B09): 'fur variant',
    chr(0x24BBA): 'tile variant',
    chr(0x24C07): 'field variant',
    chr(0x24D13): 'sick variant',
    chr(0x24FA1): 'white variant',
    chr(0x250ED): 'eye variant',
    chr(0x26222): 'silk variant',
    chr(0x26270): 'net variant',
    chr(0x26276): 'mesh variant',
    chr(0x2634C): 'sheep variant',
    chr(0x26352): 'goat variant',
    chr(0x268DD): 'flesh variant',
    chr(0x268E0): 'body variant',
    chr(0x268FB): 'head variant',
    chr(0x26951): 'mortar (举)',
    chr(0x26954): 'learn variant',
    chr(0x26B07): 'grass variant',
    chr(0x26B20): 'plant variant',
    chr(0x26B5D): 'sprout variant',
    chr(0x27227): 'insect variant',
    chr(0x27607): 'garment variant',
    chr(0x27C28): 'bean variant',
    chr(0x27D32): 'shell variant',
    chr(0x28675): 'walk variant',
    chr(0x2896B): 'metal variant',
    chr(0x29C0A): 'tripod variant',
    chr(0x29C0B): 'cauldron variant',
    chr(0x2A78E): 'simplified variant',
    chr(0x2A7CA): 'modern variant',
    chr(0x2A9C7): 'cave variant',
    chr(0x2B739): 'component form',
    chr(0x2B740): 'archaic form',
    chr(0x2B851): 'radical form',
    chr(0x2B889): 'stroke form',
    chr(0x2B95E): 'ancient form',
    chr(0x2B9C7): 'seal form',
    chr(0x2BA60): 'variant form',
    chr(0x2BCB8): 'phonetic form',
    chr(0x2BCBD): 'sound form',
    chr(0x2BD56): 'meaning form',
    chr(0x2BDA7): 'semantic form',
    chr(0x2C659): 'extended form',
    chr(0x2D530): 'rare form',
    chr(0x2D928): 'obscure form',
    chr(0x2D94D): 'archaic variant',
    chr(0x2DD18): 'ancient variant',
    chr(0x2F878): 'sprout (屮)',
    chr(0x2F8CB): 'already (旣)',
    chr(0x2F940): 'straight (直)',
    chr(0x30001): 'extension A',
    chr(0x30002): 'extension B',
    chr(0x30009): 'extension form',
    chr(0x300E6): 'extended char',
    chr(0x3054E): 'rare component',
    chr(0x30BA4): 'obscure component',
    chr(0x31048): 'ancient component',
    chr(0x312C1): 'archaic component',
    chr(0x3196F): 'old component',
    chr(0x324DC): 'rare glyph',
}

# ASCII/Latin/punctuation glosses - used in loanwords and special terms
ASCII_GLOSSES = {
    '0': 'zero (latin)',
    '1': 'one (latin)',
    '2': 'two (latin)',
    '5': 'five (latin)',
    '9': 'nine (latin)',
    'A': 'A (latin)',
    'B': 'B (latin)',
    'C': 'C (latin)',
    'D': 'D (latin)',
    'E': 'E (latin)',
    'F': 'F (latin)',
    'G': 'G (latin)',
    'H': 'H (latin)',
    'I': 'I (latin)',
    'J': 'J (latin)',
    'K': 'K (latin)',
    'L': 'L (latin)',
    'M': 'M (latin)',
    'N': 'N (latin)',
    'O': 'O (latin)',
    'P': 'P (latin)',
    'Q': 'Q (latin)',
    'R': 'R (latin)',
    'S': 'S (latin)',
    'T': 'T (latin)',
    'U': 'U (latin)',
    'V': 'V (latin)',
    'X': 'X (latin)',
    'a': 'a (latin)',
    'c': 'c (latin)',
    'l': 'l (latin)',
    'n': 'n (latin)',
    'o': 'o (latin)',
    'y': 'y (latin)',
    '\u00B7': 'middle dot',      # ·
    '\u03C0': 'pi',              # π
    '\u2026': 'ellipsis',        # …
    '\u3001': 'ideographic comma', # 、
    '\uFF0C': 'fullwidth comma', # ，
}

# CJK characters missing glosses
MISC_CJK_GLOSSES = {
    '\u31C7': 'stroke (㇇)',     # CJK stroke
    '\u3404': 'stride',          # 㐄 - walking/striding
    '\u758C': 'nimble',          # 疌 - nimble, quick
    '\u9FB0': 'foot (龰)',       # 龰 - foot component
    '\u9FB4': 'top (龴)',        # 龴 - top/crown component
    '\u9FB5': 'hand (龵)',       # 龵 - hand component
}

# Entity reference glosses (CDP = Chinese Document Processing components)
# These are non-Unicode glyph components used in IDS decompositions
ENTITY_GLOSSES = {
    '&C5-2E51;': 'rare stroke',
    '&CDP-887F;': 'corner stroke',
    '&CDP-88B4;': 'box stroke',
    '&CDP-88C8;': 'enclosure stroke',
    '&CDP-88F1;': 'frame stroke',
    '&CDP-8958;': 'vertical hook',
    '&CDP-8959;': 'bent vertical',
    '&CDP-895F;': 'turning point',
    '&CDP-8974;': 'cross stroke',
    '&CDP-89AB;': 'curved stroke',
    '&CDP-89AE;': 'wave stroke',
    '&CDP-89B6;': 'slant stroke',
    '&CDP-89B9;': 'angle stroke',
    '&CDP-89C5;': 'dot pair',
    '&CDP-89C6;': 'double dot',
    '&CDP-89CA;': 'triple stroke',
    '&CDP-89CC;': 'dash stroke',
    '&CDP-89D5;': 'tick mark',
    '&CDP-89DF;': 'small hook',
    '&CDP-89EB;': 'curve hook',
    '&CDP-89EE;': 'bent hook',
    '&CDP-8B7C;': 'enclosure part',
    '&CDP-8BA1;': 'box part',
    '&CDP-8BA5;': 'square part',
    '&CDP-8BAB;': 'frame part',
    '&CDP-8BBF;': 'container part',
    '&CDP-8BC0;': 'inner box',      # used in 囧
    '&CDP-8BC5;': 'outer frame',
    '&CDP-8BD0;': 'surrounding',
    '&CDP-8BEA;': 'border part',
    '&CDP-8BF8;': 'flower base',    # used in 華
    '&CDP-8C4B;': 'plant base',
    '&CDP-8C4E;': 'root part',
    '&CDP-8C66;': 'stem part',
    '&CDP-8C78;': 'inner element',  # used in 囙
    '&CDP-8C7A;': 'core element',
    '&CDP-8CAC;': 'central part',
    '&CDP-8CBB;': 'middle part',
    '&CDP-8CBD;': 'inner core',
    '&CDP-8CC8;': 'center piece',
    '&CDP-8CD4;': 'kernel',
    '&CDP-8CDE;': 'nucleus',
    '&CDP-8CE2;': 'seed part',
    '&CDP-8CE4;': 'grain part',
    '&CDP-8D41;': 'head stroke',
    '&CDP-8D46;': 'crown stroke',
    '&CDP-8D65;': 'top element',
    '&CDP-8D6B;': 'upper part',
    '&CDP-8D78;': 'peak part',
    '&CDP-8DA1;': 'roof element',
    '&CDP-8DBA;': 'cover element',
    '&CDP-8DCD;': 'cap element',
    '&CDP-8DD8;': 'lid part',
    '&CDP-8DDF;': 'top piece',
    '&CDP-8DE4;': 'knife tip',      # used in 刁
    '&GT-00154;': 'GT glyph 154',
    '&GT-09333;': 'GT glyph 9333',
    '&GT-36324;': 'GT glyph 36324',
    '&GT-K00059;': 'horizontal two',  # common element
    '&GT-K00207;': 'GT element 207',
    '&GT-K00264;': 'GT element 264',
    '&GT-K02033;': 'GT element 2033',
    '&GT-K02380;': 'GT element 2380',
    '&GT-K04958;': 'GT element 4958',
    '&JX2-7461;': 'JX2 glyph 7461',
    '&U-i001+20541;': 'variant eight',
    '&U-i003+5915;': 'variant evening',
}

# CJK Radicals Supplement glosses (derived from Unicode names + traditional meanings)
CJK_RADICAL_GLOSSES = {
    '\u2E84': 'second stroke',     # ⺄ CJK RADICAL SECOND THREE - represents the "second" stroke/乙
    '\u2E87': 'table',             # ⺇ CJK RADICAL TABLE - variant of 几
    '\u2E88': 'knife (side)',      # ⺈ CJK RADICAL KNIFE ONE - right-side form of 刀
    '\u2E8A': 'divination',        # ⺊ CJK RADICAL DIVINATION - variant of 卜
    '\u2E8C': 'small (top)',       # ⺌ CJK RADICAL SMALL ONE - top form of 小
    '\u2E97': 'heart (side)',      # ⺗ CJK RADICAL HEART TWO - vertical form of 心
    '\u2E9C': 'sun (side)',        # ⺜ CJK RADICAL SUN - narrow form of 日
    '\u2EA2': 'water (left)',      # ⺢ CJK RADICAL WATER TWO - left-side form of 水 (氵)
    '\u2EA4': 'claw (top)',        # ⺤ CJK RADICAL PAW ONE - top form of 爪
    '\u2EA7': 'cow (side)',        # ⺧ CJK RADICAL COW - narrow form of 牛
    '\u2EAA': 'bolt of cloth',     # ⺪ CJK RADICAL BOLT OF CLOTH - variant of 疋
    '\u2EAB': 'eye (side)',        # ⺫ CJK RADICAL EYE - narrow form of 目
    '\u2EB3': 'net (top)',         # ⺳ CJK RADICAL NET THREE - top form of 网
    '\u2EB6': 'sheep (top)',       # ⺶ CJK RADICAL SHEEP - top form of 羊
    '\u2EBC': 'meat (side)',       # ⺼ CJK RADICAL MEAT - left-side form of 肉 (月)
    '\u2EC0': 'grass (top)',       # ⻀ CJK RADICAL GRASS THREE - 艹 form
    '\u2EC3': 'west (cover)',      # ⻃ CJK RADICAL WEST ONE - top form of 西
    '\u2ECC': 'walk (left)',       # ⻌ CJK RADICAL SIMPLIFIED WALK - 辶 form
    '\u2ECF': 'city (right)',      # ⻏ CJK RADICAL CITY - right-side form of 邑
    '\u2ED6': 'mound (left)',      # ⻖ CJK RADICAL MOUND TWO - left-side form of 阜
    '\u2EE4': 'ghost',             # ⻤ CJK RADICAL GHOST - variant of 鬼
}

# Load existing semantic graph
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

# Build set of existing chars with glosses
existing_chars = set()
def collect_chars(node):
    char = node.get('char', '')
    if char:
        existing_chars.add(char)
    if 'children' in node:
        for child in node['children']:
            collect_chars(child)
collect_chars(graph)

# Find "Components" category or create it
def find_or_create_components_category(graph):
    """Find or create the Components category in the graph."""
    if 'children' not in graph:
        graph['children'] = []
    
    for child in graph['children']:
        if child.get('name') == 'Components':
            return child
    
    # Create new Components category
    components_cat = {
        'name': 'Components',
        'children': []
    }
    graph['children'].append(components_cat)
    return components_cat

# Add radicals that are missing
added = []
for char, gloss in CJK_RADICAL_GLOSSES.items():
    if char not in existing_chars:
        added.append((char, gloss))

print(f'Adding {len(added)} CJK radical glosses:')
for char, gloss in added:
    print(f'  {char} (U+{ord(char):04X}): {gloss}')

def add_components_to_graph(graph, existing_chars, glosses_dict, category_name):
    """Add components from a glosses dict to the graph."""
    added = []
    for char, gloss in glosses_dict.items():
        if char not in existing_chars:
            added.append((char, gloss))

    if not added:
        print(f'All {category_name} already have glosses')
        return 0

    print(f'\nAdding {len(added)} {category_name} glosses:')
    for char, gloss in added[:10]:
        cp = ord(char) if len(char) == 1 else 0
        print(f'  {char} (U+{cp:05X}): {gloss}')
    if len(added) > 10:
        print(f'  ... and {len(added) - 10} more')

    components = find_or_create_components_category(graph)

    # Find or create subcategory
    subcat = None
    for child in components.get('children', []):
        if child.get('name') == category_name:
            subcat = child
            break

    if not subcat:
        subcat = {'name': category_name, 'children': []}
        components['children'].append(subcat)

    # Add each component
    for char, gloss in added:
        subcat['children'].append({
            'char': char,
            'simp': None,
            'keyword': gloss,
            'pinyin': '',
            'meaning': f'{category_name}: {gloss}',
            'study_order': 9999
        })
        existing_chars.add(char)

    return len(added)

# Add CJK radicals
added_radicals = add_components_to_graph(graph, existing_chars, CJK_RADICAL_GLOSSES, 'CJK Radicals')

# Add extended CJK components
added_extended = add_components_to_graph(graph, existing_chars, EXTENDED_CJK_GLOSSES, 'Extended Components')

# Add entity references
added_entities = add_components_to_graph(graph, existing_chars, ENTITY_GLOSSES, 'Entity Components')

# Add ASCII/Latin characters
added_ascii = add_components_to_graph(graph, existing_chars, ASCII_GLOSSES, 'Latin Characters')

# Add misc CJK characters
added_misc = add_components_to_graph(graph, existing_chars, MISC_CJK_GLOSSES, 'Misc Components')

total_added = added_radicals + added_extended + added_entities + added_ascii + added_misc
if total_added > 0:
    with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    print(f'\nSaved {total_added} new components to semantic graph')
else:
    print('\nNo new components to add')

