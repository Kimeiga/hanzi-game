# Testing Guide for Chinese Character Game

This guide explains how to test the game logic using the CLI tool and automated tests.

## Why This Approach?

✅ **Same Code**: The CLI uses the exact same TypeScript files (`gameLogic.ts`, `types.ts`) as the web app  
✅ **Step-by-Step**: Execute one move at a time and inspect the state  
✅ **Persistent**: Game states are saved to JSON files  
✅ **Testable**: Easy to write automated tests  
✅ **No Duplication**: Tests validate the real game logic, not a copy  

## Architecture

```
my-app/
├── src/
│   ├── lib/
│   │   ├── types.ts          ← Shared types (web + CLI)
│   │   └── gameLogic.ts      ← Shared logic (web + CLI)
│   ├── cli/
│   │   ├── game-cli.ts       ← CLI tool
│   │   ├── test-game.ts      ← Automated tests
│   │   └── example-test.sh   ← Example bash test
│   └── routes/
│       └── +page.svelte      ← Web UI (imports gameLogic.ts)
└── .games/                   ← Saved game states
```

## Testing Methods

### 1. Manual CLI Testing

Test the game interactively:

```bash
# Create a game
pnpm cli new test1

# Play step by step
pnpm cli select test1 0,1
pnpm cli combine test1 明
pnpm cli submit test1

# Inspect state at any time
pnpm cli show test1
cat .games/test1.json
```

**Use Case**: Manual testing, debugging, understanding game flow

### 2. Automated TypeScript Tests

Run the test suite:

```bash
pnpm test:game
```

This runs `src/cli/test-game.ts` which tests:
- Basic card combination
- Card decomposition
- Answer checking
- Word decomposition
- Full game flow

**Use Case**: Continuous integration, regression testing

### 3. Shell Script Tests

Run the example bash test:

```bash
cd my-app
./src/cli/example-test.sh
```

**Use Case**: Integration testing, CI/CD pipelines

### 4. Programmatic Testing

Import the game logic directly in your tests:

```typescript
import { loadGameData, combineCards } from './src/lib/gameLogic.js';
import * as fs from 'fs';

// Load game data
const data = JSON.parse(
  fs.readFileSync('./static/game_data/char_to_decomposition.json', 'utf-8')
);

// Test directly
const cards = [
  { id: '1', character: '日', isLeaf: true },
  { id: '2', character: '月', isLeaf: true }
];

const newCards = combineCards(cards, '明', cards, data);
console.assert(newCards.length === 1);
console.assert(newCards[0].character === '明');
```

**Use Case**: Unit testing specific functions

## Test Scenarios

### Scenario 1: Test Basic Combination

```bash
pnpm cli new combo-test
pnpm cli select combo-test 0,1
# Check if combinations appear
pnpm cli show combo-test
```

### Scenario 2: Test Decomposition

```bash
pnpm cli new decomp-test
# Find a composite character (🔧)
pnpm cli decompose decomp-test 0
# Verify it breaks into components
pnpm cli show decomp-test
```

### Scenario 3: Test Full Game Flow

```bash
pnpm cli new flow-test
# Play through a complete round
pnpm cli select flow-test 0,1
pnpm cli combine flow-test 明
pnpm cli submit flow-test
# Should move to next round or show error
```

### Scenario 4: Test Error Handling

```bash
pnpm cli new error-test
# Try invalid operations
pnpm cli decompose error-test 999  # Invalid index
pnpm cli combine error-test 明     # No cards selected
```

## Writing Your Own Tests

### Example: Test a Specific Word

```typescript
// test-specific-word.ts
import { getComponentsForWord, createCardsFromComponents } from './src/lib/gameLogic.js';
import * as fs from 'fs';

const data = JSON.parse(
  fs.readFileSync('./static/game_data/char_to_decomposition.json', 'utf-8')
);

const word = '明天';
const components = getComponentsForWord(word, data);
const cards = createCardsFromComponents(components, data);

console.log(`Word: ${word}`);
console.log(`Components: ${components.join(', ')}`);
console.log(`Cards: ${cards.map(c => c.character).join(', ')}`);

// Verify we have the right components
console.assert(components.includes('日'));
console.assert(components.includes('月'));
```

### Example: Test Answer Validation

```typescript
// test-answer-validation.ts
import { checkAnswer } from './src/lib/gameLogic.js';

const testCases = [
  {
    cards: [
      { id: '1', character: '大', isLeaf: true },
      { id: '2', character: '學', isLeaf: false }
    ],
    target: '大學',
    expected: true
  },
  {
    cards: [
      { id: '1', character: '大', isLeaf: true },
      { id: '2', character: '小', isLeaf: true }
    ],
    target: '大學',
    expected: false
  }
];

testCases.forEach((test, i) => {
  const result = checkAnswer(test.cards, test.target);
  console.assert(
    result === test.expected,
    `Test ${i + 1} failed: expected ${test.expected}, got ${result}`
  );
});

console.log('✅ All answer validation tests passed!');
```

## Debugging Tips

### 1. Inspect Game State

```bash
# Pretty print the game state
cat .games/test1.json | jq

# Check specific fields
cat .games/test1.json | jq '.availableCards'
cat .games/test1.json | jq '.selectedCards'
cat .games/test1.json | jq '.possibleCombinations'
```

### 2. Trace Game Flow

```bash
# Create a game and trace each step
pnpm cli new trace-test > step1.txt
pnpm cli select trace-test 0,1 > step2.txt
pnpm cli combine trace-test 明 > step3.txt
pnpm cli submit trace-test > step4.txt

# Compare states
diff step1.txt step2.txt
```

### 3. Test Edge Cases

```bash
# Empty selection
pnpm cli new edge1
pnpm cli submit edge1  # Should fail

# Invalid combination
pnpm cli new edge2
pnpm cli select edge2 0,1
pnpm cli combine edge2 不存在  # Should fail

# Decompose leaf
pnpm cli new edge3
pnpm cli decompose edge3 0  # Should fail if card 0 is a leaf
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
name: Test Game Logic

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: pnpm test:game
```

## Best Practices

1. **Use descriptive game IDs** for different test scenarios
2. **Save game states** for regression testing
3. **Test both success and failure paths**
4. **Verify state changes** after each operation
5. **Clean up test games** periodically (`rm .games/test-*`)

## Common Issues

### Issue: "Game not found"
**Solution**: Make sure you created the game first with `pnpm cli new <game-id>`

### Issue: "No cards selected"
**Solution**: Run `pnpm cli select <game-id> <indices>` before combining

### Issue: "Cannot decompose leaf component"
**Solution**: Only composite characters (🔧) can be decomposed, not leaf components (🌿)

## Next Steps

1. Run the automated tests: `pnpm test:game`
2. Try the CLI: `pnpm cli new mygame`
3. Write your own tests using the examples above
4. Integrate into your CI/CD pipeline

Happy testing! 🧪

