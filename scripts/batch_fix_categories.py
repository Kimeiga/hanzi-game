#!/usr/bin/env python3
"""Batch fix categorization issues in hanzi_semantic_graph.json"""

import json

# Define moves: char -> new category path
MOVES = {
    # From Objects > Tools > Textiles - actions
    '締': ['Human', 'Actions'],  # conclude
    '弔': ['Human', 'Actions'],  # condole
    '續': ['Human', 'Actions'],  # continue
    '綑': ['Human', 'Actions'],  # coil
    '糺': ['Human', 'Actions'],  # collaborate
    '裂': ['Human', 'Actions', 'Change'],  # crack

    # From Objects > Tools > Clothing - qualities
    '襍': ['Abstract', 'Qualities'],  # blended mixed
    '綿': ['Abstract', 'Qualities'],  # continuous

    # From Objects > Tools > Vehicles - keep as tools/vehicles
    '軸': ['Objects', 'Tools', 'Vehicles'],  # axle - keep
    '車': ['Objects', 'Tools', 'Vehicles'],  # car - keep
    '舟': ['Objects', 'Tools', 'Vehicles'],  # boat - keep
    '幢': ['Objects', 'Tools', 'Vehicles'],  # carriage curtain - keep

    # From Nature > Animals - more actions
    '孕': ['Human', 'Body'],  # pregnant (body state)
    '息': ['Human', 'Actions'],  # rest/breathe
    '養': ['Human', 'Actions'],  # raise/nourish
    '飼': ['Human', 'Actions'],  # feed
    '繁': ['Human', 'Actions'],  # breed
    '育': ['Human', 'Actions'],  # give birth to
    '喂': ['Human', 'Actions'],  # feed
    '餵': ['Human', 'Actions'],  # feed

    # From Human > Relations - more actions
    '侮': ['Human', 'Actions'],  # insult
    '傷': ['Human', 'Actions'],  # injure
    '救': ['Human', 'Actions'],  # save
    '護': ['Human', 'Actions'],  # protect
    '援': ['Human', 'Actions'],  # rescue
    '扶': ['Human', 'Actions'],  # support
    '幫': ['Human', 'Actions'],  # help
    '助': ['Human', 'Actions'],  # assist
    '陪': ['Human', 'Actions'],  # accompany
    '隨': ['Human', 'Actions', 'Movement'],  # follow
    '伴': ['Human', 'Actions'],  # accompany
    '帶': ['Human', 'Actions'],  # lead
    '領': ['Human', 'Actions'],  # lead
    '導': ['Human', 'Actions'],  # guide
    '率': ['Human', 'Actions'],  # lead
    '引': ['Human', 'Actions'],  # lead

    # From Human > Relations - more qualities
    '俊': ['Abstract', 'Qualities'],  # handsome
    '俏': ['Abstract', 'Qualities'],  # pretty
    '俞': ['Abstract', 'Qualities'],  # good
    '佳': ['Abstract', 'Qualities'],  # fine
    '俠': ['Abstract', 'Qualities'],  # chivalrous
    '儒': ['Abstract', 'Qualities'],  # Confucian (quality)
    '僞': ['Abstract', 'Qualities'],  # false

    # From Abstract > Time - more
    '即': ['Abstract', 'Time'],  # immediately - keep
    '將': ['Abstract', 'Time'],  # will/general - keep
    '曾': ['Abstract', 'Time'],  # once - keep
    '已': ['Abstract', 'Time'],  # already - keep
    '既': ['Abstract', 'Time'],  # since - keep
    '初': ['Abstract', 'Time'],  # beginning - keep
    '末': ['Abstract', 'Time'],  # end - keep
    '終': ['Abstract', 'Time'],  # finally - keep
    '始': ['Abstract', 'Time'],  # start - keep

    # From Society > Religion - keep legitimate items
    '佛': ['Society', 'Religion'],  # Buddha - keep
    '神': ['Society', 'Religion'],  # god - keep
    '靈': ['Abstract', 'Miscellaneous'],  # spirit
    '鬼': ['Society', 'Religion'],  # ghost - keep
    '魔': ['Society', 'Religion'],  # demon - keep
    '祭': ['Human', 'Actions'],  # sacrifice (action)
    '拜': ['Human', 'Actions'],  # worship (action)
    '祈': ['Human', 'Actions'],  # pray (action)
    '禱': ['Human', 'Actions'],  # pray (action)

    # From Human > Body - more actions
    '抱': ['Human', 'Actions'],  # hug
    '握': ['Human', 'Actions'],  # grasp
    '拍': ['Human', 'Actions'],  # pat
    '打': ['Human', 'Actions'],  # hit
    '揮': ['Human', 'Actions'],  # wave
    '擺': ['Human', 'Actions'],  # place
    '推': ['Human', 'Actions'],  # push
    '拉': ['Human', 'Actions'],  # pull
    '抬': ['Human', 'Actions'],  # lift
    '舉': ['Human', 'Actions'],  # raise
    '放': ['Human', 'Actions'],  # put/release
    '擲': ['Human', 'Actions'],  # throw
    '投': ['Human', 'Actions'],  # throw
    '接': ['Human', 'Actions'],  # receive
    '掛': ['Human', 'Actions'],  # hang
    '捏': ['Human', 'Actions'],  # pinch
    '搓': ['Human', 'Actions'],  # rub
    '摸': ['Human', 'Actions'],  # touch
    '挖': ['Human', 'Actions'],  # dig
    '掘': ['Human', 'Actions'],  # dig
    '搜': ['Human', 'Actions'],  # search
    '捉': ['Human', 'Actions'],  # catch
    '抓': ['Human', 'Actions'],  # grab
}

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
                removed = node['children'].pop(i)
                return removed, current_path.strip(' > ')
            else:
                result = find_and_remove_char(child, char, current_path)
                if result[0]:
                    return result
    return None, None

def find_category(node, path_parts, idx=0):
    """Find a category node by path."""
    if idx >= len(path_parts):
        return node
    if 'children' in node:
        for child in node['children']:
            if child.get('name') == path_parts[idx]:
                return find_category(child, path_parts, idx + 1)
    return None

def main():
    print("Loading semantic graph...")
    data = load_data()
    
    success = 0
    skipped = 0
    failed = 0
    
    for char, to_path in MOVES.items():
        char_node, from_path = find_and_remove_char(data, char)
        
        if char_node is None:
            print(f"SKIP: {char} not found")
            skipped += 1
            continue
        
        category = find_category(data, to_path)
        if category is None:
            print(f"FAIL: Category {' > '.join(to_path)} not found for {char}")
            failed += 1
            continue
        
        if 'children' not in category:
            category['children'] = []
        category['children'].append(char_node)
        
        print(f"OK: {char} ({char_node.get('keyword', '?')}) : {from_path} -> {' > '.join(to_path)}")
        success += 1
    
    print(f"\nResults: {success} moved, {skipped} skipped, {failed} failed")
    
    if success > 0:
        print("Saving...")
        save_data(data)
        print("Done!")

if __name__ == '__main__':
    main()

