# Chinese Word Game - Game Data Documentation

## Overview

This document describes the game data structures generated for the Chinese character composition game.

## Game Concept

Players are given:
- A set of character subcomponents (radicals/parts)
- An English gloss (definition)

They must figure out how to combine the subcomponents to build the characters that form the word corresponding to the gloss.

## Generated Data Files

All files are located in the `game_data/` directory:

### 1. `char_to_decomposition.json` (3.1 MB)
**Purpose:** Maps each character to its IDS decomposition and immediate components.

**Structure:**
```json
{
  "明": {
    "character": "明",
    "ids": "⿰日月",
    "components": ["日", "月"]
  }
}
```

**Details:**
- Contains 27,150 character decompositions
- IDS operators (⿰, ⿱, etc.) describe spatial arrangement:
  - ⿰ = left-right (e.g., 明 = 日⿰月)
  - ⿱ = top-bottom
  - ⿲ = left-middle-right
  - ⿳ = top-middle-bottom
  - And more...
- Components are the immediate parts (not recursively decomposed)

### 2. `components_to_chars.json` (769 KB)
**Purpose:** Reverse mapping - given a set of components, what characters can be formed?

**Structure:**
```json
{
  "日月": ["明"]
}
```

**Details:**
- Contains 26,633 component combinations
- Components are sorted alphabetically to create consistent keys
- Values are arrays because multiple characters can share the same components
- **Critical for gameplay:** When player selects components, look up possible characters

**Example usage in game:**
```javascript
// Player selects: 日, 月
const sortedComponents = ["日", "月"].sort().join(""); // "日月"
const possibleChars = componentsToChars[sortedComponents]; // ["明"]
```

### 3. `allowed_components.json` (5.2 KB)
**Purpose:** Set of all leaf components that appear in HSK words.

**Structure:**
```json
[
  "日",
  "月",
  "木",
  "水",
  ...
]
```

**Details:**
- Contains 580 unique leaf components
- These are the "atomic" building blocks - components that cannot be further decomposed
- Extracted by recursively decomposing all characters in HSK 1-7 words
- **Use this to limit the component palette** shown to players

**How leaf components are determined:**
1. Start with a character (e.g., 學)
2. Look up its IDS decomposition: ⿱𦥯子
3. Extract components: [𦥯, 子]
4. Recursively decompose each component
5. Continue until reaching components with no IDS entry (leaves)
6. Add all leaves to the set

### 4. `hsk_words.json` (1.4 MB)
**Purpose:** Words organized by HSK level for progressive difficulty.

**Structure:**
```json
{
  "1": ["一", "七", "三", "上", "下", ...],
  "2": [...],
  ...
  "7": [...]
}
```

**Details:**
- HSK 1: 4,394 words (easiest)
- HSK 2: 9,835 words
- HSK 3: 14,237 words
- HSK 4: 13,568 words
- HSK 5: 9,984 words
- HSK 6: 12,167 words
- HSK 7: 28,106 words (hardest)
- Total: 92,291 words with defined HSK levels

**Game progression:**
- Start with HSK 1 words for beginners
- Progress through levels as player improves
- Each level introduces more complex characters and vocabulary

## Data Statistics

### HSK Coverage
- **Words with HSK levels:** 92,291 (63.4% of dictionary)
- **Words without HSK:** 53,289 (36.6% of dictionary)
- **Total words in dictionary:** 145,580

### Character Decomposition
- **Characters with IDS data:** 27,150
- **Unique component combinations:** 26,633
- **Leaf components in HSK words:** 580

### Character Statistics
- **Characters with HSK levels:** 2,915 (3.1% of dictionary)
- **Characters without HSK:** 90,821 (96.9% of dictionary)
- **Total characters in dictionary:** 93,736

## Game Implementation Guide

### Level Selection
```javascript
// Get words for a specific HSK level
const level = 1; // Start with HSK 1
const words = hskWords[level.toString()];
```

### Component Palette
```javascript
// Show only allowed components to player
const componentPalette = allowedComponents;
// Display these as selectable tiles/buttons
```

### Character Lookup
```javascript
// Player selects components: ["日", "月"]
const selected = ["日", "月"].sort().join("");
const possibleChars = componentsToChars[selected];
// possibleChars = ["明"]
```

### Decomposition Display
```javascript
// Show how a character breaks down
const char = "明";
const decomp = charToDecomposition[char];
// decomp.ids = "⿰日月"
// decomp.components = ["日", "月"]
```

### Recursive Decomposition (for hints)
```javascript
// Show full decomposition tree
function getLeafComponents(char) {
  const decomp = charToDecomposition[char];
  if (!decomp) return [char]; // Leaf node
  
  const leaves = [];
  for (const component of decomp.components) {
    leaves.push(...getLeafComponents(component));
  }
  return leaves;
}

// Example: getLeafComponents("學") might return ["臼", "冖", "子", ...]
```

## Rendering Components

For components that don't display properly, use GlyphWiki:

```javascript
function charToGlyphWikiUrl(char, format = 'svg') {
  const codepoint = char.codePointAt(0);
  const glyphName = 'u' + codepoint.toString(16).toLowerCase();
  return `https://glyphwiki.org/glyph/${glyphName}.${format}`;
}

// Example: charToGlyphWikiUrl("𦥯") 
// → "https://glyphwiki.org/glyph/u26969.svg"
```

## Notes

- IDS operators (⿰, ⿱, etc.) are filtered out from components
- Components are sorted alphabetically for consistent lookup keys
- Some characters may have multiple valid decompositions
- Not all characters in the dictionary have IDS data
- The 580 allowed components cover all HSK 1-7 words

## Future Enhancements

Potential additions:
- English glosses for each word (from dictionary)
- Pinyin pronunciations
- Character frequency data
- Stroke count information
- Radical information
- Example sentences

