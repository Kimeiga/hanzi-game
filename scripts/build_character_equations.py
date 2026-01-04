#!/usr/bin/env python3
"""Build character equations from decomposition data."""
import json
from typing import Optional

# Load data
with open('web-app/static/game_data/char_to_decomposition.json', 'r') as f:
    decomp = json.load(f)

with open('web-app/static/game_data/component_glosses.json', 'r') as f:
    glosses = json.load(f)

# IDS operators to remove from display
IDS_OPERATORS = set('⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻⿼⿽⿾⿿')


def get_gloss(char: str) -> str:
    """Get the gloss for a character/component."""
    if char in glosses:
        return glosses[char]
    return ''


def build_equation(char: str, include_glosses: bool = True) -> Optional[str]:
    """
    Build an equation for a character.
    
    Example: 明 = 日(sun) + 月(moon)
    """
    if char not in decomp:
        return None
    
    data = decomp[char]
    components = data.get('components', [])
    
    if not components:
        return None
    
    # Build equation parts
    parts = []
    for comp in components:
        if comp in IDS_OPERATORS:
            continue
        
        gloss = get_gloss(comp) if include_glosses else ''
        if gloss:
            parts.append(f'{comp}({gloss})')
        else:
            parts.append(comp)
    
    if not parts:
        return None
    
    char_gloss = get_gloss(char)
    if include_glosses and char_gloss:
        return f'{char}({char_gloss}) = ' + ' + '.join(parts)
    else:
        return f'{char} = ' + ' + '.join(parts)


def build_all_equations(chars: list, include_glosses: bool = True) -> dict:
    """Build equations for a list of characters."""
    equations = {}
    for char in chars:
        eq = build_equation(char, include_glosses)
        if eq:
            equations[char] = eq
    return equations


def build_equation_data(char: str) -> Optional[dict]:
    """
    Build structured equation data for a character.

    Returns: {
        'char': '明',
        'gloss': 'bright/clear',
        'components': [
            {'char': '日', 'gloss': 'day'},
            {'char': '月', 'gloss': 'month'}
        ],
        'equation': '明(bright/clear) = 日(day) + 月(month)'
    }
    """
    if char not in decomp:
        return None

    data = decomp[char]
    components = data.get('components', [])

    if not components:
        return None

    char_gloss = get_gloss(char)
    component_data = []

    for comp in components:
        if comp in IDS_OPERATORS:
            continue
        comp_gloss = get_gloss(comp)
        component_data.append({
            'char': comp,
            'gloss': comp_gloss
        })

    if not component_data:
        return None

    return {
        'char': char,
        'gloss': char_gloss,
        'components': component_data,
        'equation': build_equation(char, include_glosses=True)
    }


# Test and build output
if __name__ == '__main__':
    test_chars = ['明', '好', '休', '林', '森', '男', '女', '安', '家', '學']

    print('=== Character Equations ===\n')
    for char in test_chars:
        eq = build_equation(char)
        if eq:
            print(eq)
        else:
            print(f'{char}: No decomposition available')

    print('\n=== Building equations for all characters ===')

    # Build equations for all characters in decomposition data
    all_equations = {}
    for char in decomp.keys():
        eq_data = build_equation_data(char)
        if eq_data:
            all_equations[char] = eq_data

    print(f'Total characters with equations: {len(all_equations)}')

    # Save to file
    output_file = 'web-app/static/game_data/character_equations.json'
    with open(output_file, 'w') as f:
        json.dump(all_equations, f, ensure_ascii=False, indent=2)
    print(f'Saved to {output_file}')

