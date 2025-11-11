# Chinese Character Game - CLI Tool

This CLI tool allows you to test the game logic step-by-step in the terminal. It uses the **exact same TypeScript code** as the web app, ensuring that tests validate the real game logic.

## Features

- ✅ **Same Code**: Uses the same `gameLogic.ts` and `types.ts` as the web app
- 💾 **Persistent State**: Each game is saved to a JSON file
- 🎮 **Step-by-Step**: Execute one move at a time and inspect the state
- 🧪 **Testable**: Perfect for writing automated tests
- 📊 **Visual Output**: Clear display of game state after each action

## Installation

The CLI is already set up! Just make sure you've installed dependencies:

```bash
cd my-app
pnpm install
```

## Commands

### Create a New Game

```bash
pnpm cli new [game-id]
```

Example:
```bash
pnpm cli new test1
```

This creates a new game with a random HSK 1 word and saves it to `.games/test1.json`.

### Show Game State

```bash
pnpm cli show <game-id>
```

Example:
```bash
pnpm cli show test1
```

Displays the current state of the game including:
- Target word
- Available cards
- Selected cards
- Possible combinations
- Attempts left

### Select Cards

```bash
pnpm cli select <game-id> <card-indices>
```

Example:
```bash
pnpm cli select test1 0,1,2
```

Select cards by their index (comma-separated). The tool will automatically show possible combinations.

### Combine Cards

```bash
pnpm cli combine <game-id> <character>
```

Example:
```bash
pnpm cli combine test1 明
```

Combines the currently selected cards into the specified character. The selected cards are removed and replaced with the new character card.

### Decompose a Card

```bash
pnpm cli decompose <game-id> <card-index>
```

Example:
```bash
pnpm cli decompose test1 0
```

Decomposes a non-leaf character card back into its components.

### Submit Answer

```bash
pnpm cli submit <game-id>
```

Example:
```bash
pnpm cli submit test1
```

Submits the current cards as your answer. If correct, moves to the next round. If incorrect, decreases attempts.

### Reset Game

```bash
pnpm cli reset <game-id>
```

Example:
```bash
pnpm cli reset test1
```

Resets the game to a new random word.

## Example Gameplay Session

```bash
# Start a new game
pnpm cli new mygame

# Output shows:
# Target: Word: 大學
# Available cards: [0] 大, [1] 𦥯, [2] 子

# Select cards 1 and 2
pnpm cli select mygame 1,2

# Output shows:
# Possible combinations: 學

# Combine them into 學
pnpm cli combine mygame 學

# Output shows:
# Available cards: [0] 大, [1] 學

# Submit the answer
pnpm cli submit mygame

# Output shows:
# 🎉 CORRECT! Moving to next round...
```

## Game State Files

Game states are saved in `my-app/.games/` as JSON files. Each file contains:

```json
{
  "gameId": "test1",
  "createdAt": "2025-11-01T20:23:34.572Z",
  "lastModified": "2025-11-01T20:24:03.765Z",
  "currentLevel": 1,
  "roundsPerLevel": 2,
  "currentRound": 1,
  "totalRoundsCompleted": 0,
  "targetWord": "大學",
  "targetGloss": "Word: 大學",
  "availableCards": [...],
  "selectedCards": [...],
  "possibleCombinations": [...],
  "attemptsLeft": 3,
  "maxAttempts": 3,
  "gameOver": false,
  "won": false
}
```

## Automated Testing

Run the automated test suite:

```bash
pnpm test:game
```

This runs a series of tests that verify:
- ✅ Basic card combination
- ✅ Card decomposition
- ✅ Answer checking
- ✅ Word decomposition
- ✅ Full game flow

All tests use the same game logic as the web app!

## Writing Your Own Tests

You can create test scripts that use the CLI programmatically:

```typescript
import { execSync } from 'child_process';

// Create a new game
execSync('pnpm cli new test1');

// Select cards
execSync('pnpm cli select test1 0,1');

// Combine
execSync('pnpm cli combine test1 明');

// Submit
const output = execSync('pnpm cli submit test1').toString();

// Check if it passed
if (output.includes('CORRECT')) {
  console.log('Test passed!');
}
```

Or import the game logic directly:

```typescript
import { loadGameData, combineCards } from './src/lib/gameLogic.js';

const data = await loadGameData();
// ... test the functions directly
```

## Card Symbols

- 🌿 = Leaf component (cannot be decomposed further)
- 🔧 = Composite character (can be decomposed)

## Tips

1. **Use descriptive game IDs** for different test scenarios
2. **Check the `.games/` folder** to inspect saved states
3. **Run `show` after each command** to see the updated state
4. **Use the test suite** as examples for writing your own tests

## Architecture

```
my-app/
├── src/
│   ├── lib/
│   │   ├── types.ts          # Shared type definitions
│   │   └── gameLogic.ts      # Shared game logic (used by both web & CLI)
│   ├── cli/
│   │   ├── game-cli.ts       # CLI tool
│   │   └── test-game.ts      # Automated tests
│   └── routes/
│       └── +page.svelte      # Web UI (uses same gameLogic.ts)
├── static/
│   └── game_data/            # Game data JSON files
└── .games/                   # Saved game states (gitignored)
```

The key insight is that **both the web app and CLI use the exact same `gameLogic.ts` file**, so testing the CLI validates the web app's logic!

