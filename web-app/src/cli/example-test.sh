#!/bin/bash

# Example: Automated test script using the CLI
# This demonstrates how to test game logic step-by-step

set -e  # Exit on error

GAME_ID="automated-test-$(date +%s)"

echo "🧪 Starting automated test with game ID: $GAME_ID"
echo ""

# Create a new game
echo "1️⃣ Creating new game..."
pnpm cli new "$GAME_ID" > /tmp/game_output.txt
cat /tmp/game_output.txt

# Extract target word from output
TARGET=$(grep "Target:" /tmp/game_output.txt | sed 's/.*Word: //')
echo ""
echo "🎯 Target word: $TARGET"
echo ""

# Show initial state
echo "2️⃣ Initial state:"
pnpm cli show "$GAME_ID"
echo ""

# Try selecting first two cards
echo "3️⃣ Selecting cards 0,1..."
pnpm cli select "$GAME_ID" 0,1 > /tmp/game_output.txt
cat /tmp/game_output.txt
echo ""

# Check if there are possible combinations
if grep -q "POSSIBLE COMBINATIONS:" /tmp/game_output.txt; then
    echo "✅ Found possible combinations!"
    COMBO=$(grep -A 1 "POSSIBLE COMBINATIONS:" /tmp/game_output.txt | tail -1 | sed 's/.*\[0\] //')
    echo "   First combination: $COMBO"
    echo ""
    
    # Try combining
    echo "4️⃣ Combining into: $COMBO"
    pnpm cli combine "$GAME_ID" "$COMBO"
    echo ""
else
    echo "ℹ️  No combinations found for cards 0,1"
    echo ""
fi

# Show current state
echo "5️⃣ Current state:"
pnpm cli show "$GAME_ID"
echo ""

# Try submitting
echo "6️⃣ Submitting answer..."
pnpm cli submit "$GAME_ID" > /tmp/game_output.txt
cat /tmp/game_output.txt
echo ""

# Check result
if grep -q "CORRECT" /tmp/game_output.txt; then
    echo "✅ TEST PASSED: Answer was correct!"
    exit 0
elif grep -q "Incorrect" /tmp/game_output.txt; then
    echo "ℹ️  TEST RESULT: Answer was incorrect (this is expected for random games)"
    echo "   This demonstrates the game logic is working correctly."
    exit 0
else
    echo "❌ TEST FAILED: Unexpected output"
    exit 1
fi

