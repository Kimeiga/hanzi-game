# Chinese Word Game - Character Composition Game

A game where players learn Chinese characters by building them from their component parts.

## Game Concept

Players are given:
- **A set of character subcomponents** (radicals/parts) to choose from
- **An English gloss** (definition) as a hint

They must figure out how to combine the subcomponents to build the characters that form the word corresponding to the gloss.

## Project Structure

```
chinese-word-game/
├── src/
│   ├── main.rs                    # Main program - HSK analysis & game data generation
│   ├── chinese_types.rs           # Chinese word dictionary types
│   ├── chinese_char_types.rs      # Chinese character dictionary types
│   └── game_data_builder.rs       # Game data generation logic
├── game_data/                     # Generated game data (gitignored)
│   ├── char_to_decomposition.json # Character → components mapping
│   ├── components_to_chars.json   # Components → character mapping (reverse)
│   ├── allowed_components.json    # Set of all leaf components
│   └── hsk_words.json             # Words organized by HSK level
├── ids/                           # IDS (Ideographic Description Sequence) data
│   ├── IDS-UCS-Basic.txt         # ~20,568 basic character decompositions
│   └── IDS-UCS-Ext-A.txt         # ~6,582 extended character decompositions
├── chinese_dictionary_word_2025-06-25.jsonl   # Word dictionary (145,580 words)
├── chinese_dictionary_char_2025-06-25.jsonl   # Character dictionary (93,736 chars)
├── test_game_data.sh             # Test script for game data
├── explore_game_data.sh          # Interactive data explorer
├── GAME_DATA_README.md           # Detailed game data documentation
└── README.md                     # This file
```

## Quick Start

### 1. Generate Game Data

```bash
cargo run
```

This will:
- Analyze HSK levels in the dictionary
- Extract words with defined HSK levels (1-7)
- Load IDS decomposition data
- Build character decomposition mappings
- Create reverse lookup (components → characters)
- Extract all leaf components from HSK words
- Save everything to `game_data/` directory

### 2. Explore the Data

```bash
# Show statistics
./explore_game_data.sh stats

# Decompose a character
./explore_game_data.sh decompose 明

# Find characters from components
./explore_game_data.sh lookup 日月

# Show HSK level 1 words
./explore_game_data.sh hsk 1

# List allowed components
./explore_game_data.sh components
```

### 3. Run Tests

```bash
./test_game_data.sh
```

## Game Data Summary

### HSK Coverage
- **HSK 1:** 4,394 words (easiest - beginner level)
- **HSK 2:** 9,835 words
- **HSK 3:** 14,237 words
- **HSK 4:** 13,568 words
- **HSK 5:** 9,984 words
- **HSK 6:** 12,167 words
- **HSK 7:** 28,106 words (hardest - advanced level)
- **Total:** 92,291 words with HSK levels

### Component Data
- **Allowed components:** 580 unique leaf components
- **Character decompositions:** 27,150 characters
- **Component combinations:** 26,633 unique combinations

## How It Works

### Character Decomposition

Characters are decomposed using IDS (Ideographic Description Sequences):

```
明 (bright) = ⿰日月
  ⿰ = left-right composition operator
  日 = sun (left component)
  月 = moon (right component)
```

### Recursive Decomposition to Leaf Components

The system recursively decomposes characters until reaching "leaf" components (components that cannot be further decomposed):

```
學 (study)
  ↓ IDS: ⿱𦥯子
  ├─ 𦥯 (臼 + 冖 + ...)
  └─ 子 (leaf component)
```

### Component Set for Game

The **allowed_components** set contains all 580 leaf components that appear in HSK 1-7 words. This ensures:
- Players only see components relevant to their learning level
- All HSK words can be constructed from the available components
- The component palette is manageable (not overwhelming)

## Example Game Flow

1. **Select Level:** Player chooses HSK 1 (beginner)
2. **Get Word:** System picks a random HSK 1 word, e.g., "明" (bright)
3. **Show Gloss:** Display English definition: "bright, clear,明白"
4. **Show Components:** Display available components including 日 and 月
5. **Player Builds:** Player selects 日 and 月
6. **Lookup:** System checks `components_to_chars["日月"]` → finds "明"
7. **Verify:** Check if "明" matches the target word
8. **Success!** Player learns that 明 = 日 + 月

## Data Files Explained

### 1. char_to_decomposition.json
Maps each character to its decomposition:
```json
{
  "明": {
    "character": "明",
    "ids": "⿰日月",
    "components": ["日", "月"]
  }
}
```

### 2. components_to_chars.json
Reverse lookup - components to possible characters:
```json
{
  "日月": ["明"]
}
```

**Note:** Components are sorted alphabetically for consistent keys.

### 3. allowed_components.json
Set of all leaf components:
```json
["日", "月", "木", "水", "火", "土", ...]
```

### 4. hsk_words.json
Words organized by HSK level:
```json
{
  "1": ["一", "七", "三", "上", "下", ...],
  "2": [...],
  ...
}
```

## Rendering Non-Displayable Characters

Some components may not display properly on all systems. Use GlyphWiki to render them:

```javascript
function charToGlyphWikiUrl(char, format = 'svg') {
  const codepoint = char.codePointAt(0);
  const glyphName = 'u' + codepoint.toString(16).toLowerCase();
  return `https://glyphwiki.org/glyph/${glyphName}.${format}`;
}

// Example: 𦥯 → https://glyphwiki.org/glyph/u26969.svg
```

## IDS Operators Reference

Common IDS operators used in decompositions:

- `⿰` - Left-right (e.g., 明 = ⿰日月)
- `⿱` - Top-bottom (e.g., 字 = ⿱宀子)
- `⿲` - Left-middle-right (e.g., 辦 = ⿲辛力辛)
- `⿳` - Top-middle-bottom
- `⿴` - Surround
- `⿵` - Surround from above
- `⿶` - Surround from below
- `⿷` - Surround from left
- `⿸` - Surround from upper left
- `⿹` - Surround from upper right
- `⿺` - Surround from lower left
- `⿻` - Overlaid

These operators are filtered out when extracting components for the game.

## Development

### Build
```bash
cargo build
```

### Run
```bash
cargo run
```

### Clean
```bash
cargo clean
rm -rf game_data/
```

## Dependencies

- `anyhow` - Error handling
- `serde` - Serialization/deserialization
- `serde_json` - JSON support

## License

Data sources:
- Chinese dictionary: CC-CEDICT
- IDS data: Unicode IDS Database
- HSK levels: Integrated from various sources

## Future Enhancements

- [ ] Add English glosses to game data
- [ ] Include pinyin pronunciations
- [ ] Add character frequency data
- [ ] Include stroke count information
- [ ] Add example sentences
- [ ] Create web-based game interface
- [ ] Add progressive hints system
- [ ] Track player progress and statistics

