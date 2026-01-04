#!/usr/bin/env python3
"""
Fix slashed keywords:
- Remove slashes from same-reading characters (pick most concrete meaning)
- Keep slashes only for true 多音字 (multiple Chinese readings)
"""
import json

# True 多音字 - characters with genuinely different readings
# These SHOULD keep slashes or have reading-specific keywords
MULTI_READING_CHARS = {
    '行', '了', '得', '着', '长', '重', '还', '地', '干', '乐', '少', '为',
    '便', '分', '好', '的', '种', '没', '数', '觉', '角', '发', '处', '朝',
    '倒', '弹', '担', '答', '藏', '称', '差', '传', '创', '度', '缝', '更',
    '供', '观', '冠', '横', '划', '会', '几', '假', '间', '将', '降', '教',
    '结', '解', '禁', '尽', '卷', '看', '壳', '空', '累', '量', '露', '落',
    '蒙', '磨', '难', '宁', '胖', '迫', '铺', '曲', '塞', '散', '丧', '舍',
    '省', '识', '似', '宿', '调', '挑', '吐', '喂', '系', '鲜', '相', '兴',
    '削', '血', '压', '应', '与', '载', '扎', '占', '涨', '折', '正', '只',
    '中', '转', '著', '奔', '薄', '泊', '参', '颤', '称', '乘', '澄', '冲',
    '臭', '畜', '揣', '攒', '当', '都', '逗', '恶', '否', '服', '夫', '佛',
}

# Single-meaning fixes: char -> preferred keyword
# Pick the most concrete, imageable meaning
SINGLE_MEANING_FIXES = {
    '明': 'bright',
    '天': 'heaven',
    '土': 'earth',
    '力': 'power',
    '方': 'direction',
    '理': 'reason',
    '代': 'generation',
    '意': 'meaning',
    '世': 'generation',
    '前': 'front',
    '先': 'ahead',
    '文': 'writing',
    '出': 'exit',
    '何': 'what',
    '等': 'equal',
    '作': 'make',
    '通': 'pass through',
    '事': 'matter',
    '高': 'tall',
    '髙': 'tall',
    '挙': 'raise',
    '𦦙': 'raise',
    '靔': 'heaven (simp)',
    '於': 'at (trad)',
    '谌': 'Chen (surname) (simp)',
}

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

changes = []

def fix_node(node):
    char = node.get('char', '')
    kw = node.get('keyword', '')
    
    if char and '/' in kw:
        # Skip variant markers like (trad/jp)
        if '(trad/jp)' in kw or '(simp/jp)' in kw:
            return
        
        if char in MULTI_READING_CHARS:
            # Keep slash for multi-reading characters
            return
        
        if char in SINGLE_MEANING_FIXES:
            new_kw = SINGLE_MEANING_FIXES[char]
            changes.append((char, kw, new_kw))
            node['keyword'] = new_kw
        else:
            # Default: take first meaning before slash
            first_meaning = kw.split('/')[0].strip()
            # Preserve any suffix like (trad) or (simp)
            suffix_match = ''
            for suffix in ['(trad)', '(simp)', '(jp)', '(trad/jp)', '(simp/jp)']:
                if suffix in kw:
                    suffix_match = ' ' + suffix
                    break
            new_kw = first_meaning + suffix_match
            if new_kw != kw:
                changes.append((char, kw, new_kw))
                node['keyword'] = new_kw
    
    if 'children' in node:
        for child in node['children']:
            fix_node(child)

fix_node(graph)

print(f'Fixed {len(changes)} slashed keywords:')
for char, old, new in changes:
    print(f'  {char}: "{old}" -> "{new}"')

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print('\nSaved!')

