#!/usr/bin/env python3
"""
Fix categorization issues in hanzi_semantic_graph.json
"""

import json
import copy

# Define the moves: (char, from_path_contains, to_category_path)
MOVES = [
    # Car should be in Vehicles
    ('車', 'Human > Body', ['Objects', 'Tools', 'Vehicles']),
    # 回 (return) should be an action
    ('回', 'Society > Government', ['Human', 'Actions']),
    # 影 (shadow) should be abstract quality
    ('影', 'Society > Government', ['Abstract', 'Qualities']),
    # 差 (fall short) should be abstract quality
    ('差', 'Society > Government', ['Abstract', 'Qualities']),
]

def load_data():
    with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
        return json.load(f)

def save_data(data):
    with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_and_remove_char(node, char, path=''):
    """Find and remove a character node, returning it if found."""
    current_path = path + ' > ' + node.get('name', '') if 'name' in node else path
    
    if 'children' in node:
        for i, child in enumerate(node['children']):
            if 'char' in child and child['char'] == char:
                # Found it - remove and return
                removed = node['children'].pop(i)
                print(f"  Removed {char} from {current_path.strip(' > ')}")
                return removed
            else:
                # Recurse into children
                result = find_and_remove_char(child, char, current_path)
                if result:
                    return result
    return None

def find_category(node, path_parts, current_idx=0):
    """Find a category node by path parts."""
    if current_idx >= len(path_parts):
        return node
    
    target_name = path_parts[current_idx]
    
    if 'children' in node:
        for child in node['children']:
            if child.get('name') == target_name:
                return find_category(child, path_parts, current_idx + 1)
    
    return None

def add_char_to_category(node, path_parts, char_node):
    """Add a character node to the specified category."""
    category = find_category(node, path_parts)
    if category is None:
        print(f"  ERROR: Category not found: {' > '.join(path_parts)}")
        return False
    
    if 'children' not in category:
        category['children'] = []
    
    category['children'].append(char_node)
    print(f"  Added {char_node['char']} to {' > '.join(path_parts)}")
    return True

def main():
    print("Loading semantic graph...")
    data = load_data()
    
    print(f"\nProcessing {len(MOVES)} character moves...\n")
    
    success_count = 0
    for char, from_hint, to_path in MOVES:
        print(f"Moving {char} ({from_hint} -> {' > '.join(to_path)})")
        
        # Remove from current location
        char_node = find_and_remove_char(data, char)
        
        if char_node is None:
            print(f"  WARNING: Character {char} not found!")
            continue
        
        # Add to new location
        if add_char_to_category(data, to_path, char_node):
            success_count += 1
        else:
            print(f"  ERROR: Failed to add {char} to new location!")
    
    print(f"\nSuccessfully moved {success_count}/{len(MOVES)} characters")
    
    print("\nSaving updated semantic graph...")
    save_data(data)
    print("Done!")

if __name__ == '__main__':
    main()

