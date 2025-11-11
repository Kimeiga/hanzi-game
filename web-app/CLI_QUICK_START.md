# CLI Quick Start Guide

## 🚀 Quick Commands

```bash
# Create new game
pnpm cli new test1

# Show current state
pnpm cli show test1

# Select cards (by index)
pnpm cli select test1 0,1

# Combine selected cards
pnpm cli combine test1 明

# Decompose a card
pnpm cli decompose test1 0

# Submit answer
pnpm cli submit test1

# Run automated tests
pnpm test:game
```

## 📝 Example Session

```bash
# 1. Start new game
$ pnpm cli new demo

🎮 Creating new game: demo
Target: Word: 大學
Available cards:
  [0] 大 🌿
  [1] 𦥯 🌿
  [2] 子 🌿

# 2. Select cards 1 and 2
$ pnpm cli select demo 1,2

Selected cards: 𦥯, 子
Possible combinations: 學

# 3. Combine into 學
$ pnpm cli combine demo 學

Available cards:
  [0] 大 🌿
  [1] 學 🔧

# 4. Submit answer
$ pnpm cli submit demo

🎉 CORRECT! Moving to next round...
```

## 🧪 Testing Workflow

```bash
# Run all automated tests
pnpm test:game

# Create a test game
pnpm cli new mytest

# Play through it step by step
pnpm cli show mytest
pnpm cli select mytest 0,1
pnpm cli combine mytest 明
pnpm cli submit mytest

# Check the saved state
cat .games/mytest.json
```

## 💡 Tips

- **Card indices start at 0**
- **Leaf components (🌿) cannot be decomposed**
- **Composite characters (🔧) can be decomposed**
- **Game states are saved in `.games/` folder**
- **Use descriptive game IDs for different test scenarios**

## 🔍 Debugging

```bash
# View saved game state
cat .games/test1.json | jq

# List all saved games
ls -la .games/

# Show game state after each command
pnpm cli show test1
```

