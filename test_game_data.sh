#!/bin/bash

echo "🧪 Testing Game Data Files"
echo "=========================="
echo ""

echo "📊 File Sizes:"
ls -lh game_data/

echo ""
echo "📈 Data Counts:"
echo "  Allowed components: $(jq 'length' game_data/allowed_components.json)"
echo "  Character decompositions: $(jq 'length' game_data/char_to_decomposition.json)"
echo "  Component combinations: $(jq 'length' game_data/components_to_chars.json)"
echo "  HSK levels: $(jq 'keys | length' game_data/hsk_words.json)"

echo ""
echo "🎮 Game Scenario Tests:"
echo ""

echo "Test 1: Character 明 (bright)"
echo "  Decomposition: $(jq -c '.["明"]' game_data/char_to_decomposition.json)"
echo "  Reverse lookup (日月): $(jq -c '.["日月"]' game_data/components_to_chars.json)"

echo ""
echo "Test 2: Character 好 (good)"
echo "  Decomposition: $(jq -c '.["好"]' game_data/char_to_decomposition.json)"
echo "  Reverse lookup (女子): $(jq -c '.["女子"]' game_data/components_to_chars.json)"

echo ""
echo "Test 3: HSK 1 Sample Words (first 20)"
jq -c '.["1"][:20]' game_data/hsk_words.json

echo ""
echo "Test 4: Check if common components are in allowed set"
for comp in "日" "月" "木" "水" "火" "土" "人" "女" "子"; do
  if jq -e --arg c "$comp" 'index($c)' game_data/allowed_components.json > /dev/null; then
    echo "  ✅ $comp is allowed"
  else
    echo "  ❌ $comp is NOT allowed"
  fi
done

echo ""
echo "✅ All tests complete!"

