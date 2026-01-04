# Chinese Character Semantic Categorization System

## Overview

This document describes the complete system for:
1. **Generating unique English glosses (keywords)** for every Chinese character
2. **Categorizing characters into a semantic hierarchy** for visualization and learning

The goal is to create a browsable "Hanzi Universe" where users can explore ~23,000 Chinese characters organized by meaning.

---

## Part 1: Unique English Keyword Generation

### The Problem

We need a unique, memorable English keyword for each of ~23,000 Chinese characters. Keywords must be:
- **Unique**: No two characters can share the same keyword
- **Meaningful**: The keyword should reflect the character's primary meaning
- **Concise**: Short enough to display in a UI (ideally 1-3 words, max ~25 chars)

### Data Sources (Priority Order)

#### 1. Heisig Keywords (Highest Priority - ~3,036 characters)

**Source**: James Heisig's "Remembering the Hanzi" methodology, specifically from [agj/3000-traditional-hanzi](https://github.com/agj/3000-traditional-hanzi)

**Why this is best**: Heisig keywords are carefully curated to be:
- Unique across all characters
- Memorable and evocative
- Designed for mnemonic learning

**Format**: TSV file with fields including traditional character, simplified variant, pinyin, keyword, and meaning.

**Rule**: Heisig keywords are NEVER overridden by any other source.

#### 2. Curated Names (~1,800 characters)

**Source**: Hand-curated `curated_component_names_v2.json`

**Purpose**: Provides quality keywords for:
- Common radicals and components not in Heisig
- Characters where dictionary definitions are poor
- Conflict resolution between similar characters

**Rule**: Only applied to non-Heisig characters. If a keyword conflicts with an existing one, it's made unique via suffix.

#### 3. Dictionary Definitions (~19,800 characters)

**Source**: `char_glosses.json` containing CEDICT-derived definitions for 23,000+ characters

**Processing**:
```python
def clean_definition(defn: str) -> str:
    # Remove parenthetical prefixes like "(variant of X)"
    # Take first phrase before comma/semicolon
    # Remove trailing parentheticals
    # Limit to ~25 characters (3 words max)
```

**Examples**:
- `"(same as 貓) cat, feline"` → `"cat"`
- `"to walk; to go; to travel"` → `"to walk"`

### Unihan Semantic Deduplication

Before falling back to mechanical suffixes, we try to use Unihan definitions to create semantically meaningful unique keywords.

**Source**: Unicode Unihan database (`kDefinition` field) with ~23,285 character definitions

**How it works**:
1. If a keyword conflicts, check if Unihan has a definition for this character
2. Extract distinguishing words from the Unihan definition
3. Create a more descriptive keyword like "jade ring" instead of "jade (var)"

**Word Count Limit**: Generated keywords are limited to **4 words maximum** (`MAX_KEYWORD_WORDS = 4`).
- This prevents overly verbose keywords like "A kind of jade that was used in ancient rituals"
- If semantic extraction produces > 4 words, fall back to suffix-based uniquification

**Distinguishing Word Extraction** (`extract_semantic_qualifier()`):
```python
# Words we look for to differentiate similar characters:
distinguishing_words = [
    'disk', 'tablet', 'ring', 'pendant', 'ornament', 'seal', 'scepter',
    'beautiful', 'precious', 'flawless', 'fine', 'rough', 'uncut',
    'white', 'green', 'black', 'red', 'yellow', 'blue',
    'round', 'flat', 'long', 'small', 'large', 'ancient',
    'ritual', 'ceremonial', 'imperial', 'royal',
    'pair', 'two', 'half', 'broken', 'cracked',
    'star', 'moon', 'sun', 'mountain', 'water', 'cloud',
]
```

**Examples**:
- Instead of `jade (var)` → `jade ring` (璩)
- Instead of `jade (alt)` → `beautiful jade` (璆)
- Instead of `jade (3eb0)` → `semicircular jade` (璜)
- `"piece of jade with hole in it"` → `jade disk` (matches "hole" pattern)

### Uniqueness Resolution (Fallback)

When semantic deduplication doesn't help, we append suffixes in order:
1. `(hex code)` - e.g., "horse (99ac)"
2. `(var)` - variant
3. `(alt)` - alternate
4. `(ii)`, `(iii)` - numbered
5. `(rare)`, `(archaic)` - for uncommon characters
6. `(U+XXXX)` - Unicode code point (last resort)

### Final Statistics
- ~3,036 from Heisig (protected, never changed)
- ~487 from curated names
- ~19,812 from dictionary with auto-uniquification
- **Total: ~23,335 characters with unique keywords**

---

## Part 2: Semantic Categorization

### The Hierarchy

Characters are organized into a 3-level hierarchy:
```
Root Category (7 total)
└── Primary Category
    └── Subcategory (optional)
        └── Characters
```

**Root Categories**:
1. **Nature** - Animals, Plants, Elements, Weather
2. **Human** - Body, Actions, Relations, Emotions  
3. **Society** - Government, Economy, Religion
4. **Objects** - Tools, Buildings, Containers, Clothing, Food
5. **Abstract** - Numbers, Time, Space, Colors, Qualities
6. **Communication** - Language, Arts

### Categorization Pipeline (Priority Order)

#### Step 1: HowNet Sememe Lookup (Chinese-First)

**What is HowNet?**
[OpenHowNet](https://github.com/thunlp/OpenHowNet) is a Chinese semantic knowledge base that describes word meanings using "sememes" - the smallest semantic units.

**Example**: The character 狗 (dog) has sememes: `['dog|狗', 'livestock|牲畜', 'AnimalHuman|动物']`

**How we use it**:
1. Look up the character in HowNet
2. Also try the simplified form (using OpenCC for Traditional→Simplified conversion)
3. Use both `get_sense()` + `get_sememe_list()` AND `get_sememes_by_word()` for better coverage
4. Map sememes to categories via a lookup table

**Sememe → Category Mapping** (excerpt):
```python
SEMEME_TO_CATEGORY = {
    'animal|动物': ('Nature', 'Animals'),
    'bird|禽': ('Nature', 'Animals'),
    'plant|植物': ('Nature', 'Plants'),
    'tree|树': ('Nature', 'Plants'),
    'human|人': ('Human', 'Relations'),
    'emotion|情感': ('Human', 'Emotions'),
    'Color|颜色': ('Abstract', 'Colors'),
    'white|白': ('Abstract', 'Colors'),
    # ... ~150 mappings total
}
```

**Priority Sememes**: Certain sememes take precedence to avoid miscategorization. These are checked FIRST, before any other categorization logic:

1. **Plants** (checked before body parts to prevent 木 tree → Human > Body):
   - `FlowerGrass|花草`, `plant|植物`, `tree|树`, `grass|草`, `flower|花`, `wood|木`, `grain|谷`

2. **Body parts**:
   - `eye|眼`, `mouth|嘴`, `ear|耳`, `bone|骨`, `viscera|脏`, `blood|血`, `heart|心`

3. **Moral/Abstract Qualities** (catches "False Friends" from 女/心 radicals):
   - `Morality|道德`, `benevolent|仁`, `wicked|歹`, `guilty|有罪`
   - `rash|莽`, `arrogant|傲`, `mental|精神`, `reason|道理`, `method|方法`
   - This ensures 奸 (treacherous), 妄 (absurd), 德 (virtue), 道 (way) go to Abstract > Qualities

4. **Function Words** → Communication > Language:
   - `FuncWord|功能词` - ensures 如 (if/like) goes to Language, not Relations

5. **Colors**:
   - `Color|颜色`, `white|白`, `black|黑`, `red|红`, `yellow|黄`, `blue|蓝`, `green|绿`

6. **Food**:
   - `edible|食物`, `food|食品` → Objects > Food (not Animals)

**Non-Animal Indicators**: If a character has these sememes, we ignore animal sememes:
- Abstract concepts: `Wisdom|智慧`, `Attribute|属性`, `Ability|能力`
- Colors: `Color|颜色`
- Directions: `Vdirection|动趋`
- Qualities: `Pattern|样式`, `Kind|类型`

**Why Priority Order Matters**:
The character 草 (grass) has HowNet sememes `['material|材料', 'write|写', 'FlowerGrass|花草']`. Without priority ordering, it might match `write|写` → Human > Actions. By checking plant sememes first, it correctly goes to Nature > Plants.

#### Step 2: Radical Anchor (Chinese-Native Fallback)

**What are Kangxi Radicals?**
The 214 Kangxi radicals are traditional components used to index Chinese characters. Many radicals have inherent semantic meaning (e.g., 氵 water, 木 tree, 犭 animal).

**Source**: Unicode Unihan database (`kRSKangXi` field) with ~103,000 character-to-radical mappings

**When used**: If HowNet doesn't return a category

**How we use it**:
1. Look up the character's Kangxi radical number from Unihan
2. Map the radical to a semantic category

**Radical → Category Mapping** (excerpt from `scripts/radical_mapping.py`):
```python
KANGXI_RADICAL_TO_CATEGORY = {
    # Nature > Animals
    142: ('Nature', 'Animals', 'Insects'),      # 虫 insect
    153: ('Nature', 'Animals', 'Mammals'),      # 豸 beast/badger
    187: ('Nature', 'Animals', 'Mammals'),      # 馬 horse
    195: ('Nature', 'Animals', 'Fish'),         # 魚 fish
    196: ('Nature', 'Animals', 'Birds'),        # 鳥 bird

    # Nature > Plants
    75: ('Nature', 'Plants', 'Trees'),          # 木 tree
    115: ('Nature', 'Plants', 'Grasses'),       # 禾 grain
    140: ('Nature', 'Plants', 'Grasses'),       # 艸 grass

    # Nature > Elements
    32: ('Nature', 'Elements', 'Landforms'),    # 土 earth
    46: ('Nature', 'Elements', 'Landforms'),    # 山 mountain
    85: ('Nature', 'Elements', 'Water'),        # 水 water
    86: ('Nature', 'Elements', 'Minerals'),     # 火 fire
    112: ('Nature', 'Elements', 'Minerals'),    # 石 stone
    167: ('Nature', 'Elements', 'Minerals'),    # 金 metal

    # ... 66 radical mappings total
}
```

**Why this works**: Characters with radical 魚 (fish) are almost always fish names. Characters with radical 鳥 (bird) are almost always bird names. This provides reliable Chinese-native categorization for thousands of characters.

**"False Friends" - Radicals That Don't Work**:

Some radicals are "semantic chameleons" - they appear in characters with very different meanings:

| Radical | Name | Works For | Fails For |
|---------|------|-----------|-----------|
| 38 女 | woman | 妈 (mom), 姑 (aunt) | 奸 (treacherous), 妄 (absurd), 如 (if) |
| 61 心 | heart | 情 (emotion), 愛 (love) | 思 (think), 德 (virtue), 忠 (loyal) |
| 9 人 | person | 他 (he), 們 (plural) | Abstract concepts with person component |

**Solution**: These radicals ARE mapped (to Human > Relations/Emotions), but the **Priority Sememes in Step 1** catch abstract/moral concepts BEFORE the radical anchor runs. This ensures:
- 奸 (treacherous) → Abstract > Qualities (via `wicked|歹` sememe)
- 德 (virtue) → Abstract > Qualities (via `Morality|道德` sememe)
- 如 (if/like) → Communication > Language (via `FuncWord|功能词` sememe)

**Unmapped Radicals**: Some radicals are purely graphical and NOT mapped:
- 6 亅 (hook) - just a stroke, no semantic meaning
- 111 矢 (arrow) - used phonetically in 知 (know)

Characters with unmapped radicals fall through to WordNet (Step 3).

#### Step 3: WordNet Lookup (English-Based)

**What is WordNet?**
[NLTK WordNet](https://www.nltk.org/howto/wordnet.html) is an English lexical database organized by "synsets" (synonym sets) with semantic relationships.

**When used**: If neither HowNet nor Radical Anchor returns a category

**How we use it**:
1. Look up the English keyword in WordNet
2. Also try all words from the character's definition/meaning
3. Get the "lexname" (lexical category) of the first synset
4. Map lexname to our category

**Lexname → Category Mapping** (excerpt):
```python
WORDNET_LEXNAME_TO_CATEGORY = {
    'noun.animal': ('Nature', 'Animals'),
    'noun.plant': ('Nature', 'Plants'),
    'noun.body': ('Human', 'Body'),
    'noun.person': ('Human', 'Relations'),
    'noun.artifact': ('Objects', 'Tools'),
    'noun.food': ('Objects', 'Food'),
    'adj.all': ('Abstract', 'Qualities'),
    # ... etc
}
```

#### Step 4: WordNet Hypernym Chain (For Subcategories)

**The Problem**: WordNet lexnames only give 2 levels. We want 3 levels (subcategories like "Mammals", "Birds", "Insects").

**Solution**: Walk up the hypernym chain to find specific subcategories.

**Example**: For "eagle":
```
eagle.n.01
  └── bird_of_prey.n.01
      └── bird.n.01  ← matches "bird" → Animals > Birds
          └── vertebrate.n.01
              └── animal.n.01
```

**Hypernym → Subcategory Mapping** (excerpt):
```python
WORDNET_HYPERNYM_TO_SUBCATEGORY = {
    # Animals
    'bird': ('Animals', 'Birds'),
    'insect': ('Animals', 'Insects'),
    'fish': ('Animals', 'Fish'),
    'mammal': ('Animals', 'Mammals'),
    'reptile': ('Animals', 'Reptiles'),
    
    # Plants  
    'tree': ('Plants', 'Trees'),
    'flower': ('Plants', 'Flowers'),
    'fungus': ('Plants', 'Fungi'),
    
    # Body
    'body_part': ('Body', 'Body Parts'),
    'organ': ('Body', 'Organs'),
    'limb': ('Body', 'Limbs'),
    
    # ... ~80 mappings total
}
```

#### Step 5: Keyword Pattern Matching (Final Fallback)

**When used**: If HowNet, Radical Anchor, and WordNet all fail to provide a category

**How it works**: Simple keyword matching against curated word lists

```python
categories = {
    ("Nature", "Animals"): [
        'cat', 'dog', 'horse', 'bird', 'fish', 'tiger', 'dragon', ...
    ],
    ("Nature", "Plants"): [
        'tree', 'flower', 'grass', 'leaf', 'bamboo', 'rice', ...
    ],
    # ... etc
}

text = f"{keyword} {meaning}".lower()
for (root, primary), keywords in categories.items():
    for kw in keywords:
        if kw in text:
            return (root, primary)
```

### Special Handling

#### Mythical Creatures
WordNet classifies dragons, phoenixes, unicorns as `noun.person` (imaginary being). We detect these via hypernym chain and override to Animals > Mythical.

#### Traditional → Simplified Conversion  
Many characters have better HowNet coverage in simplified form. We use OpenCC to convert and try both forms.

#### Color Words Overriding Person
"White" in WordNet's first sense is "a member of the Caucasoid race" (noun.person). We add color sememes to priority list to catch this.

---

## Current Results

| Metric | Count | % of Total |
|--------|-------|------------|
| Total characters | 23,335 | 100% |
| HowNet categorized | 5,056 | 22% |
| **Radical Anchor categorized** | **15,127** | **65%** |
| WordNet categorized | 3,114 | 13% |
| Keyword fallback | 38 | <1% |
| **With subcategories** | **12,384** | **53%** |

### Categorization Pipeline Efficiency

The addition of Radical Anchor + expanded mappings dramatically improved Chinese-native categorization:

| Source | Original | With Radical | Final (Expanded) |
|--------|----------|--------------|------------------|
| Chinese-native (HowNet + Radical) | 18% | 83% | **87%** |
| English-based (WordNet) | 81% | 17% | **13%** |
| Keyword fallback | 1% | <1% | <1% |
| Subcategory coverage | 28% | 51% | **53%** |

### Top 500 Characters: 100% Coverage ✅
All top 500 most common Chinese characters are properly categorized by the pipeline.

### Animals Category (Example)
| Metric | Before Optimization | After |
|--------|---------------------|-------|
| Total | 1,743 | 2,310 |
| In subcategories | 455 (26%) | 1,800+ (78%) |
| In "Other" | 1,288 (74%) | ~500 (22%) |

---

## Known Limitations

1. **HowNet coverage is incomplete** - Many characters only have generic sememes like `character|文字` or `China|中国`

2. **Radical semantics aren't always meaningful** - Some radicals (like 亅 hook) are purely graphical, not semantic

3. **WordNet is English-biased** - The first sense of an English word may not match the Chinese meaning (e.g., "white" → person, not color)

4. **Keyword quality varies** - Dictionary-derived keywords for rare characters can be awkward

5. **Cross-category characters** - Some characters genuinely belong to multiple categories (e.g., 明 "bright" could be Colors, Qualities, or Nature)

---

## Implemented Improvements ✅

### 1. ✅ Radical Anchor (Step 2 in Pipeline)
Uses Kangxi radical meanings for Chinese-native categorization.
- **Coverage**: 65% of all characters (15,127)
- **80+ radicals mapped** to semantic categories with subcategories
- High-yield radicals: 辶 (walk), 宀 (roof), 衤 (clothes), 彳 (step)
- Provides 3-level depth (e.g., Nature > Animals > Fish) for most characters

### 2. ✅ Unihan Semantic Deduplication
Creates meaningful unique keywords instead of mechanical suffixes.
- **Source**: Unicode Unihan `kDefinition` field
- **Word limit**: Max 4 words per keyword
- **Example**: `jade (var)` → `jade ring`, `beautiful jade`, `semicircular jade`

### 3. ✅ Priority Sememe Ordering
Ensures correct categorization when characters have multiple sememes.
- **Plants before Body**: 木 (tree), 花 (flower), 草 (grass) go to Nature > Plants
- **Moral/Abstract before Relations**: 德 (virtue), 道 (way), 奸 (treacherous) go to Abstract > Qualities
- **Function Words**: 如 (if/like) goes to Communication > Language

### 4. ✅ "False Friends" Protection
Handles radicals that don't reliably indicate meaning.
- **Problem**: 女 (woman) radical appears in 妄 (absurd), 奸 (treacherous)
- **Problem**: 心 (heart) radical appears in 德 (virtue), 思 (think)
- **Solution**: Priority sememes catch abstract/moral concepts BEFORE radical anchor runs

## Potential Future Improvements

1. **Curated overrides for common WordNet characters** - The ~4,000 characters (17%) still using WordNet should have the top 100-200 most common ones manually reviewed

2. **Frequency-weighted senses** - Use character frequency data to prefer common meanings

3. **Chinese WordNet (CWN)** - A Chinese equivalent to WordNet, might provide better coverage than translating through English

4. **Semantic Zoom Visualization** - For the UI, implement level-of-detail rendering:
   - Level 0: 7 Root Categories only
   - Level 1: Primary Categories + top 100 characters
   - Level 2: Subcategories + Heisig 3,000
   - Level 3: All 23,000 characters (deep zoom only)

---

## Code Location

**Main script**: `scripts/build_semantic_graph.py`
- `load_extended_data()` - Loads all data sources
- `extend_with_dictionary()` - Generates unique keywords with Unihan deduplication
- `get_semantic_category()` - 5-step categorization pipeline
- `build_semantic_tree()` - Assembles final hierarchy

**Radical mapping**: `scripts/radical_mapping.py`
- `KANGXI_RADICAL_TO_CATEGORY` - 66 radical → category mappings

**Output**: `web-app/static/game_data/hanzi_semantic_graph.json`

**Data sources**:
- Heisig: fetched from GitHub at runtime (~3,036 characters)
- Dictionary: `web-app/static/game_data/char_glosses.json` (~23,000 characters)
- Curated: `web-app/static/game_data/curated_component_names_v2.json` (~1,800 names)
- Unihan: `web-app/static/game_data/unihan_data.json` (~103,000 radicals, ~23,000 definitions)

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    KEYWORD GENERATION                            │
├─────────────────────────────────────────────────────────────────┤
│  1. Heisig (3,036) ──► PROTECTED, never changed                 │
│  2. Curated (1,800) ──► Quality overrides for non-Heisig        │
│  3. Dictionary (19,800) ──► CEDICT definitions                  │
│         │                                                        │
│         ▼                                                        │
│  Uniqueness Check ──► Unihan Semantic Dedup (max 4 words)       │
│         │                  │                                     │
│         ▼                  ▼                                     │
│  Fallback Suffixes    "jade ring", "beautiful jade"             │
│  (ii), (alt), (hex)                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CATEGORIZATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: HowNet Sememes (22%)                                   │
│          ├── Priority Sememes (plants, body, moral, colors)     │
│          ├── Non-Animal Indicators                              │
│          └── Standard Sememe → Category mapping                 │
│                    │                                             │
│                    ▼ (if no match)                               │
│  Step 2: Radical Anchor (65%)                                   │
│          └── 80+ Kangxi radicals → Category+Subcategory         │
│                    │                                             │
│                    ▼ (if no match)                               │
│  Step 3: WordNet Lexname (13%)                                  │
│          └── English semantic lookup                            │
│                    │                                             │
│                    ▼ (if no match)                               │
│  Step 4: WordNet Hypernym Chain                                 │
│          └── Walk up hierarchy for subcategories                │
│                    │                                             │
│                    ▼ (if no match)                               │
│  Step 5: Keyword Pattern Match (<1%)                            │
│          └── Last resort fallback                               │
└─────────────────────────────────────────────────────────────────┘

Result: 87% Chinese-native categorization (HowNet + Radical)
        53% with 3-level subcategories
        100% coverage for top 500 common characters
```

