#!/bin/bash

# Interactive script to explore game data

if [ $# -eq 0 ]; then
    echo "🎮 Chinese Word Game - Data Explorer"
    echo "===================================="
    echo ""
    echo "Usage:"
    echo "  $0 decompose <character>    - Show how a character decomposes"
    echo "  $0 lookup <components>      - Find characters from components (e.g., '日月')"
    echo "  $0 hsk <level>              - Show words for HSK level (1-7)"
    echo "  $0 stats                    - Show data statistics"
    echo "  $0 components               - List all allowed components"
    echo ""
    echo "Examples:"
    echo "  $0 decompose 明"
    echo "  $0 lookup 日月"
    echo "  $0 hsk 1"
    exit 0
fi

COMMAND=$1
shift

case $COMMAND in
    decompose)
        if [ -z "$1" ]; then
            echo "Error: Please provide a character"
            exit 1
        fi
        CHAR=$1
        echo "🔍 Decomposition of '$CHAR':"
        jq --arg c "$CHAR" '.[$c]' game_data/char_to_decomposition.json
        ;;
    
    lookup)
        if [ -z "$1" ]; then
            echo "Error: Please provide components (e.g., 日月)"
            exit 1
        fi
        COMPONENTS=$1
        echo "🔍 Characters that can be formed from '$COMPONENTS':"
        jq --arg c "$COMPONENTS" '.[$c]' game_data/components_to_chars.json
        ;;
    
    hsk)
        if [ -z "$1" ]; then
            echo "Error: Please provide HSK level (1-7)"
            exit 1
        fi
        LEVEL=$1
        echo "📚 HSK Level $LEVEL words (first 50):"
        jq --arg l "$LEVEL" '.[$l][:50]' game_data/hsk_words.json
        echo ""
        echo "Total words at this level:"
        jq --arg l "$LEVEL" '.[$l] | length' game_data/hsk_words.json
        ;;
    
    stats)
        echo "📊 Game Data Statistics"
        echo "======================="
        echo ""
        echo "Allowed components: $(jq 'length' game_data/allowed_components.json)"
        echo "Character decompositions: $(jq 'length' game_data/char_to_decomposition.json)"
        echo "Component combinations: $(jq 'length' game_data/components_to_chars.json)"
        echo ""
        echo "HSK Words by Level:"
        for i in {1..7}; do
            count=$(jq --arg l "$i" '.[$l] | length' game_data/hsk_words.json)
            echo "  HSK $i: $count words"
        done
        ;;
    
    components)
        echo "🧩 Allowed Components (580 total):"
        jq -r '.[]' game_data/allowed_components.json | head -100
        echo ""
        echo "(Showing first 100 components. Total: 580)"
        ;;
    
    *)
        echo "Error: Unknown command '$COMMAND'"
        echo "Run '$0' without arguments to see usage"
        exit 1
        ;;
esac

