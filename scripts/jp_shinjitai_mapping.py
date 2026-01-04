#!/usr/bin/env python3
"""
Japanese shinjitai (新字体) to traditional (旧字体) mapping.
These are characters where Japan simplified differently than China.
"""

# Japanese shinjitai -> Traditional form
JP_SHINJITAI = {
    '来': '來', '読': '讀', '国': '國', '売': '賣', '気': '氣',
    '会': '會', '発': '發', '学': '學', '写': '寫', '楽': '樂',
    '実': '實', '単': '單', '変': '變', '応': '應', '当': '當',
    '図': '圖', '画': '畫', '仏': '佛', '体': '體', '広': '廣',
    '礼': '禮', '経': '經', '続': '續', '総': '總', '観': '觀',
    '悪': '惡', '戦': '戰', '乱': '亂', '弁': '辯', '芸': '藝',
    '予': '豫', '余': '餘', '両': '兩', '労': '勞', '営': '營',
    '衛': '衞', '栄': '榮', '帰': '歸', '黒': '黑', '県': '縣',
    '庁': '廳', '聴': '聽', '医': '醫', '旧': '舊', '区': '區',
    '駆': '驅', '撃': '擊', '欠': '缺', '検': '檢', '険': '險',
    '剣': '劍', '権': '權', '献': '獻', '顕': '顯', '験': '驗',
    '効': '效', '号': '號', '済': '濟', '斎': '齋', '歳': '歲',
    '桜': '櫻', '蚕': '蠶', '惨': '慘', '産': '產', '賛': '贊',
    '残': '殘', '糸': '絲', '歯': '齒', '児': '兒', '辞': '辭',
    '湿': '濕', '収': '收', '従': '從', '処': '處', '称': '稱',
    '将': '將', '焼': '燒', '状': '狀', '条': '條', '畳': '疊',
    '嬢': '孃', '穣': '穰', '醸': '釀', '触': '觸', '寝': '寢',
    '枢': '樞', '数': '數', '声': '聲', '斉': '齊', '静': '靜',
    '摂': '攝', '窃': '竊', '専': '專', '浅': '淺', '践': '踐',
    '潜': '潛', '繊': '纖', '禅': '禪', '双': '雙', '壮': '壯',
    '争': '爭', '荘': '莊', '捜': '搜', '挿': '插', '騒': '騷',
    '属': '屬', '対': '對', '滞': '滯', '択': '擇', '沢': '澤',
    '担': '擔', '胆': '膽', '団': '團', '断': '斷', '遅': '遲',
    '痴': '癡', '昼': '晝', '虫': '蟲', '鋳': '鑄', '勅': '敕',
    '逓': '遞', '鉄': '鐵', '伝': '傳', '転': '轉', '灯': '燈',
    '党': '黨', '闘': '鬪', '独': '獨', '徳': '德', '突': '突',
    '縄': '繩', '拝': '拜', '麦': '麥', '抜': '拔', '浜': '濱',
    '払': '拂', '並': '竝', '辺': '邊', '弁': '辨', '宝': '寶',
    '豊': '豐', '翻': '飜', '万': '萬', '満': '滿', '毎': '每',
    '猛': '猛', '薬': '藥', '訳': '譯', '予': '豫', '与': '與',
    '誉': '譽', '様': '樣', '謡': '謠', '揺': '搖', '覧': '覽',
    '竜': '龍', '隆': '隆', '虜': '虜', '涙': '淚', '類': '類',
    '霊': '靈', '暦': '曆', '歴': '歷', '恋': '戀', '炉': '爐',
    '労': '勞', '郎': '郞', '楼': '樓', '禄': '祿', '湾': '灣',
}

if __name__ == '__main__':
    import json
    
    with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
        jlpt = json.load(f)
    with open('web-app/static/game_data/joyo_kanji.json', 'r') as f:
        joyo = json.load(f)
    
    jlpt_joyo = set(jlpt['N5'] + jlpt['N4'] + jlpt['N3'] + jlpt['N2'] + jlpt['N1'] + joyo)
    
    with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
        graph = json.load(f)
    
    chars_in_graph = set()
    def collect(node):
        if 'char' in node:
            chars_in_graph.add(node['char'])
        if 'children' in node:
            for child in node['children']:
                collect(child)
    collect(graph)
    
    # Count
    in_jlpt = sum(1 for k in JP_SHINJITAI if k in jlpt_joyo)
    both_in_graph = [(jp, trad) for jp, trad in JP_SHINJITAI.items() 
                     if jp in chars_in_graph and trad in chars_in_graph]
    
    print(f"Total shinjitai mappings: {len(JP_SHINJITAI)}")
    print(f"In JLPT/Joyo: {in_jlpt}")
    print(f"Both JP and trad in graph: {len(both_in_graph)}")

