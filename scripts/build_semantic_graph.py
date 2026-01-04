#!/usr/bin/env python3
"""
Build Semantic Graph for Chinese Characters

This script combines:
1. Heisig data (from agj/3000-traditional-hanzi) for unique English glosses
2. char_glosses.json for characters not in Heisig
3. curated_component_names_v2.json for conflict resolution
4. OpenHowNet for semantic structure (sememe trees)

Output: hanzi_semantic_graph.json - hierarchical tree for visualization
"""

import json
import urllib.request
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Constants
HEISIG_DATA_URL = "https://raw.githubusercontent.com/agj/3000-traditional-hanzi/master/output/notes.tsv"
OUTPUT_DIR = Path(__file__).parent.parent / "web-app" / "static" / "game_data"
OUTPUT_FILE = OUTPUT_DIR / "hanzi_semantic_graph.json"
CHAR_GLOSSES_FILE = OUTPUT_DIR / "char_glosses.json"
CURATED_NAMES_FILE = OUTPUT_DIR / "curated_component_names_v2.json"
UNIHAN_DATA_FILE = OUTPUT_DIR / "unihan_data.json"

# Import radical mapping
from radical_mapping import KANGXI_RADICAL_TO_CATEGORY


def fetch_heisig_data() -> list[dict]:
    """
    Fetch and parse Heisig data from agj/3000-traditional-hanzi repository.

    The notes.tsv format (tab-separated):
    0: Traditional
    1: Study order
    2: Variants
    3: Simplified
    4: Pinyin
    5: Heisig keyword
    6: Meaning
    7: Vocabulary hanzi
    8: Vocabulary pinyin
    ...more fields
    """
    print("Fetching Heisig data from GitHub...")

    with urllib.request.urlopen(HEISIG_DATA_URL) as response:
        content = response.read().decode('utf-8')

    entries = []
    lines = content.strip().split('\n')

    for line in lines:
        if not line.strip():
            continue

        # Parse tab-separated format
        parts = line.split('\t')
        if len(parts) < 7:
            continue

        traditional = parts[0].strip() if len(parts) > 0 else None

        # Skip header or invalid lines
        if not traditional or traditional == 'Traditional' or len(traditional) != 1:
            continue

        entry = {
            'traditional_char': traditional,
            'study_order': int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None,
            'variants': parts[2].strip() if len(parts) > 2 else None,
            'simplified_char': parts[3].strip() if len(parts) > 3 and parts[3].strip() else None,
            'pinyin': parts[4].strip() if len(parts) > 4 else None,
            'heisig_keyword': parts[5].strip() if len(parts) > 5 else None,
            'meaning': parts[6].strip() if len(parts) > 6 else None,
        }

        if entry['traditional_char'] and entry['heisig_keyword']:
            entries.append(entry)

    print(f"  Parsed {len(entries)} Heisig entries")
    return entries


def load_extended_data() -> tuple[dict, dict, dict, dict]:
    """
    Load additional data sources:
    - char_glosses.json: dictionary definitions for 23k+ characters
    - curated_component_names_v2.json: hand-curated unique glosses
    - unihan_data.json: Unihan radicals and definitions

    Returns (char_glosses, curated_names, unihan_radicals, unihan_definitions)
    """
    char_glosses = {}
    curated_names = {}
    unihan_radicals = {}
    unihan_definitions = {}

    if CHAR_GLOSSES_FILE.exists():
        with open(CHAR_GLOSSES_FILE, 'r', encoding='utf-8') as f:
            char_glosses = json.load(f)
        print(f"  Loaded {len(char_glosses)} character glosses")

    if CURATED_NAMES_FILE.exists():
        with open(CURATED_NAMES_FILE, 'r', encoding='utf-8') as f:
            curated_names = json.load(f)
            # Remove metadata keys
            curated_names = {k: v for k, v in curated_names.items() if not k.startswith('_')}
        print(f"  Loaded {len(curated_names)} curated names")

    if UNIHAN_DATA_FILE.exists():
        with open(UNIHAN_DATA_FILE, 'r', encoding='utf-8') as f:
            unihan_data = json.load(f)
            unihan_radicals = unihan_data.get('radicals', {})
            unihan_definitions = unihan_data.get('definitions', {})
        print(f"  Loaded {len(unihan_radicals)} Unihan radicals, {len(unihan_definitions)} definitions")

    return char_glosses, curated_names, unihan_radicals, unihan_definitions


def extract_semantic_qualifier(unihan_def: str, base_keyword: str) -> str | None:
    """
    Extract a semantic qualifier from Unihan definition to distinguish duplicates.

    Examples:
    - "piece of jade with hole in it" + "jade" -> "jade disk"
    - "two pieces of jade joined together" + "jade" -> "jade pair"
    - "beautiful jade; star" + "jade" -> "star jade" or "beautiful jade"

    NOTE: Unihan definitions are often formatted as "primary meaning; secondary meaning"
    We ONLY analyze the first segment to avoid overly long keywords.
    """
    if not unihan_def:
        return None

    # Only use first segment before semicolon or comma (avoid definition dumps)
    # "semicircular jade; half-circle jade pendant" → "semicircular jade"
    first_segment = unihan_def.split(';')[0].split(',')[0].strip()
    defn_lower = first_segment.lower()
    base_lower = base_keyword.lower()

    # Common patterns to extract qualifiers
    qualifiers = []

    # Pattern: "X jade" or "jade X" where X is a distinguishing word
    distinguishing_words = [
        'disk', 'tablet', 'ring', 'pendant', 'ornament', 'seal', 'scepter',
        'beautiful', 'precious', 'flawless', 'fine', 'rough', 'uncut', 'polished',
        'white', 'green', 'black', 'red', 'yellow', 'blue',
        'round', 'flat', 'long', 'small', 'large', 'ancient',
        'ritual', 'ceremonial', 'imperial', 'royal',
        'pair', 'two', 'half', 'broken', 'cracked',
        'star', 'moon', 'sun', 'mountain', 'water', 'cloud',
    ]

    for word in distinguishing_words:
        if word in defn_lower and word not in base_lower:
            # Found a distinguishing word
            qualifiers.append(word)

    # Also try to extract descriptor patterns
    # "piece of X with hole" -> "X disk/ring"
    if 'hole' in defn_lower and ('piece' in defn_lower or 'disk' in defn_lower or 'ring' in defn_lower):
        if 'disk' not in qualifiers and 'ring' not in qualifiers:
            qualifiers.append('disk')

    # "two pieces" -> "pair"
    if 'two' in defn_lower and 'piece' in defn_lower:
        qualifiers.append('pair')

    if qualifiers:
        # Use the first qualifier to create a new keyword
        qualifier = qualifiers[0]
        result = f"{qualifier} {base_keyword}"
        # Enforce word count limit (max 4 words)
        if len(result.split()) <= 4:
            return result
        # Too long, fall back to None
        return None

    return None


# Maximum words allowed in a generated keyword (to avoid "A kind of jade that was used in ancient rituals")
MAX_KEYWORD_WORDS = 4


def make_unique_keyword(base: str, used_keywords: set, char: str,
                        unihan_definitions: dict = None) -> str:
    """
    Generate a unique keyword by adding semantic qualifiers.
    Keywords are limited to MAX_KEYWORD_WORDS words to avoid overly long descriptions.
    Uses Unihan definitions for meaningful differentiation when possible.
    """
    if base.lower() not in used_keywords:
        return base

    # First, try to use Unihan definition for semantic differentiation
    if unihan_definitions and char in unihan_definitions:
        unihan_def = unihan_definitions[char]
        semantic_keyword = extract_semantic_qualifier(unihan_def, base)
        if semantic_keyword and semantic_keyword.lower() not in used_keywords:
            return semantic_keyword.title()

        # Try using first distinct word from Unihan definition as prefix
        words = unihan_def.split()
        for word in words[:5]:
            word = word.strip('.,;:()').lower()
            if len(word) >= 3 and word != base.lower() and word not in ['the', 'and', 'for', 'with', 'kind', 'type', 'sort']:
                candidate = f"{word} {base}"
                # Enforce word count limit
                if len(candidate.split()) <= MAX_KEYWORD_WORDS and candidate.lower() not in used_keywords:
                    return candidate.title()

    # Fallback: Try adding character code as suffix (less desirable)
    code_point = ord(char)
    suffixes = [
        f" (ii)",
        f" (iii)",
        f" (alt)",
        f" ({hex(code_point)[2:]})",  # hex code as last resort
    ]

    for suffix in suffixes:
        candidate = f"{base}{suffix}"
        if candidate.lower() not in used_keywords:
            return candidate

    # Last resort: use hex code
    return f"{base} (U+{code_point:04X})"


def clean_definition(defn: str) -> str:
    """Clean a dictionary definition into a usable keyword."""
    clean = defn.strip()

    # Remove leading underscore markers
    if clean.startswith('_'):
        clean = clean[1:].strip()
    if clean.startswith('(') and ')' in clean:
        # Handle things like "(variant of X)"
        paren_content = clean[1:clean.index(')')]
        after_paren = clean[clean.index(')')+1:].strip()
        if after_paren:
            clean = after_paren
        elif 'variant' not in paren_content.lower():
            clean = paren_content

    # Take first phrase before comma/semicolon
    clean = clean.split(',')[0].split(';')[0].strip()

    # Remove trailing parentheticals
    if '(' in clean:
        clean = clean[:clean.index('(')].strip()

    # Limit length
    if len(clean) > 25:
        words = clean.split()
        clean = ' '.join(words[:3])

    return clean


def extend_with_dictionary(heisig_entries: list[dict], char_glosses: dict,
                           curated_names: dict, unihan_definitions: dict = None) -> list[dict]:
    """
    Extend Heisig entries with ALL characters from the dictionary.
    Uses curated_names first, then generates unique keywords for conflicts.
    Uses Unihan definitions for semantic deduplication.

    Returns:
        Extended list of entries with unique keywords for all characters
    """
    unihan_definitions = unihan_definitions or {}

    # Build mapping: char -> keyword, and track used keywords
    char_to_keyword: dict[str, str] = {}
    used_keywords: set[str] = set()

    # Step 1: Add all Heisig entries (HIGHEST priority - never override)
    heisig_chars = set()
    for entry in heisig_entries:
        char = entry['traditional_char']
        keyword = entry['heisig_keyword']
        char_to_keyword[char] = keyword
        used_keywords.add(keyword.lower())
        heisig_chars.add(char)

    print(f"  Step 1: {len(char_to_keyword)} Heisig characters (protected)")

    # Step 2: Apply curated names ONLY for non-Heisig characters
    curated_applied = 0
    for char, keyword in curated_names.items():
        # NEVER override Heisig characters
        if char in heisig_chars:
            continue

        if char in char_to_keyword:
            # Already have this char from somewhere else, skip
            continue

        # New character from curated
        if keyword.lower() in used_keywords:
            keyword = make_unique_keyword(keyword, used_keywords, char, unihan_definitions)
        char_to_keyword[char] = keyword
        used_keywords.add(keyword.lower())
        curated_applied += 1

    print(f"  Step 2: Applied {curated_applied} curated names (new chars only)")

    # Step 3: Add ALL remaining characters from dictionary
    dict_added = 0
    dict_skipped = 0

    for char, definitions in char_glosses.items():
        # Skip if already have this character
        if char in char_to_keyword:
            continue

        # Skip multi-character entries
        if len(char) != 1:
            continue

        # Skip if no definitions
        if not definitions:
            dict_skipped += 1
            continue

        # Try each definition until we find a usable keyword
        keyword = None
        for defn in definitions:
            clean = clean_definition(defn)
            if clean and len(clean) >= 2:
                keyword = clean
                break

        if not keyword:
            # Use first definition as-is, truncated
            keyword = definitions[0][:20].strip()

        if not keyword:
            dict_skipped += 1
            continue

        # Make unique if needed (use Unihan for semantic deduplication)
        if keyword.lower() in used_keywords:
            keyword = make_unique_keyword(keyword, used_keywords, char, unihan_definitions)

        char_to_keyword[char] = keyword
        used_keywords.add(keyword.lower())
        dict_added += 1

    print(f"  Step 3: Added {dict_added} from dictionary, skipped {dict_skipped}")

    # Step 4: Build extended entries list
    extended = []

    # First add original Heisig entries (preserve their ORIGINAL keywords - never change)
    for entry in heisig_entries:
        char = entry['traditional_char']
        entry_copy = dict(entry)
        # Keep original Heisig keyword, NOT the char_to_keyword version
        entry_copy['source'] = 'heisig'
        extended.append(entry_copy)

    # Then add new entries
    study_order = len(heisig_entries) + 1
    for char, keyword in char_to_keyword.items():
        if char in heisig_chars:
            continue

        # Get meaning from dictionary
        meaning = ''
        if char in char_glosses and char_glosses[char]:
            meaning = char_glosses[char][0]

        extended.append({
            'traditional_char': char,
            'study_order': study_order,
            'variants': None,
            'simplified_char': None,
            'pinyin': None,
            'heisig_keyword': keyword,
            'meaning': meaning,
            'source': 'curated' if char in curated_names else 'dictionary'
        })
        study_order += 1

    print(f"  Total: {len(extended)} characters with unique keywords")

    return extended


# HowNet sememe to category mapping
SEMEME_TO_CATEGORY = {
    # Nature > Animals
    'animal|动物': ('Nature', 'Animals'),
    'AnimalHuman|动物': ('Nature', 'Animals'),
    'bird|禽': ('Nature', 'Animals'),
    'fish|鱼': ('Nature', 'Animals'),
    'beast|走兽': ('Nature', 'Animals'),
    'insect|虫': ('Nature', 'Animals'),
    'livestock|牲畜': ('Nature', 'Animals'),
    'reptile|爬虫': ('Nature', 'Animals'),
    'mammal|兽': ('Nature', 'Animals'),

    # Nature > Plants
    'plant|植物': ('Nature', 'Plants'),
    'tree|树': ('Nature', 'Plants'),
    'wood|木': ('Nature', 'Plants'),  # wood/tree
    'flower|花': ('Nature', 'Plants'),
    'FlowerGrass|花草': ('Nature', 'Plants'),  # flowers and grasses
    'fruit|水果': ('Nature', 'Plants'),
    'vegetable|蔬菜': ('Nature', 'Plants'),
    'grass|草': ('Nature', 'Plants'),
    'grain|谷': ('Nature', 'Plants'),
    'crop|庄稼': ('Nature', 'Plants'),
    'AlgaeFungi|低植': ('Nature', 'Plants'),  # algae, fungi, etc.

    # Nature > Elements
    'water|水': ('Nature', 'Elements'),
    'fire|火': ('Nature', 'Elements'),
    'earth|土': ('Nature', 'Elements'),
    'metal|金属': ('Nature', 'Elements'),
    'stone|石': ('Nature', 'Elements'),
    'mineral|矿': ('Nature', 'Elements'),
    'LandShape|地形': ('Nature', 'Elements'),
    'land|陆地': ('Nature', 'Elements'),
    'celestial|天体': ('Nature', 'Elements'),
    'sun|日': ('Nature', 'Elements'),
    'moon|月': ('Nature', 'Elements'),
    'star|星': ('Nature', 'Elements'),

    # Nature > Weather
    'weather|天气': ('Nature', 'Weather'),
    'atmosphere|大气': ('Nature', 'Weather'),
    'rain|雨': ('Nature', 'Weather'),
    'wind|风': ('Nature', 'Weather'),
    'cloud|云': ('Nature', 'Weather'),
    'snow|雪': ('Nature', 'Weather'),

    # Human > Body
    'part|部件': ('Human', 'Body'),  # body part
    'body|身': ('Human', 'Body'),
    'head|头': ('Human', 'Body'),
    'heart|心': ('Human', 'Body'),
    'hand|手': ('Human', 'Body'),
    'foot|脚': ('Human', 'Body'),
    'eye|眼': ('Human', 'Body'),
    'mouth|嘴': ('Human', 'Body'),
    'ear|耳': ('Human', 'Body'),
    'bone|骨': ('Human', 'Body'),
    'viscera|脏': ('Human', 'Body'),
    'blood|血': ('Human', 'Body'),
    'flesh|肉': ('Human', 'Body'),
    'skin|皮': ('Human', 'Body'),
    'hair|发': ('Human', 'Body'),
    'physiology|生理学': ('Human', 'Body'),

    # Human > Actions
    'act|行动': ('Human', 'Actions'),
    'walk|走': ('Human', 'Actions'),
    'run|跑': ('Human', 'Actions'),
    'jump|跳': ('Human', 'Actions'),
    'eat|吃': ('Human', 'Actions'),
    'drink|喝': ('Human', 'Actions'),
    'speak|说': ('Human', 'Actions'),
    'look|看': ('Human', 'Actions'),
    'listen|听': ('Human', 'Actions'),
    'think|想': ('Human', 'Actions'),
    'know|知': ('Human', 'Actions'),
    'learn|学': ('Human', 'Actions'),
    'teach|教': ('Human', 'Actions'),
    'write|写': ('Human', 'Actions'),
    'read|读': ('Human', 'Actions'),
    'make|制造': ('Human', 'Actions'),
    'do|做': ('Human', 'Actions'),
    'use|使用': ('Human', 'Actions'),
    'give|给': ('Human', 'Actions'),
    'take|取': ('Human', 'Actions'),
    'put|放': ('Human', 'Actions'),
    'hold|握': ('Human', 'Actions'),
    'hit|打': ('Human', 'Actions'),
    'cut|切': ('Human', 'Actions'),
    'open|开': ('Human', 'Actions'),
    'close|关': ('Human', 'Actions'),
    'come|来': ('Human', 'Actions'),
    'go|去': ('Human', 'Actions'),
    'enter|入': ('Human', 'Actions'),
    'leave|离': ('Human', 'Actions'),
    'move|移动': ('Human', 'Actions'),
    'stop|停': ('Human', 'Actions'),
    'start|始': ('Human', 'Actions'),
    'end|终': ('Human', 'Actions'),
    'change|变': ('Human', 'Actions'),
    'grow|长': ('Human', 'Actions'),
    'decrease|减': ('Human', 'Actions'),
    'increase|增': ('Human', 'Actions'),

    # Human > Relations
    'human|人': ('Human', 'Relations'),
    'family|家庭': ('Human', 'Relations'),
    'relative|亲属': ('Human', 'Relations'),
    'friend|友': ('Human', 'Relations'),
    'male|男': ('Human', 'Relations'),
    'female|女': ('Human', 'Relations'),
    'senior|长辈': ('Human', 'Relations'),
    'junior|小辈': ('Human', 'Relations'),
    'child|少儿': ('Human', 'Relations'),
    'collateral|旁系': ('Human', 'Relations'),
    'forefathers|祖先': ('Human', 'Relations'),
    'offspring|后代': ('Human', 'Relations'),

    # Human > Emotions
    'mental|精神': ('Human', 'Emotions'),
    'emotion|情感': ('Human', 'Emotions'),
    'happy|乐': ('Human', 'Emotions'),
    'sad|悲': ('Human', 'Emotions'),
    'angry|怒': ('Human', 'Emotions'),
    'afraid|怕': ('Human', 'Emotions'),
    'love|爱': ('Human', 'Emotions'),
    'hate|恨': ('Human', 'Emotions'),
    'desire|欲': ('Human', 'Emotions'),
    'willing|愿意': ('Human', 'Emotions'),
    'attitude|态度': ('Human', 'Emotions'),

    # Society > Government
    'politics|政': ('Society', 'Government'),
    'country|国家': ('Society', 'Government'),
    'government|政府': ('Society', 'Government'),
    'official|官': ('Society', 'Government'),
    'law|律': ('Society', 'Government'),
    'military|军': ('Society', 'Government'),
    'army|兵': ('Society', 'Government'),
    'power|权': ('Society', 'Government'),
    'rule|治': ('Society', 'Government'),
    'affairs|事务': ('Society', 'Government'),  # official affairs, matters
    'duty|责任': ('Society', 'Government'),
    'fact|事情': ('Society', 'Government'),  # matters, affairs
    'Occupation|职位': ('Society', 'Government'),  # positions, roles

    # Society > Economy
    'commerce|商业': ('Society', 'Economy'),
    'finance|金融': ('Society', 'Economy'),
    'money|钱': ('Society', 'Economy'),
    'wealth|钱财': ('Society', 'Economy'),
    'trade|贸易': ('Society', 'Economy'),
    'buy|买': ('Society', 'Economy'),
    'sell|卖': ('Society', 'Economy'),
    'price|价': ('Society', 'Economy'),
    'occupation|职业': ('Society', 'Economy'),

    # Society > Religion
    'religion|宗教': ('Society', 'Religion'),
    'god|神': ('Society', 'Religion'),
    'spirit|灵': ('Society', 'Religion'),
    'soul|魂': ('Society', 'Religion'),
    'worship|拜': ('Society', 'Religion'),
    'ceremony|仪式': ('Society', 'Religion'),
    'sacrifice|祭': ('Society', 'Religion'),
    'blessing|福': ('Society', 'Religion'),
    'fate|命': ('Society', 'Religion'),
    'divine|圣': ('Society', 'Religion'),

    # Objects > Tools
    'tool|用具': ('Objects', 'Tools'),
    'weapon|武器': ('Objects', 'Tools'),
    'instrument|乐器': ('Objects', 'Tools'),
    'knife|刀': ('Objects', 'Tools'),
    'vehicle|车': ('Objects', 'Tools'),
    'ship|船': ('Objects', 'Tools'),
    'machine|机': ('Objects', 'Tools'),
    'equipment|设备': ('Objects', 'Tools'),

    # Objects > Buildings
    'building|建筑': ('Objects', 'Buildings'),
    'facilities|设施': ('Objects', 'Buildings'),
    'house|房': ('Objects', 'Buildings'),
    'room|屋': ('Objects', 'Buildings'),
    'InstitutePlace|场所': ('Objects', 'Buildings'),

    # Objects > Containers
    'container|容器': ('Objects', 'Containers'),
    'furniture|家具': ('Objects', 'Containers'),
    'box|盒': ('Objects', 'Containers'),

    # Objects > Clothing
    'clothing|衣': ('Objects', 'Clothing'),
    'ornament|饰品': ('Objects', 'Clothing'),
    'hat|帽': ('Objects', 'Clothing'),
    'shoes|鞋': ('Objects', 'Clothing'),

    # Objects > Food
    'food|食品': ('Objects', 'Food'),
    'edible|食物': ('Objects', 'Food'),
    'drink|饮料': ('Objects', 'Food'),
    'taste|味': ('Objects', 'Food'),
    'cook|烹': ('Objects', 'Food'),

    # Communication > Language
    'language|语言': ('Communication', 'Language'),
    'text|语文': ('Communication', 'Language'),
    'symbol|符号': ('Communication', 'Language'),
    'expression|词语': ('Communication', 'Language'),
    'communicate|交流': ('Communication', 'Language'),
    'character|文字': ('Communication', 'Language'),  # Note: may cause over-categorization
    'knowledge|知识': ('Communication', 'Language'),  # know, understand
    'know|知道': ('Communication', 'Language'),
    'tell|告诉': ('Communication', 'Language'),
    'information|信息': ('Communication', 'Language'),

    # Communication > Arts
    'music|音乐': ('Communication', 'Arts'),
    'art|艺术': ('Communication', 'Arts'),
    'literature|文学': ('Communication', 'Arts'),
    'entertainment|娱乐': ('Communication', 'Arts'),

    # Abstract > Numbers
    'quantity|数量': ('Abstract', 'Numbers'),
    'number|数': ('Abstract', 'Numbers'),
    'single|单': ('Abstract', 'Numbers'),
    'double|复': ('Abstract', 'Numbers'),
    'ordinal|序数': ('Abstract', 'Numbers'),
    'cardinal|基数': ('Abstract', 'Numbers'),
    'amount|量': ('Abstract', 'Numbers'),

    # Abstract > Time
    'time|时间': ('Abstract', 'Time'),
    'day|日': ('Abstract', 'Time'),
    'month|月': ('Abstract', 'Time'),
    'year|年': ('Abstract', 'Time'),
    'TimeValue|时间值': ('Abstract', 'Time'),
    'past|过去': ('Abstract', 'Time'),
    'future|将来': ('Abstract', 'Time'),
    'FrequencyValue|频度值': ('Abstract', 'Time'),

    # Abstract > Space
    'space|空间': ('Abstract', 'Space'),
    'place|地方': ('Abstract', 'Space'),
    'location|位置': ('Abstract', 'Space'),
    'direction|方向': ('Abstract', 'Space'),
    'SpaceValue|空间值': ('Abstract', 'Space'),
    'upper|上': ('Abstract', 'Space'),
    'lower|下': ('Abstract', 'Space'),
    'internal|内': ('Abstract', 'Space'),
    'external|外': ('Abstract', 'Space'),
    'front|前': ('Abstract', 'Space'),
    'behind|后': ('Abstract', 'Space'),

    # Abstract > Colors
    'color|颜色': ('Abstract', 'Colors'),
    'ColorValue|颜色值': ('Abstract', 'Colors'),
    'red|红': ('Abstract', 'Colors'),
    'yellow|黄': ('Abstract', 'Colors'),
    'blue|蓝': ('Abstract', 'Colors'),
    'green|绿': ('Abstract', 'Colors'),
    'white|白': ('Abstract', 'Colors'),
    'black|黑': ('Abstract', 'Colors'),

    # Abstract > Qualities
    'attribute|属性': ('Abstract', 'Qualities'),
    'PropertyValue|特性值': ('Abstract', 'Qualities'),
    'good|好': ('Abstract', 'Qualities'),
    'bad|坏': ('Abstract', 'Qualities'),
    'big|大': ('Abstract', 'Qualities'),
    'small|小': ('Abstract', 'Qualities'),
    'long|长': ('Abstract', 'Qualities'),
    'short|短': ('Abstract', 'Qualities'),
    'high|高': ('Abstract', 'Qualities'),
    'low|低': ('Abstract', 'Qualities'),
    'new|新': ('Abstract', 'Qualities'),
    'old|旧': ('Abstract', 'Qualities'),
    'fast|快': ('Abstract', 'Qualities'),
    'slow|慢': ('Abstract', 'Qualities'),
    'strong|强': ('Abstract', 'Qualities'),
    'weak|弱': ('Abstract', 'Qualities'),
    'true|真': ('Abstract', 'Qualities'),
    'false|假': ('Abstract', 'Qualities'),
    # Moral/Character qualities (catches 女/心 radical "false friends")
    'Morality|道德': ('Abstract', 'Qualities'),
    'benevolent|仁': ('Abstract', 'Qualities'),
    'wicked|歹': ('Abstract', 'Qualities'),
    'guilty|有罪': ('Abstract', 'Qualities'),
    'rash|莽': ('Abstract', 'Qualities'),
    'arrogant|傲': ('Abstract', 'Qualities'),
    'mental|精神': ('Abstract', 'Qualities'),
    'reason|道理': ('Abstract', 'Qualities'),
    'method|方法': ('Abstract', 'Qualities'),
    # Function words → Language
    'FuncWord|功能词': ('Communication', 'Language'),
}


def get_category_from_hownet(char: str, hownet_dict, t2s_converter=None) -> tuple[str, str] | None:
    """
    Get category from HowNet sememes.
    Returns (root_category, primary_category) or None if not found.

    Uses OpenCC to convert traditional to simplified for better HowNet coverage.
    """
    try:
        all_sememes = set()

        # Try the character as-is first using get_sense (structured approach)
        senses = hownet_dict.get_sense(char)
        if senses:
            for sense in senses[:3]:
                try:
                    sememes = sense.get_sememe_list()
                    all_sememes.update(str(s) for s in sememes)
                except:
                    pass

        # Also use get_sememes_by_word which often returns more sememes
        try:
            merged_sememes = hownet_dict.get_sememes_by_word(char, merge=True)
            if merged_sememes:
                all_sememes.update(str(s) for s in merged_sememes)
        except:
            pass

        # If we only got generic sememes or nothing, try simplified version
        generic_only = (not all_sememes or
                       all_sememes == {'China|中国', 'character|文字'} or
                       all_sememes == {'character|文字'} or
                       all_sememes <= {'China|中国', 'character|文字'})

        if generic_only and t2s_converter is not None:
            simp_char = t2s_converter.convert(char)
            if simp_char != char:  # Only if conversion produced something different
                simp_senses = hownet_dict.get_sense(simp_char)
                if simp_senses:
                    all_sememes = set()  # Reset to use simplified sememes
                    for sense in simp_senses[:3]:
                        try:
                            sememes = sense.get_sememe_list()
                            all_sememes.update(str(s) for s in sememes)
                        except:
                            pass
                # Also get merged sememes for simplified
                try:
                    merged_sememes = hownet_dict.get_sememes_by_word(simp_char, merge=True)
                    if merged_sememes:
                        all_sememes.update(str(s) for s in merged_sememes)
                except:
                    pass

        if not all_sememes:
            return None

        # Skip if only has generic "character" sememe
        if all_sememes <= {'China|中国', 'character|文字'}:
            return None

        # Define priority sememes - check these first (more specific categories)
        # These take precedence over generic animal sememes like livestock|牲畜
        priority_sememes = [
            # Plants - should be Nature > Plants even if also has body/heart sememes
            # (木 tree and 花 flower have body|身 and heart|心 but are clearly plants)
            'AlgaeFungi|低植', 'FlowerGrass|花草', 'plant|植物', 'tree|树',
            'grass|草', 'flower|花', 'wood|木', 'grain|谷',
            # Body parts (after plants, so 木/花 don't get miscategorized)
            'part|部件', 'physiology|生理学', 'eye|眼', 'mouth|嘴', 'ear|耳',
            'bone|骨', 'viscera|脏', 'blood|血', 'flesh|肉', 'skin|皮', 'hair|发',
            'body|身', 'head|头', 'heart|心', 'hand|手', 'foot|脚',
            # Colors - should be Abstract > Colors, not Human > Relations
            'Color|颜色', 'color|颜色',
            'white|白', 'black|黑', 'red|红', 'yellow|黄', 'blue|蓝', 'green|绿',
            # Health - should be Abstract > Qualities
            'healthy|康健', 'Health|健康',
            # Moral/Character qualities - catches 女/心 radical "false friends"
            # (e.g., 奸 treacherous, 妄 absurd, 德 virtue, 道 way)
            'Morality|道德', 'benevolent|仁', 'wicked|歹', 'guilty|有罪',
            'rash|莽', 'arrogant|傲', 'mental|精神', 'reason|道理', 'method|方法',
            # Function words → Language (e.g., 如 if/like)
            'FuncWord|功能词',
            # Patterns/Styles - should be Abstract
            'Pattern|样式', 'Kind|类型',
            # Groups - should be Human > Relations
            'group|群体',
            # Directions - should be Abstract > Space
            'Vdirection|动趋',
            # Food - should be Objects > Food, not Animals
            'edible|食物', 'food|食品',
            # Human/Children - should be Human, not Animals
            'child|少儿', 'human|人',
            # Material/Measure words - should not be Animals
            'material|材料', 'NounUnit|名量',
        ]

        # Check priority sememes first
        for sememe in priority_sememes:
            if sememe in all_sememes and sememe in SEMEME_TO_CATEGORY:
                return SEMEME_TO_CATEGORY[sememe]

        # Sememes that indicate NON-animal concepts - should NOT be categorized as animals
        # even if they have AnimalHuman or beast sememe
        non_animal_indicators = {
            # Abstract concepts
            'Wisdom|智慧', 'wise|智', 'Power|势力', 'fierce|暴', 'brave|勇',
            'attribute|属性', 'mental|精神', 'emotion|情感', 'PropertyValue|特性值',
            # Colors
            'Color|颜色', 'color|颜色',
            # Health/Qualities
            'healthy|康健', 'Health|健康',
            # Patterns/Styles
            'Pattern|样式', 'Kind|类型', 'Attribute|属性',
            # Groups (could be human or animal, but primary meaning is human groups)
            'group|群体',
            # Directions/Positions
            'Vdirection|动趋', 'next|下次', 'drop|投下',
            # Actions that just happen to involve animals
            'add|增加', 'lose|失去', 'leave|离开',
            # Abilities/Senses (smart, clever, etc.) - abstract qualities
            'Ability|能力', 'listen|听', 'wise|智',
        }

        # Sememes that definitely indicate animals
        animal_sememes = {'AnimalHuman|动物', 'beast|走兽', 'livestock|牲畜'}

        # If we have non-animal indicators along with animal sememes, skip the animal categorization
        has_non_animal = bool(non_animal_indicators & all_sememes)
        has_animal = bool(animal_sememes & all_sememes)

        # Match against our category mapping
        for sememe in all_sememes:
            if sememe in SEMEME_TO_CATEGORY:
                # Skip generic "character" categorization
                if sememe == 'character|文字':
                    continue
                # Skip animal sememes if we have non-animal indicators
                if sememe in animal_sememes and has_non_animal:
                    continue
                return SEMEME_TO_CATEGORY[sememe]

        return None
    except Exception:
        return None


# WordNet lexname to category mapping (root, primary)
WORDNET_LEXNAME_TO_CATEGORY = {
    # Nature
    'noun.animal': ('Nature', 'Animals'),
    'noun.plant': ('Nature', 'Plants'),
    'noun.substance': ('Nature', 'Elements'),
    'noun.object': ('Nature', 'Elements'),
    'noun.phenomenon': ('Nature', 'Weather'),

    # Human
    'noun.body': ('Human', 'Body'),
    'noun.person': ('Human', 'Relations'),
    'noun.group': ('Human', 'Relations'),
    'verb.motion': ('Human', 'Actions'),
    'verb.contact': ('Human', 'Actions'),
    'verb.creation': ('Human', 'Actions'),
    'verb.change': ('Human', 'Actions'),
    'verb.consumption': ('Human', 'Actions'),
    'verb.cognition': ('Human', 'Actions'),
    'verb.perception': ('Human', 'Actions'),
    'verb.body': ('Human', 'Actions'),
    'verb.social': ('Human', 'Actions'),
    'noun.act': ('Human', 'Actions'),
    'noun.event': ('Human', 'Actions'),
    'noun.feeling': ('Human', 'Emotions'),
    'noun.motive': ('Human', 'Emotions'),
    'adj.all': ('Abstract', 'Qualities'),
    'adj.pert': ('Abstract', 'Qualities'),

    # Society
    'noun.state': ('Society', 'Government'),
    'noun.attribute': ('Abstract', 'Qualities'),
    'noun.possession': ('Society', 'Economy'),

    # Objects
    'noun.artifact': ('Objects', 'Tools'),
    'noun.food': ('Objects', 'Food'),
    'noun.location': ('Objects', 'Buildings'),

    # Communication
    'noun.communication': ('Communication', 'Language'),
    'verb.communication': ('Communication', 'Language'),

    # Abstract
    'noun.time': ('Abstract', 'Time'),
    'noun.quantity': ('Abstract', 'Numbers'),
    'noun.relation': ('Abstract', 'Miscellaneous'),
    'noun.cognition': ('Abstract', 'Miscellaneous'),
    'noun.Tops': ('Abstract', 'Miscellaneous'),

    # Verbs default
    'verb.stative': ('Abstract', 'Qualities'),
    'verb.emotion': ('Human', 'Emotions'),
    'verb.possession': ('Society', 'Economy'),
    'verb.competition': ('Human', 'Actions'),
    'verb.weather': ('Nature', 'Weather'),
}

# WordNet hypernym to subcategory mapping for 3-level depth
# Format: hypernym_name -> (primary_category, subcategory)
WORDNET_HYPERNYM_TO_SUBCATEGORY = {
    # Animals subcategories
    'bird': ('Animals', 'Birds'),
    'gallinaceous_bird': ('Animals', 'Birds'),
    'domestic_fowl': ('Animals', 'Birds'),
    'insect': ('Animals', 'Insects'),
    'caterpillar': ('Animals', 'Insects'),
    'larva': ('Animals', 'Insects'),
    'fish': ('Animals', 'Fish'),
    'reptile': ('Animals', 'Reptiles'),
    'amphibian': ('Animals', 'Amphibians'),
    'mammal': ('Animals', 'Mammals'),
    'placental': ('Animals', 'Mammals'),
    'ungulate': ('Animals', 'Mammals'),
    'carnivore': ('Animals', 'Mammals'),
    'feline': ('Animals', 'Mammals'),
    'bovid': ('Animals', 'Mammals'),
    'equine': ('Animals', 'Mammals'),
    'rodent': ('Animals', 'Mammals'),
    'primate': ('Animals', 'Mammals'),
    # Domestic animals (dogs, cats, etc.)
    'domestic_animal': ('Animals', 'Mammals'),
    'dog': ('Animals', 'Mammals'),
    'domestic_cat': ('Animals', 'Mammals'),
    'livestock': ('Animals', 'Mammals'),
    'aquatic_vertebrate': ('Animals', 'Fish'),
    'mollusk': ('Animals', 'Invertebrates'),
    'arthropod': ('Animals', 'Invertebrates'),
    'worm': ('Animals', 'Invertebrates'),
    'crustacean': ('Animals', 'Invertebrates'),
    # Mythical creatures
    'mythical_monster': ('Animals', 'Mythical'),
    'imaginary_being': ('Animals', 'Mythical'),
    'mythical_creature': ('Animals', 'Mythical'),
    'legendary_creature': ('Animals', 'Mythical'),

    # Plants subcategories
    'tree': ('Plants', 'Trees'),
    'woody_plant': ('Plants', 'Trees'),
    'shrub': ('Plants', 'Shrubs'),
    'flower': ('Plants', 'Flowers'),
    'angiosperm': ('Plants', 'Flowers'),
    'grass': ('Plants', 'Grasses'),
    'gramineous_plant': ('Plants', 'Grasses'),
    'cereal': ('Plants', 'Grasses'),
    'herb': ('Plants', 'Herbs'),
    'vegetable': ('Plants', 'Vegetables'),
    'fruit': ('Plants', 'Fruits'),
    'fungus': ('Plants', 'Fungi'),

    # Elements subcategories
    'chemical_element': ('Elements', 'Minerals'),
    'metal': ('Elements', 'Minerals'),
    'mineral': ('Elements', 'Minerals'),
    'geological_formation': ('Elements', 'Landforms'),
    'natural_elevation': ('Elements', 'Landforms'),
    'mountain': ('Elements', 'Landforms'),
    'body_of_water': ('Elements', 'Water'),
    'water': ('Elements', 'Water'),
    'fluid': ('Elements', 'Water'),
    'stream': ('Elements', 'Water'),

    # Body subcategories (Human > Body)
    'body_part': ('Body', 'Body Parts'),
    'organ': ('Body', 'Organs'),
    'sense_organ': ('Body', 'Sense Organs'),
    'internal_organ': ('Body', 'Organs'),
    'viscus': ('Body', 'Organs'),
    'skeletal_structure': ('Body', 'Skeleton'),
    'bone': ('Body', 'Skeleton'),
    'limb': ('Body', 'Limbs'),
    'extremity': ('Body', 'Limbs'),
    'hand': ('Body', 'Limbs'),
    'foot': ('Body', 'Limbs'),
    'arm': ('Body', 'Limbs'),
    'leg': ('Body', 'Limbs'),
    'face': ('Body', 'Face'),
    'facial_feature': ('Body', 'Face'),
    'mouth': ('Body', 'Face'),
    'nose': ('Body', 'Face'),
    'eye': ('Body', 'Sense Organs'),
    'ear': ('Body', 'Sense Organs'),
    'head': ('Body', 'Head'),
    'bodily_fluid': ('Body', 'Fluids'),
    'body_covering': ('Body', 'Covering'),
    'skin': ('Body', 'Covering'),
    'hair': ('Body', 'Covering'),
    'muscle': ('Body', 'Muscles'),
    'muscular_tissue': ('Body', 'Muscles'),

    # Relations subcategories
    'leader': ('Relations', 'Leaders'),
    'ruler': ('Relations', 'Leaders'),
    'sovereign': ('Relations', 'Leaders'),
    'relative': ('Relations', 'Family'),
    'parent': ('Relations', 'Family'),
    'sibling': ('Relations', 'Family'),
    'offspring': ('Relations', 'Family'),
    'ancestor': ('Relations', 'Family'),
    'worker': ('Relations', 'Occupations'),
    'professional': ('Relations', 'Occupations'),
    'skilled_worker': ('Relations', 'Occupations'),
    'organization': ('Relations', 'Groups'),
    'social_group': ('Relations', 'Groups'),

    # Tools/Artifacts subcategories
    'weapon': ('Tools', 'Weapons'),
    'container': ('Tools', 'Containers'),
    'vehicle': ('Tools', 'Vehicles'),
    'wheeled_vehicle': ('Tools', 'Vehicles'),
    'instrument': ('Tools', 'Instruments'),
    'implement': ('Tools', 'Implements'),
    'furniture': ('Tools', 'Furniture'),
    'fabric': ('Tools', 'Textiles'),
    'textile': ('Tools', 'Textiles'),
    'clothing': ('Tools', 'Clothing'),
    'garment': ('Tools', 'Clothing'),
    'building': ('Buildings', 'Structures'),
    'structure': ('Buildings', 'Structures'),

    # Actions subcategories
    'locomotion': ('Actions', 'Movement'),
    'motion': ('Actions', 'Movement'),
    'travel': ('Actions', 'Movement'),
    'speech_act': ('Actions', 'Speech'),
    'utterance': ('Actions', 'Speech'),
    'creation': ('Actions', 'Making'),
    'production': ('Actions', 'Making'),
    'destruction': ('Actions', 'Destruction'),
    'change': ('Actions', 'Change'),
    'group_action': ('Actions', 'Social'),
    'social_activity': ('Actions', 'Social'),
}


def get_category_from_wordnet(keyword: str, meaning: str = "", wordnet=None, require_subcategory: bool = False) -> tuple | None:
    """
    Get category from WordNet using keyword and meaning.
    Returns (root, primary) or (root, primary, subcategory) or None.

    If require_subcategory is True, only returns results that have a subcategory.
    """
    if wordnet is None:
        return None

    try:
        import re

        def get_category_for_synset(synset, need_subcat: bool = False):
            """Extract category info from a synset."""
            lexname = synset.lexname()

            # First check hypernym chain for special cases that override lexname
            # (e.g., mythical creatures are noun.person but should be Animals > Mythical)
            paths = synset.hypernym_paths()
            if paths:
                path = paths[0]
                hypernym_names = [p.name().split('.')[0] for p in path]

                # Check for mythical creatures first (they have noun.person lexname but should be Animals)
                mythical_hypernyms = {'imaginary_being', 'mythical_monster', 'mythical_creature', 'legendary_creature', 'monster'}
                if mythical_hypernyms & set(hypernym_names):
                    return ('Nature', 'Animals', 'Mythical')

            if lexname not in WORDNET_LEXNAME_TO_CATEGORY:
                return None

            root, primary = WORDNET_LEXNAME_TO_CATEGORY[lexname]

            # Try to find subcategory from hypernym chain
            if paths:
                path = paths[0]
                # Check hypernyms from most specific to most general
                for i in range(len(path) - 1, -1, -1):
                    hypernym_name = path[i].name().split('.')[0]
                    if hypernym_name in WORDNET_HYPERNYM_TO_SUBCATEGORY:
                        mapped_primary, subcategory = WORDNET_HYPERNYM_TO_SUBCATEGORY[hypernym_name]
                        # Only use if it matches our primary category
                        if mapped_primary == primary:
                            return (root, primary, subcategory)

            # If we need a subcategory but didn't find one, return None
            if need_subcat:
                return None
            return (root, primary)

        def try_word(word: str, need_subcat: bool = False):
            """Try to get category for a single word."""
            word = word.lower().strip()
            if len(word) < 2:
                return None
            synsets = wordnet.synsets(word)
            if synsets:
                # Try first few senses, not just the first
                for synset in synsets[:3]:
                    result = get_category_for_synset(synset, need_subcat)
                    if result:
                        return result
            return None

        # Extract all words from keyword
        keyword_words = re.sub(r'[^a-zA-Z\s]', '', keyword).strip().split() if keyword else []

        # Try keyword words first
        for word in keyword_words:
            result = try_word(word, require_subcategory)
            if result:
                return result

        # Try ALL words from meaning/definition (not just first 3)
        if meaning:
            meaning_words = re.sub(r'[^a-zA-Z\s]', '', meaning).strip().split()
            for word in meaning_words:
                if len(word) >= 3:  # Skip very short words
                    result = try_word(word, require_subcategory)
                    if result:
                        return result

        return None
    except Exception:
        return None


def get_semantic_category(char: str, keyword: str, meaning: str = "",
                          hownet_dict=None, t2s_converter=None, wordnet=None,
                          unihan_radicals: dict = None) -> tuple:
    """
    Determine semantic category for a character.
    Returns (root, primary) or (root, primary, subcategory).

    Priority:
    1. HowNet sememes (if available) - most accurate for Chinese
    2. Radical Anchor (NEW) - Use Kangxi radical for reliable Chinese-native fallback
    3. WordNet (if available) - good for English keywords/definitions, can provide subcategories
    4. Keyword/meaning pattern matching - fallback

    After initial categorization, tries to find subcategory if not already assigned.
    """
    base_category = None

    # Try HowNet sememe-based categorization first
    if hownet_dict is not None:
        category = get_category_from_hownet(char, hownet_dict, t2s_converter)
        if category:
            base_category = category  # HowNet returns 2-level only

    # NEW: Try Radical Anchor before WordNet
    # Radicals provide reliable Chinese-native categorization
    if base_category is None and unihan_radicals is not None:
        if char in unihan_radicals:
            radical_info = unihan_radicals[char]
            # radical_info is (radical_number, additional_strokes)
            if isinstance(radical_info, (list, tuple)) and len(radical_info) >= 1:
                radical_num = radical_info[0]
                if radical_num in KANGXI_RADICAL_TO_CATEGORY:
                    base_category = KANGXI_RADICAL_TO_CATEGORY[radical_num]

    # Try WordNet for English keywords/definitions (may return 3 levels)
    if base_category is None and wordnet is not None:
        category = get_category_from_wordnet(keyword, meaning, wordnet)
        if category:
            if len(category) == 3:
                return category  # Already has subcategory
            base_category = category

    # If we have a 2-level category from HowNet, Radical, or WordNet, try to find subcategory
    if base_category is not None and len(base_category) == 2 and wordnet is not None:
        # Try harder to find a subcategory using WordNet
        subcat_result = get_category_from_wordnet(keyword, meaning, wordnet, require_subcategory=True)
        if subcat_result and len(subcat_result) == 3:
            # Verify the subcategory matches our primary category
            if subcat_result[0] == base_category[0] and subcat_result[1] == base_category[1]:
                return subcat_result
        return base_category

    if base_category is not None:
        return base_category

    # Fallback to keyword matching (2-level only)
    text = f"{keyword} {meaning}".lower()

    # Define categories with keyword lists
    categories = {
        # Nature
        ("Nature", "Animals"): [
            'cat', 'dog', 'horse', 'bird', 'fish', 'tiger', 'dragon', 'ox', 'sheep',
            'pig', 'snake', 'rabbit', 'rat', 'chicken', 'elephant', 'deer', 'wolf',
            'lion', 'bear', 'monkey', 'insect', 'bee', 'butterfly', 'turtle', 'frog',
            'cow', 'goat', 'mouse', 'eagle', 'crow', 'duck', 'goose', 'swan', 'hawk',
            'crane', 'phoenix', 'worm', 'ant', 'spider', 'fly', 'mosquito', 'moth',
            'shrimp', 'crab', 'clam', 'oyster', 'snail', 'animal', 'beast', 'creature',
            'livestock', 'pet', 'wild', 'mammal', 'reptile', 'amphibian'
        ],
        ("Nature", "Plants"): [
            'tree', 'flower', 'grass', 'leaf', 'wood', 'forest', 'bamboo', 'rice',
            'grain', 'seed', 'root', 'branch', 'fruit', 'vegetable', 'pine', 'plum',
            'willow', 'oak', 'peach', 'pear', 'apple', 'orange', 'grape', 'melon',
            'bean', 'wheat', 'millet', 'corn', 'hemp', 'cotton', 'silk', 'plant',
            'herb', 'sprout', 'bud', 'blossom', 'petal', 'stem', 'trunk', 'bark',
            'vine', 'mushroom', 'moss', 'fern', 'lotus', 'orchid', 'chrysanthemum'
        ],
        ("Nature", "Elements"): [
            'water', 'fire', 'earth', 'metal', 'gold', 'silver', 'stone', 'mountain',
            'river', 'sea', 'lake', 'rain', 'snow', 'ice', 'wind', 'cloud', 'sun',
            'moon', 'star', 'sky', 'thunder', 'lightning', 'iron', 'copper', 'bronze',
            'jade', 'pearl', 'gem', 'diamond', 'crystal', 'sand', 'mud', 'clay',
            'rock', 'cliff', 'peak', 'valley', 'cave', 'spring', 'stream', 'ocean',
            'wave', 'tide', 'flood', 'dew', 'frost', 'mist', 'fog', 'vapor'
        ],
        ("Nature", "Weather"): [
            'sunny', 'cloudy', 'rainy', 'snowy', 'windy', 'storm', 'hurricane',
            'typhoon', 'drought', 'rainbow', 'hail', 'sleet', 'weather', 'climate',
            'season', 'spring', 'summer', 'autumn', 'winter', 'warm', 'cold', 'hot'
        ],
        # Human
        ("Human", "Body"): [
            'head', 'eye', 'ear', 'mouth', 'hand', 'foot', 'heart', 'bone', 'blood',
            'face', 'nose', 'tooth', 'tongue', 'finger', 'leg', 'arm', 'hair', 'skin',
            'neck', 'shoulder', 'chest', 'back', 'waist', 'belly', 'stomach', 'liver',
            'lung', 'kidney', 'brain', 'nerve', 'muscle', 'flesh', 'body', 'limb',
            'palm', 'elbow', 'knee', 'ankle', 'wrist', 'thumb', 'nail', 'eyelid',
            'eyebrow', 'cheek', 'chin', 'lip', 'throat', 'spine', 'rib', 'skull'
        ],
        ("Human", "Actions"): [
            'walk', 'run', 'eat', 'drink', 'sleep', 'speak', 'write', 'read', 'see',
            'hear', 'think', 'feel', 'love', 'hate', 'go', 'come', 'stand', 'sit',
            'lie', 'jump', 'climb', 'swim', 'fly', 'dance', 'sing', 'play', 'work',
            'study', 'teach', 'learn', 'know', 'remember', 'forget', 'believe', 'doubt',
            'hope', 'fear', 'laugh', 'cry', 'smile', 'weep', 'shout', 'whisper',
            'push', 'pull', 'lift', 'carry', 'throw', 'catch', 'hold', 'grasp', 'grab',
            'hit', 'strike', 'kick', 'punch', 'cut', 'slice', 'chop', 'stab', 'shoot',
            'open', 'close', 'enter', 'exit', 'leave', 'arrive', 'return', 'stay',
            'move', 'stop', 'start', 'begin', 'end', 'finish', 'continue', 'wait'
        ],
        ("Human", "Relations"): [
            'father', 'mother', 'son', 'daughter', 'brother', 'sister', 'wife',
            'husband', 'friend', 'teacher', 'student', 'king', 'emperor', 'master',
            'parent', 'child', 'baby', 'infant', 'elder', 'ancestor', 'descendant',
            'uncle', 'aunt', 'nephew', 'niece', 'cousin', 'grandparent', 'grandchild',
            'family', 'clan', 'tribe', 'nation', 'people', 'person', 'man', 'woman',
            'boy', 'girl', 'gentleman', 'lady', 'servant', 'slave', 'lord', 'noble'
        ],
        ("Human", "Emotions"): [
            'happy', 'sad', 'angry', 'afraid', 'joy', 'sorrow', 'anger', 'fear',
            'surprise', 'disgust', 'shame', 'guilt', 'pride', 'envy', 'jealous',
            'anxious', 'worry', 'stress', 'calm', 'peace', 'content', 'satisfy',
            'desire', 'wish', 'want', 'need', 'miss', 'lonely', 'depressed', 'excited'
        ],
        # Society
        ("Society", "Government"): [
            'country', 'state', 'kingdom', 'empire', 'government', 'politics', 'law',
            'rule', 'order', 'power', 'authority', 'official', 'minister', 'court',
            'palace', 'throne', 'crown', 'decree', 'edict', 'tax', 'tribute', 'army',
            'military', 'soldier', 'general', 'war', 'battle', 'victory', 'defeat'
        ],
        ("Society", "Economy"): [
            'money', 'wealth', 'rich', 'poor', 'trade', 'commerce', 'merchant', 'market',
            'shop', 'store', 'buy', 'sell', 'price', 'cost', 'profit', 'loss',
            'borrow', 'lend', 'debt', 'pay', 'wage', 'salary', 'property', 'asset'
        ],
        ("Society", "Religion"): [
            'god', 'spirit', 'ghost', 'soul', 'heaven', 'hell', 'temple', 'shrine',
            'church', 'mosque', 'buddha', 'monk', 'priest', 'pray', 'worship',
            'sacred', 'holy', 'divine', 'blessing', 'curse', 'fate', 'destiny',
            'fortune', 'luck', 'omen', 'ritual', 'ceremony', 'sacrifice', 'offering'
        ],
        # Objects
        ("Objects", "Tools"): [
            'knife', 'sword', 'bow', 'arrow', 'axe', 'hammer', 'needle', 'thread',
            'rope', 'chain', 'hook', 'nail', 'screw', 'saw', 'drill', 'shovel',
            'rake', 'hoe', 'plow', 'wheel', 'cart', 'wagon', 'boat', 'ship',
            'vehicle', 'tool', 'instrument', 'weapon', 'utensil', 'device', 'machine'
        ],
        ("Objects", "Buildings"): [
            'house', 'door', 'window', 'wall', 'roof', 'room', 'gate', 'temple',
            'tower', 'bridge', 'road', 'path', 'street', 'hall', 'palace', 'castle',
            'fortress', 'prison', 'school', 'hospital', 'inn', 'hotel', 'building',
            'structure', 'floor', 'ceiling', 'stair', 'pillar', 'beam', 'foundation'
        ],
        ("Objects", "Containers"): [
            'box', 'bottle', 'cup', 'bowl', 'pot', 'basket', 'bag', 'chest',
            'jar', 'vase', 'barrel', 'bucket', 'tank', 'can', 'container', 'vessel',
            'package', 'envelope', 'case', 'trunk', 'coffin', 'urn', 'cabinet'
        ],
        ("Objects", "Clothing"): [
            'clothes', 'garment', 'robe', 'coat', 'jacket', 'shirt', 'pants', 'skirt',
            'dress', 'hat', 'cap', 'helmet', 'shoe', 'boot', 'sock', 'glove',
            'belt', 'button', 'zipper', 'pocket', 'collar', 'sleeve', 'fabric', 'cloth'
        ],
        ("Objects", "Food"): [
            'meat', 'fish', 'egg', 'milk', 'bread', 'noodle', 'soup', 'sauce',
            'salt', 'sugar', 'oil', 'vinegar', 'wine', 'tea', 'coffee', 'alcohol',
            'meal', 'dish', 'cuisine', 'cook', 'boil', 'fry', 'roast', 'bake',
            'taste', 'flavor', 'spice', 'sweet', 'sour', 'bitter', 'salty', 'savory'
        ],
        # Abstract
        ("Abstract", "Numbers"): [
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
            'ten', 'hundred', 'thousand', 'million', 'billion', 'zero', 'half',
            'double', 'triple', 'first', 'second', 'third', 'number', 'count', 'amount'
        ],
        ("Abstract", "Time"): [
            'time', 'year', 'month', 'week', 'day', 'hour', 'minute', 'second',
            'morning', 'noon', 'afternoon', 'evening', 'night', 'midnight', 'dawn',
            'dusk', 'today', 'yesterday', 'tomorrow', 'past', 'present', 'future',
            'ancient', 'old', 'new', 'young', 'early', 'late', 'always', 'never'
        ],
        ("Abstract", "Space"): [
            'place', 'location', 'position', 'direction', 'north', 'south', 'east',
            'west', 'up', 'down', 'left', 'right', 'front', 'back', 'inside', 'outside',
            'near', 'far', 'high', 'low', 'long', 'short', 'wide', 'narrow', 'deep',
            'shallow', 'big', 'small', 'large', 'tiny', 'huge', 'vast', 'space', 'area'
        ],
        ("Abstract", "Colors"): [
            'color', 'red', 'blue', 'green', 'yellow', 'black', 'white', 'purple',
            'orange', 'pink', 'brown', 'gray', 'grey', 'gold', 'silver', 'bright',
            'dark', 'light', 'pale', 'vivid', 'colorful', 'dull', 'shine', 'glow'
        ],
        ("Abstract", "Qualities"): [
            'good', 'bad', 'beautiful', 'ugly', 'strong', 'weak', 'fast', 'slow',
            'hard', 'soft', 'heavy', 'light', 'thick', 'thin', 'full', 'empty',
            'clean', 'dirty', 'pure', 'mixed', 'true', 'false', 'real', 'fake',
            'right', 'wrong', 'correct', 'incorrect', 'perfect', 'flawed', 'quality'
        ],
        # Communication
        ("Communication", "Language"): [
            'word', 'speech', 'language', 'voice', 'sound', 'tone', 'accent', 'dialect',
            'sentence', 'phrase', 'grammar', 'meaning', 'symbol', 'sign', 'letter',
            'character', 'script', 'text', 'book', 'document', 'article', 'essay',
            'poem', 'story', 'novel', 'literature', 'writing', 'reading', 'translate'
        ],
        ("Communication", "Arts"): [
            'art', 'music', 'song', 'melody', 'rhythm', 'dance', 'drama', 'theater',
            'paint', 'draw', 'sketch', 'sculpture', 'craft', 'design', 'pattern',
            'style', 'beauty', 'aesthetic', 'creative', 'artistic', 'perform', 'act'
        ],
    }

    # Check each category
    for (root, primary), keywords in categories.items():
        for kw in keywords:
            # Use word boundary matching to avoid partial matches
            if re.search(rf'\b{re.escape(kw)}\b', text):
                return (root, primary)

    # Default: Abstract/Miscellaneous
    return ("Abstract", "Miscellaneous")


def build_semantic_tree(entries: list[dict], unihan_radicals: dict = None) -> dict:
    """
    Build hierarchical tree structure from Heisig entries.
    Uses HowNet for primary categorization, Radical Anchor, WordNet for English, keyword matching as fallback.
    """
    print("Building semantic tree...")
    unihan_radicals = unihan_radicals or {}

    # Initialize HowNet, OpenCC, and WordNet
    hownet_dict = None
    t2s_converter = None
    wordnet = None
    hownet_hits = 0
    radical_hits = 0
    wordnet_hits = 0
    keyword_hits = 0

    try:
        import OpenHowNet
        hownet_dict = OpenHowNet.HowNetDict()
        print("  HowNet initialized successfully")
    except Exception as e:
        print(f"  Warning: Could not initialize HowNet: {e}")

    try:
        import opencc
        t2s_converter = opencc.OpenCC('t2s')  # Traditional to Simplified
        print("  OpenCC initialized (Traditional -> Simplified conversion enabled)")
    except Exception as e:
        print(f"  Warning: Could not initialize OpenCC: {e}")

    try:
        from nltk.corpus import wordnet as wn
        # Test that it works
        wn.synsets('test')
        wordnet = wn
        print("  WordNet initialized (English semantic lookup enabled)")
    except Exception as e:
        print(f"  Warning: Could not initialize WordNet: {e}")

    if unihan_radicals:
        print(f"  Unihan radicals loaded ({len(unihan_radicals)} characters)")

    # Group by categories - support 3 levels: root -> primary -> subcategory
    # tree_data[root][primary][subcategory] = [chars]
    tree_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    subcategory_hits = 0

    for entry in entries:
        char = entry['traditional_char']
        keyword = entry['heisig_keyword']
        meaning = entry.get('meaning', '')

        # Try HowNet first, then Radical Anchor, then WordNet, then keyword matching
        category = get_semantic_category(char, keyword, meaning, hownet_dict, t2s_converter, wordnet, unihan_radicals)

        # Handle 2-level or 3-level results
        if len(category) == 3:
            root_cat, primary_cat, sub_cat = category
            subcategory_hits += 1
        else:
            root_cat, primary_cat = category
            sub_cat = None  # No subcategory

        # Track statistics
        hownet_category = None
        wordnet_category = None

        if hownet_dict is not None:
            hownet_category = get_category_from_hownet(char, hownet_dict, t2s_converter)

        # Check radical anchor
        radical_category = None
        if unihan_radicals and char in unihan_radicals:
            radical_info = unihan_radicals[char]
            if isinstance(radical_info, (list, tuple)) and len(radical_info) >= 1:
                radical_num = radical_info[0]
                if radical_num in KANGXI_RADICAL_TO_CATEGORY:
                    radical_category = KANGXI_RADICAL_TO_CATEGORY[radical_num]

        if wordnet is not None and hownet_category is None and radical_category is None:
            wordnet_category = get_category_from_wordnet(keyword, meaning, wordnet)

        if hownet_category:
            hownet_hits += 1
        elif radical_category:
            radical_hits += 1
        elif wordnet_category:
            wordnet_hits += 1
        else:
            keyword_hits += 1

        char_data = {
            'char': char,
            'simp': entry.get('simplified_char'),
            'keyword': keyword,
            'pinyin': entry.get('pinyin'),
            'meaning': entry.get('meaning'),
            'study_order': entry.get('study_order'),
        }

        # Store with subcategory key (None means no subcategory)
        tree_data[root_cat][primary_cat][sub_cat].append(char_data)

    print(f"  HowNet categorized: {hownet_hits} characters")
    print(f"  Radical Anchor categorized: {radical_hits} characters")
    print(f"  WordNet categorized: {wordnet_hits} characters")
    print(f"  Keyword fallback: {keyword_hits} characters")
    print(f"  With subcategories: {subcategory_hits} characters")

    # Convert to tree structure with optional 3rd level
    tree = {
        'name': 'Hanzi Universe',
        'children': []
    }

    for root_cat, primary_cats in sorted(tree_data.items()):
        root_node = {
            'name': root_cat,
            'children': []
        }
        for primary_cat, subcats in sorted(primary_cats.items()):
            primary_node = {
                'name': primary_cat,
                'children': []
            }

            # Check if we have subcategories or just direct characters
            has_subcategories = any(k is not None for k in subcats.keys())

            if has_subcategories:
                # Group characters with subcategories
                for sub_cat, chars in sorted(subcats.items(), key=lambda x: (x[0] is None, x[0] or '')):
                    if sub_cat is None:
                        # Characters without subcategory go directly
                        primary_node['children'].extend(chars)
                    else:
                        # Create subcategory node
                        sub_node = {
                            'name': sub_cat,
                            'children': chars
                        }
                        primary_node['children'].append(sub_node)
            else:
                # All characters are without subcategory
                for chars in subcats.values():
                    primary_node['children'].extend(chars)

            root_node['children'].append(primary_node)
        tree['children'].append(root_node)

    return tree


def try_openhownet_integration(entries: list[dict]) -> dict[str, dict]:
    """
    Try to get semantic data from OpenHowNet.
    Returns dict mapping char -> {root_sememe, primary_sememe}
    """
    try:
        import OpenHowNet
        hownet = OpenHowNet.HowNetDict()
        print("OpenHowNet loaded successfully!")

        sememe_data = {}
        for entry in entries[:100]:  # Start with first 100 for testing
            char = entry['traditional_char']
            try:
                results = hownet.get(char)
                if results:
                    # Get first sense
                    sense = results[0]
                    sememes = hownet.get_sememes_by_word(char, structured=True)
                    if sememes:
                        sememe_data[char] = {
                            'root': sememes[0].get('root', 'Unknown'),
                            'primary': sememes[0].get('sememe', 'Unknown')
                        }
            except Exception:
                pass

        return sememe_data
    except ImportError:
        print("OpenHowNet not installed. Using keyword-based categorization.")
        print("To install: pip install OpenHowNet")
        return {}


def count_chars_recursive(node):
    """Count characters recursively in a node."""
    if 'char' in node:
        return 1
    return sum(count_chars_recursive(child) for child in node.get('children', []))


def print_stats(tree: dict):
    """Print statistics about the generated tree."""
    total_chars = 0
    print("\nTree Statistics:")
    print("-" * 40)

    for root_node in tree['children']:
        root_count = 0
        for primary_node in root_node['children']:
            char_count = count_chars_recursive(primary_node)
            root_count += char_count

            # Check for subcategories
            subcats = [c for c in primary_node.get('children', []) if 'name' in c]
            if subcats:
                print(f"  {root_node['name']} > {primary_node['name']}: {char_count} chars ({len(subcats)} subcats)")
                for subcat in subcats[:3]:
                    sub_count = count_chars_recursive(subcat)
                    print(f"    - {subcat['name']}: {sub_count} chars")
                if len(subcats) > 3:
                    print(f"    - ... and {len(subcats) - 3} more subcategories")
            else:
                print(f"  {root_node['name']} > {primary_node['name']}: {char_count} chars")

        total_chars += root_count
        print(f"  {root_node['name']} Total: {root_count}")
        print()

    print(f"Total characters in tree: {total_chars}")


def main():
    """Main entry point."""
    print("=" * 50)
    print("Chinese Character Semantic Graph Builder")
    print("=" * 50)

    # Step 1: Fetch Heisig data (3036 characters)
    print("\n[1/5] Fetching Heisig data...")
    heisig_entries = fetch_heisig_data()

    if not heisig_entries:
        print("ERROR: No Heisig data fetched!")
        return

    # Step 2: Load extended data (char_glosses + curated names + Unihan)
    print("\n[2/5] Loading extended data...")
    char_glosses, curated_names, unihan_radicals, unihan_definitions = load_extended_data()

    # Step 3: Extend with ALL dictionary characters (dedupe keywords using Unihan)
    print("\n[3/5] Extending with dictionary characters...")
    all_entries = extend_with_dictionary(heisig_entries, char_glosses, curated_names, unihan_definitions)

    # Step 4: Build semantic tree (with Radical Anchor fallback)
    print("\n[4/5] Building semantic tree...")
    tree = build_semantic_tree(all_entries, unihan_radicals)

    # Step 5: Print stats
    print_stats(tree)

    # Step 6: Save output
    print("\n[5/5] Saving output...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print("Done!")


if __name__ == "__main__":
    main()

